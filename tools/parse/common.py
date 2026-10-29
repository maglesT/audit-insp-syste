"""Shared clause model and helpers for the source parsers (deterministic, no AI).

A clause is the smallest citable unit of a source. Every body line of a source ends up in exactly one clause:
numbered clauses get their own reference ("9.3", "211.68(b)"), and text the parser cannot attach to a number
goes into "_unnumbered:<n>" segments, so nothing is silently dropped.
"""
import hashlib
import json
import re
import subprocess
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


def pdf_pages(path):
    """Layout-preserving text, one string per page."""
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
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
    """A line compared across pages: digits masked, spacing collapsed (layout mode varies the gaps)."""
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", line.strip()))


def edge_lines(page, n=3):
    """The first and last few non-empty lines of a page: the only places running headers and footers sit."""
    lines = [ln for ln in page.splitlines() if ln.strip()]
    return lines[:n] + lines[-n:] if len(lines) > 2 * n else lines


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
            if c.page_start in toc_pages or short_entry:
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
