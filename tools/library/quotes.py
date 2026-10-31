"""Quote check (D45): every item's quote, found word for word in two independent readings of its source page.

  python3 tools/library/quotes.py run      # read the sources again, check every mapping, write library/quote-check.json
  python3 tools/library/quotes.py check    # the committed file is current for every mapping (Layer 1 uses it)

The first reading is the stored clause (poppler, `pdftotext`), which Layer 1 check 1 already holds the quote to.
The second is a separate code base: for a PDF, pdfminer.six's words (through pdfplumber) of the clause's pages and
one page either side; for an HTML or XML page, the file's text taken with Python's own html.parser (tags dropped,
entities resolved), not the parser's reader. The quote is found when its letters and digits, in order (case
folded, Unicode NFKC, word breaks and hyphenation ignored; contains() for ligature letters), are a stretch of the second
reading; running headers and footers and small-font footnote marks between them are skipped (a quote may run
over a page break or past a footnote mark). A quote from a table row is checked piece by piece (its " | "
cells), each piece in the text of the pdfminer words inside one of the row's cell boxes (Clause.cells, D44) or in
the page text.

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
LOOSE = re.compile(r"[fil]")


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def code_sha256():
    return sha256(Path(__file__).read_bytes())


def letters(text):
    """Letters and digits only, case folded and NFKC-normalised, so word breaks, hyphenation and punctuation do not
    matter."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "").casefold()
    return "".join(ch for ch in text if ch.isalnum())


def contains(quote, text):
    """quote (letters()) is a stretch of text (letters()); or, as pdfminer drops some ligature letters
    ("qualication"), both are equal without the letters f, i and l (every other letter still in order). A stripped
    ligature cannot be told apart from a word boundary ("staff implement"), hence the letters, not the ligatures,
    are left out."""
    return quote in text or LOOSE.sub("", quote) in LOOSE.sub("", text)


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
        for (toks, small, _, _, _, head), page in zip(read, lines):
            self.pages.append(letters(" ".join(t for k, t in enumerate(toks) if k not in small and k not in head)))
            self.full.append(letters(" ".join(w[0] for ln in page for w in ln)))

    def text(self, first, last, full=False):
        src = self.full if full else self.pages
        return "".join(src[max(first - 2, 0):min(last + 1, len(src))])

    def cell_text(self, boxes):
        out = []
        for page, x0, top, x1, bottom in boxes:
            if 1 <= page <= len(self.words):
                out += [w[0] for w in self.words[page - 1]
                        if x0 <= (w[1] + w[3]) / 2 <= x1 and top <= (w[2] + w[4]) / 2 <= bottom]
        return letters(" ".join(out))


def found(quote, clause, reading):
    """Whether the quote is in the second reading (see the module docstring)."""
    if isinstance(reading, str):                              # an HTML or XML page: its whole text
        return contains(letters(quote), reading)
    first, last = clause["page_start"], clause["page_end"]
    texts = (reading.text(first, last), reading.text(first, last, full=True))
    if clause.get("kind") in ("table_row", "table_header"):
        cells = [reading.cell_text(bs) for bs in clause.get("cells") or []]
        return all(any(contains(letters(piece), t) for t in cells + list(texts))
                   for piece in quote.split(" | ") if letters(piece))
    return any(contains(letters(quote), t) for t in texts)


def run(root=model.LIBRARY):
    import layer1
    reqs = [r for r in model.requirements(root) if r["status"] != "retired"]
    readings, entries = {}, {}
    for req in reqs:
        for n, m in enumerate(req["mappings"], start=1):
            source = m["source"]
            path = OFFICIAL / source
            if source not in readings:
                readings[source] = PdfReading(path) if source.endswith(".pdf") else letters(html_text(path))
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
