"""Quote check (D45): every item's quote, found word for word in two independent readings of its source page.

  python3 tools/library/quotes.py run      # read the sources again, check every mapping, write library/quote-check.json
  python3 tools/library/quotes.py check    # the committed file is current for every mapping (Layer 1 uses it)

The first reading is the stored clause (poppler, `pdftotext`), which Layer 1 check 1 already holds the quote to.
The second is a separate code base: for a PDF, pdfminer.six's words (through pdfplumber) of the clause's pages and
one page either side; for an HTML or XML page, the file's text taken with Python's own html.parser (tags dropped,
entities resolved), not the parser's reader. The quote is found when its letters and digits, in order (case
folded, Unicode NFKC, whole tokens in order; see toks() and contains()), are a stretch of the second
reading; running headers and footers (drop_running) and small-font footnote marks between them are skipped (a quote may run
over a page break or past a footnote mark). A quote from a table row is checked cell by cell (its " | " pieces),
each piece equal (token for token) to the pdfminer words inside the row's cell boxes (Clause.cells, D44), from
the row's first cell on, consecutive; without cell boxes a table quote is not found.

Each entry records the sha256 of the quote, of the source file and of this code; `check` (and Layer 1) treat an
entry as missing when any of them changed. This file never runs in CI: CI reads the result.
"""
import hashlib
import html.parser
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "parse"))
import model  # noqa: E402
from common import OFFICIAL  # noqa: E402

RESULT = model.ROOT / "library" / "quote-check.json"


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def code_sha256():
    return sha256(Path(__file__).read_bytes())


TOKEN = re.compile(r"\d+(?:[.,]\d+)*|[^\W\d_]+|[<>≤≥±%^−]|(?:(?<=\^)|(?<![\w.]))[-–](?=\s?\d)")
LIGATURE = re.compile(r"ff[il]?|f[il]")


