"""Shared clause model and helpers for the source parsers (deterministic, no AI).

A clause is the smallest citable unit of a source. Every body line of a source ends up in exactly one clause:
numbered clauses get their own reference ("9.3", "211.68(b)"), and text the parser cannot attach to a number
goes into "_unnumbered:<n>" segments, so nothing is silently dropped.
"""
import hashlib
import json
import re
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / "sources" / "official"
CLAUSES = ROOT / "library" / "clauses"

CITABLE = ("clause", "principle", "section", "table_row", "table_header")   # kinds with a reference of their own
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


@dataclass
class Clause:
    source: str            # file name in sources/official
    ref: str               # e.g. "Part I 10.5", "211.68(b)", "Principle", "_unnumbered:3"
    section: str           # section prefix that resets numbering ("Annex 1", "Part II"); "" if none
    number: str            # the bare number ("10.5"); "" for headings and unnumbered segments
    heading: str           # first line, trimmed (for humans and drafting context)
    text: str              # whitespace-normalised text of the whole clause
    page_start: int
    page_end: int
    kind: str = "clause"   # clause | principle | section | unnumbered | toc | table_row | table_header
    notes: list = field(default_factory=list)
    parent: str = ""       # table rows: the clause the table sits in ("" when it sits before any clause)

    def to_json(self):
        d = asdict(self)
        d["sha256"] = hashlib.sha256(self.text.encode("utf-8")).hexdigest()
        return d


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


# a clause's own number at its start ("9.3", "10.1.", "(b)", "Principle"): left out when twins are compared
TWIN_LEADING = re.compile(r"^\s*(?:[A-Z]?\d+(?:\.\d+)*\.?|\([a-zA-Z0-9]+\)|principle)\s*", re.I)


def twin_key(text):
    """The words of a clause, lowercased, without its leading number and without punctuation: two clauses of
    different sources with the same key are twins (D36, D37; Layer 1 check 8 and topic.py use this one key)."""
    return " ".join(re.findall(r"\w+", TWIN_LEADING.sub("", normalise(text)).lower()))


GLYPH_SPACE = "\x01"
GLYPH_EXTRA = {"m": "fi", "t": "•", "õ": "ff"}     # glyphs 109, 116, 245 of the same glyph order
GLYPH_TOKEN = re.compile(r"[^ \t\n\r\f\v]*\x01[^ \t\n\r\f\v]*")


def _unshift_part(part):
    if not part or not all("\x02" <= c <= "\x5f" or c in GLYPH_EXTRA for c in part):
        return part
    return "".join(GLYPH_EXTRA.get(c) or chr(ord(c) + 31) for c in part)


def unshift_glyphs(text):
    """Text of fonts without a Unicode map, which poppler prints as raw glyph numbers (WHO TRS 981 Annex 2's QRM
    tables: "UFDIOJRVF\\x01UP" for "technique to"). The font's glyphs are in the standard order of Adobe's Pro
    fonts, glyph n = character n + 31 (glyph 1 is the space, which poppler prints as \\x01; 109 "fi", 116 a bullet,
    245 "ff"). Only words that hold the \\x01 space glyph are read this way, part by part between the spaces, and
    a part is converted only when every character is a raw glyph number of that range; a part in ordinary letters
    ("t\\x01Tool": bullet, then "Tool") stays. A word made of \\x01 alone (a bullet in some PIC/S fonts) stays."""
    def one(m):
        token = m.group(0)
        if not token.strip(GLYPH_SPACE):
            return token
        return " ".join(_unshift_part(p) for p in token.split(GLYPH_SPACE)).rstrip()
    return GLYPH_TOKEN.sub(one, text)


def turned_pages(path):
    """{page number: degrees} for pages whose text is set turned on an unrotated page (a landscape table printed
    on a portrait page, WHO TRS 1010 Annex 8 Table A8.1): most characters run at 90 or 270 degrees once the
    page's own rotation is applied. The degrees are the rotation that sets the text upright."""
    import math
    import pypdfium2 as pdfium
    import pypdfium2.raw as raw
    out = {}
    pdf = pdfium.PdfDocument(str(path))
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            textpage = page.get_textpage()
            angles = [raw.FPDFText_GetCharAngle(textpage.raw, k) for k in range(textpage.count_chars())]
            degrees = [(round(math.degrees(a)) + page.get_rotation()) % 360 for a in angles if a >= 0]
            turned = Counter(d for d in degrees if d in (89, 90, 91, 269, 270, 271))
            if degrees and sum(turned.values()) > len(degrees) / 2:
                main = turned.most_common(1)[0][0]
                out[i + 1] = (page.get_rotation() + (90 if main >= 269 else 270)) % 360
    finally:
        pdf.close()
    return out