def toks(text):
    """Comparable tokens: words, numbers with their decimal point or comma ("1.5", "3,520"), and the signs
    < > ≤ ≥ ± % ^ and a minus (−, or - and – before a number not after a word: "-20 °C", "10^-6"); case folded, NFKC, soft hyphens dropped. Punctuation and
    spacing do not count, and a footnote mark written "^1" right after a word counts as "1" (D46: the drafters quote
footnote marks so; the readings print them flat), but every token must match whole: "15" is not "1.5", "inappropriate" is not
    "appropriate"."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "").casefold().replace("-", "-")
    text = re.sub(r"(?:(?<=[^\W\d_])|(?<=\)))\^(?=\d)", " ", text)     # a footnote mark after a word, "Cumene^1": the
    return [("−" if t in "-–" else t) for t in TOKEN.findall(text)]   # readings print it flat ("Cumene1")


def letters(text):
    """The tokens of a text (kept under its old name for callers): see toks()."""
    return toks(text)


def _same(q, p, loose):
    return q == p or (loose and q.isalpha() and LIGATURE.sub("", q) == p and q != p)


def contains(quote, text, loose=False):
    """The quote's tokens are a run of the text's tokens, whole tokens, in order. Allowed between them: a word
    split in two by a line-end hyphen ("speci", "fied" for "specified") or two words read as one, with exactly
    the same letters. loose (pdfminer only): a word may lack its ligature letters ("qualication"), as pdfminer
    sometimes drops them; nothing else is loosened."""
    if not quote:
        return True
    n = len(text)
    for start in range(n):
        i, j = 0, start
        while i < len(quote) and j < n:
            q, p = quote[i], text[j]
            if _same(q, p, loose):
                i, j = i + 1, j + 1
            elif j + 1 < n and q.isalpha() and p.isalpha() and text[j + 1].isalpha() and q == p + text[j + 1]:
                i, j = i + 1, j + 2                                  # split by a line-end hyphen
            elif i + 1 < len(quote) and p.isalpha() and q + quote[i + 1] == p:
                i, j = i + 2, j + 1                                  # two words read as one
            else:
                break
        if i == len(quote):
            return True
    return False


EDGE = 3       # lines at the top and the bottom of a page where running headers and footers stand


def line_key(line):
    """A line's key for running-line matching: digits masked only for a page-number line ("- 6 -", "Page 6 of 9")
    or a footer of 4 or more words ("PE 009-18 (Annexes) -15- 24 September 2026"); a short body line such as
    "6 months." must repeat exactly ("12 months." is another line)."""
    line = re.sub(r"\s+", " ", line).strip().lower()
    words = re.findall(r"[^\W\d_]+", line)
    if len(line.split()) >= 4 or not [w for w in words if w not in ("page", "of")]:
        return re.sub(r"\d+", "#", line)
    return line


def drop_running(pages):
    """Pages (lists of non-empty lines) without their running lines: among a page's first and last EDGE lines,
    those whose line_key is also among the first or last EDGE lines of the page before or after."""
    def edge(lines):
        n = len(lines)
        return set(range(min(EDGE, n))) | set(range(max(n - EDGE, 0), n))
    keys = [{line_key(pg[k]) for k in edge(pg)} for pg in pages]
    out = []
    for i, pg in enumerate(pages):
        near = (keys[i - 1] if i > 0 else set()) | (keys[i + 1] if i + 1 < len(pages) else set())
        out.append([ln for k, ln in enumerate(pg) if not (k in edge(pg) and line_key(ln) in near)])
    return out


def mapping_key(req_id, n):
    return f"{req_id}#{n}"


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style") and self.skip > 0

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(path):
    p = _Text()
    p.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    return " ".join(p.parts)


class PdfReading:
    """pdfminer's reading of one PDF: per page the letters of the body text (running headers and footers and
    small-font marks left out) and of the full text, and the words with their boxes for table cells."""

    def __init__(self, path):
        import fidelity
        import pdfplumber
        self.pages, self.full, self.words = [], [], []
        with pdfplumber.open(str(path)) as pdf:
            lines = []
            for page in pdf.pages:
                lines.append(fidelity.page_lines(page))
                ws = page.extract_words(keep_blank_chars=False, use_text_flow=True)
                self.words.append([(fidelity.cid_text(w["text"]), w["x0"], w["top"], w["x1"], w["bottom"])
                                   for w in ws])
        read, _ = fidelity.read_pages(lines)
        plain = [[" ".join(w[0] for w in ln) for ln in page] for page in lines]
        self.body = [toks(" ".join(pg)) for pg in drop_running(plain)]
        for (page_toks, small, _, _, _, head), page in zip(read, lines):
            self.pages.append(toks(" ".join(t for k, t in enumerate(page_toks) if k not in small and k not in head)))
            self.full.append(letters(" ".join(w[0] for ln in page for w in ln)))

    def text(self, first, last, full=False, body=False):
        src = self.body if body else self.full if full else self.pages
        return [t for page in src[max(first - 2, 0):min(last + 1, len(src))] for t in page]

    def cell_text(self, boxes):
        out = []
        for page, x0, top, x1, bottom in boxes:
            if 1 <= page <= len(self.words):
                out += [w[0] for w in self.words[page - 1]
                        if x0 <= (w[1] + w[3]) / 2 <= x1 and top <= (w[2] + w[4]) / 2 <= bottom]
        return letters(" ".join(out))


def found(quote, clause, reading):
    """Whether the quote is in the second reading (see the module docstring)."""
    if not isinstance(reading, PdfReading):                   # an HTML or XML page: its whole text
        return contains(toks(quote), reading)
    first, last = clause["page_start"], clause["page_end"]
    texts = (reading.text(first, last), reading.text(first, last, full=True), reading.text(first, last, body=True))
    if " | " in quote:                                        # a table row: its cells, whole and in order, are
        cells = [reading.cell_text(bs) for bs in clause.get("cells") or []]   # the row's cells from the first one
        pieces = [toks(x) for x in quote.split(" | ")]
        return len(cells) >= len(pieces) and all(c == p for c, p in zip(cells, pieces))
    return any(contains(toks(quote), t, loose=True) for t in texts)


def run(root=model.LIBRARY):
    import layer1
    reqs = [r for r in model.requirements(root) if r["status"] != "retired"]
    readings, entries = {}, {}
    for req in reqs:
        for n, m in enumerate(req["mappings"], start=1):
            source = m["source"]
            path = OFFICIAL / source
            if source not in readings:
                readings[source] = PdfReading(path) if source.endswith(".pdf") else toks(html_text(path))
                print(source, flush=True)
            clause = layer1.segments_of(source)
            clause = next((c for c in clause if c["ref"] == m["clause_ref"]), None)
            entries[mapping_key(req["id"], n)] = {
                "source": source, "clause_ref": m["clause_ref"], "quote_sha256": sha256(m["quote"]),
                "source_sha256": sha256(path.read_bytes()),
                "reader": "pdfminer" if source.endswith(".pdf") else "html.parser",
                "found": bool(clause) and found(m["quote"], clause, readings[source])}
    doc = {"code_sha256": code_sha256(), "mappings": dict(sorted(entries.items()))}
    RESULT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    bad = [k for k, e in entries.items() if not e["found"]]
    print(f"{len(entries)} quotes, {len(bad)} not found in the second reading")
    return doc


def findings(reqs, result=RESULT, source_hashes=None):
    """Layer 1 findings (req id, mapping number, "quote2", message) from the committed result: a mapping with no
    current entry (quote, source or code changed) or whose quote the second reading lacks."""
    doc = json.loads(Path(result).read_text(encoding="utf-8")) if Path(result).exists() else {"mappings": {}}
    current = doc.get("code_sha256") == code_sha256()
    hashes = source_hashes if source_hashes is not None else {}
    out = []
    for req in reqs:
        if req["status"] == "retired":
            continue
        for n, m in enumerate(req["mappings"], start=1):
            e = doc["mappings"].get(mapping_key(req["id"], n))
            if source_hashes is None and m["source"] not in hashes:
                hashes[m["source"]] = sha256((OFFICIAL / m["source"]).read_bytes())
            if (not current or e is None or e["quote_sha256"] != sha256(m["quote"])
                    or e["source"] != m["source"] or e["source_sha256"] != hashes.get(m["source"])):
                out.append((req["id"], n, "quote2", "no current second-reading check: run tools/library/quotes.py run"))
            elif not e["found"]:
                out.append((req["id"], n, "quote2", f"quote not found word for word in the second reading "
                                                    f"({e['reader']}) of {m['clause_ref']}"))
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "run":
        run()
    elif cmd == "check":
        out = findings(model.requirements(model.LIBRARY))
        for f in out:
            print(f"{f[0]} mapping {f[1]} [{f[2]}] {f[3]}")
        print(f"{len(out)} quote findings")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