def upright_copy(path, folder):
    """The PDF itself, or, when it has turned pages (turned_pages), a copy in folder (same file name) with those
    pages rotated so their text is upright: poppler reads turned text backwards ("elbat" for "table"), so the
    parsers read the copy. Page numbers and text are unchanged; the fidelity check reads the original."""
    turned = turned_pages(path)
    if not turned:
        return Path(path)
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(path))
    try:
        for pno, degrees in turned.items():
            pdf[pno - 1].set_rotation(degrees)
        out = Path(folder) / Path(path).name
        pdf.save(str(out))
    finally:
        pdf.close()
    return out


def pdf_pages(path):
    """Layout-preserving text, one string per page."""
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
    out = unshift_glyphs(out)
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages


def devanagari_share(text):
    letters = [c for c in text if c.isalpha()]
    return sum(1 for c in letters if DEVANAGARI.match(c)) / len(letters) if letters else 0.0


def english_page(page):
    """Mostly English. Gazette notices mix a Hindi preamble and the English rule text on one page; such a page is
    kept, and its Hindi lines are dropped one by one (english_line)."""
    return devanagari_share(page) < 0.5


def english_line(line):
    return devanagari_share(line) < 0.3


def line_key(line):
    """A line compared across pages: digits masked, spacing collapsed (layout mode varies the gaps), no spaces
    around dashes (the PIC/S footer prints "-6-" on one page and "- 10 -" on the next), lower-case roman page
    numbers masked like digits ("-ii-")."""
    masked = re.sub(r"(?<![^\W\d_])[ivxl]{1,6}(?![^\W\d_])", "#", re.sub(r"\d+", "#", line.strip()))
    return re.sub(r"\s*([-–—])\s*", r"\1", re.sub(r"\s+", " ", masked))


def edge_lines(page, n=3):
    """The first and last few non-empty lines of a page: the only places running headers and footers sit."""
    lines = [ln for ln in page.splitlines() if ln.strip()]
    return lines[:n] + lines[-n:] if len(lines) > 2 * n else lines


BLOCK = 6           # lines from a page edge that may belong to one running header or footer block
BLOCK_SHARE = 0.6   # share of the pages a line beyond the edge lines must recur on to extend a block


def edge_block(page, noise, n=3):
    """The page's edge lines (edge_lines) plus the lines that continue a run of repeated lines inward from the top
    or the bottom: a running footer of four lines (the EMA nitrosamine Q&A's title, two lines more and
    "EMA/409815/2020 Page 5/27") is one block. noise is repeated_lines(pages, min_share=BLOCK_SHARE, n=BLOCK):
    stricter than the edge rule, so a heading that often sits near a page edge ("References", "Supplement 2" in
    WHO TRS 992 Annex 5) is not taken for part of a block."""
    lines = [ln for ln in page.splitlines() if ln.strip()]
    out = set(ln.strip() for ln in edge_lines(page, n))
    for seq in (lines[:BLOCK], lines[::-1][:BLOCK]):
        run = 0
        while run < len(seq) and line_key(seq[run]) in noise:
            run += 1
        if run >= n:
            out |= {ln.strip() for ln in seq[:run]}
    return out


def repeated_lines(pages, min_share=0.3, min_pages=3, n=3):
    """Lines that recur on many pages (running headers and footers), compared with digits masked."""
    counts = {}
    for page in pages:
        seen = set()
        for line in edge_lines(page, n):
            key = line_key(line)
            if key and key not in seen:
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
    limit = max(min_pages, int(len(pages) * min_share))
    return {k for k, n in counts.items() if n >= limit}


SIDE_HEADER = re.compile(r"^WHO Technical Report Series,? No\. #, #$")


def running_lines(pages, min_share=0.3, min_pages=3):
    """Known running lines that recur on many pages anywhere on the page, compared with digits masked.

    WHO TRS volumes print the series name ("WHO Technical Report Series, No. 1044, 2022") rotated in the margin;
    layout mode puts it mid-page, between body lines, where the edge rule misses it. Only lines matching
    SIDE_HEADER count: a general "repeated anywhere" rule would also drop body lines that repeat, such as list
    items in the PIC/S aide-memoires.
    """
    counts = {}
    for page in pages:
        for key in {line_key(ln) for ln in page.splitlines()}:
            if SIDE_HEADER.match(key):
                counts[key] = counts.get(key, 0) + 1
    limit = max(min_pages, int(len(pages) * min_share))
    return {k for k, n in counts.items() if n >= limit}


CONTENTS_ENTRY = re.compile(r"(\.\s?){4,}\s*\d*\s*$|\s\d{1,3}$")
CONTENTS_ENTRY_MAX = 150


def contents_pages(clauses):
    """Pages that hold a contents list: in the first third of the document, at least 4 numbered clauses start
    there and at least 70 % of them are short (a contents entry, not a paragraph)."""
    last = max((c.page_end for c in clauses), default=0)
    starts = {}
    for c in clauses:
        if c.kind in ("clause", "principle"):
            starts.setdefault(c.page_start, []).append(len(c.text) <= CONTENTS_ENTRY_MAX)
    return {p for p, short in starts.items()
            if p <= max(3, last / 3) and len(short) >= 4 and sum(short) >= 0.7 * len(short)}


def resolve_duplicates(clauses):
    """Make references unique, without dropping anything.

    - A copy that is a contents entry becomes kind "toc": it sits on a contents page (contents_pages) or is short
      and ends in dot leaders or a page number, and a later copy of the same reference exists.
    - Numbering that genuinely starts again (an annex or appendix whose heading the parser does not know) keeps its
      text; the later copies get "#2", "#3" and a note naming the heading the restart follows.
    """
    toc_pages = contents_pages(clauses)
    groups = {}
    for i, c in enumerate(clauses):
        if c.kind in ("clause", "principle", "section"):
            groups.setdefault(c.ref, []).append(i)
    for ref, idx in groups.items():
        if len(idx) < 2:
            continue
        for i in idx[:-1]:
            c = clauses[i]
            short_entry = len(c.text) <= CONTENTS_ENTRY_MAX and CONTENTS_ENTRY.search(c.text)
            on_contents_page = c.page_start in toc_pages and len(c.text) <= CONTENTS_ENTRY_MAX
            early_heading = c.kind == "section" and len(c.text) <= CONTENTS_ENTRY_MAX
            if on_contents_page or short_entry or early_heading:
                c.kind, c.ref = "toc", f"_toc:{c.ref}"
        rest = [i for i in idx if clauses[i].kind != "toc"]
        for n, i in enumerate(rest[1:], start=2):
            context = next((clauses[j].heading[:60] for j in range(i - 1, -1, -1)
                            if clauses[j].kind == "unnumbered"), clauses[i - 1].heading[:60] if i else "")
            clauses[i].ref = f"{ref} #{n}"
            clauses[i].notes.append(f"restart: numbering starts again after '{context}'")
    return clauses


def write_clauses(source, clauses):
    CLAUSES.mkdir(parents=True, exist_ok=True)
    path = CLAUSES / (Path(source).stem + ".jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for c in clauses:
            f.write(json.dumps(c.to_json(), ensure_ascii=False) + "\n")
    return path


def report(source, clauses, body_chars, dropped_chars=0):
    """Completeness figures for one source."""
    assigned = sum(len(c.text.replace(" ", "").replace("|", "")) for c in clauses)
    numbered = sum(len(c.text.replace(" ", "").replace("|", "")) for c in clauses if c.kind in CITABLE)
    refs = [c.ref for c in clauses if c.kind in CITABLE]
    dups = sorted({r for r in refs if refs.count(r) > 1})
    return {
        "source": source,
        "clauses": len(refs),
        "table_rows": sum(1 for c in clauses if c.kind == "table_row"),
        "unnumbered_segments": sum(1 for c in clauses if c.kind == "unnumbered"),
        "toc_segments": sum(1 for c in clauses if c.kind == "toc"),
        "body_chars": body_chars,
        "dropped_chars": dropped_chars,
        "assigned_share": round(assigned / body_chars, 4) if body_chars else 1.0,
        "numbered_share": round(numbered / body_chars, 4) if body_chars else 1.0,
        "duplicate_refs": dups,
        "gaps": [n for c in clauses for n in c.notes if n.startswith("gap")],
    }
