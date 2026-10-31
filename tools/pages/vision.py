"""Page-based drafting with vision (D45): checklist items drafted from PDF pages, checked on page text.

  python3 tools/pages/vision.py prepare-draft [SOURCE:PAGE ...]   # default: the trial pages (TRIAL)
  python3 tools/pages/vision.py ingest-draft RUN                  # checks + measures -> RUN/items.jsonl, report.json
  python3 tools/pages/vision.py prepare-verify RUN [SOURCE ...]   # verifier A and B batches, one per document
  python3 tools/pages/vision.py ingest-verify RUN                 # verifier agreement -> RUN/verify-report.json
  python3 tools/pages/vision.py record-model RUN ROLE MODEL       # which model answered drafting / verify_a / verify_b

Each page is rendered to PNG at DPI with pypdfium2 (pinned in requirements.txt; image sha256 recorded) and its text
layer taken with `pdftotext -layout`. A drafting agent gets, per page, the image path, the text layer, and the next
page's text when a sentence runs over the break; it writes the items it sees (batch file -> answers file, as in
tools/ai/sessions.py). Nothing here depends on the parsed clause store (frozen, D45).

Checks on each item (deterministic, no AI):
  quote      found token for token (quotes.toks / quotes.contains: whole tokens in order, so "15" is not "1.5")
             on its page, or page + next when the item says it runs over, in BOTH readings, pdftotext -layout and
             pdfminer, each also without the page's running lines (body(): edge lines repeated on a neighbouring
             page). A table row (cells joined with " | ") must be consecutive cells of ONE row of a ruled table,
             each cell whole, read by pdfminer and by poppler inside the same cell boxes; an unruled row must stand
             on one line. A quote found in one reading only, or in neither, goes to the "text layer differs" list
             (the image-true reading is kept for the verifiers and the spot check; never accepted silently).
  clause     the clause number as printed (clause_findings): its main number starts a line on the page, its first
             sub-part too ("4.22 iii"); a cross-reference inside a sentence or a page-number line does not count
  numbers    every number of the statement is in its quote, and every number of the quote in its statement
             (layer1.number_found, word forms count)
  strength   the item's strength matches its quote's wording where the quote has one (layer1.strength_of)
  conditions condition wording in the quote has a counterpart in the statement (layer1.conditions_missing)
  lead-in    a table row or list item states the scoping condition (if / where / when, unless, only) of the lead-in
             that governs it (lead_in, D46): for a table row, an obligation sentence pointing to the row's table
             ("Table n", from the page's caption, table_number)
  strength   for an inspection checklist (layer1.INSPECTION_CHECKLISTS) a row without a modal verb is mandatory
Coverage per page: every obligation sentence of the page's text layer (without running lines; obligations.py;
not a descriptive "may" nor a table caption, counts_for_coverage; a leading clause number and a glued WHO side
title left out) has
at least COVERED_SHARE of its words, and all its condition wording, in one item quote of that page or a carry-over
quote of the page before, or in the quotes printed inside it taken together (a sentence with two obligations, or
a lead-in with its list, drafted item by item), or is listed by the drafter as not applicable.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "library"))
sys.path.insert(0, str(ROOT / "tools" / "parse"))
sys.path.insert(0, str(ROOT / "tools" / "ai"))
import obligations  # noqa: E402
import quotes  # noqa: E402
from common import OFFICIAL  # noqa: E402

DPI = 150
RUNS = ROOT / "library" / "ai-runs"
IMAGES = ROOT / "work" / "vision-pages"            # rendered pages (not in git; sha256 in the run's pages.json)
PROMPTS = HERE / "prompts"
COVERED_SHARE = 0.8
UNION_SHARE = 0.9          # a sentence covered by several quotes printed inside it: a stricter share, every number
PAGES_PER_BATCH = 5
STRENGTHS = ("mandatory", "recommended", "optional")
PLANTS = ("OSD", "LIQ", "SEMI", "INJ", "API")

# The D45 trial: 5 pages from each of the 10 hardest documents. Known hard pages (tables, landscape pages,
# superscripts, pages of former parser defects) plus ordinary body pages of the same document.
TRIAL = {
    "eu-20220825_gmp-an1_en_0.pdf": [12, 13, 14, 22, 45],
    "pics-pe009-18-annexes.pdf": [18, 19, 20, 21, 22],
    "who-trs1044-a2-sterile.pdf": [17, 18, 19, 20, 52],
    "who-trs1010-a8-hvac-nonsterile.pdf": [8, 9, 15, 16, 17],
    "ich-q3c-r9.pdf": [8, 11, 12, 13, 17],
    "india-cdsco-circ-2024-03-risk-based-inspection.pdf": [16, 17, 45, 48, 116],
    "fda-cp-7356-002-drug-manufacturing-inspections.pdf": [10, 11, 20, 21, 41],
    "fda-guidance-nitrosamine-control-2024.pdf": [10, 11, 12, 20, 41],
    "india-schedule-m-2023-GSR922E.pdf": [155, 156, 157, 163, 271],    # English half starts at p149
    "pics-pi011-3-computerised-systems.pdf": [8, 9, 10, 20, 21],
}

DRAFT_SCHEMA = {
    "type": "object", "required": ["page", "items", "not_applicable"],
    "properties": {
        "page": {"type": "string"},
        "items": {"type": "array", "items": {
            "type": "object",
            "required": ["statement", "quote", "clause_number", "strength", "plant_types", "numbers", "condition",
                         "topic", "runs_over", "text_layer_differs"],
            "properties": {
                "statement": {"type": "string"}, "quote": {"type": "string"},
                "clause_number": {"type": "string"},
                "strength": {"enum": list(STRENGTHS)},
                "plant_types": {"type": "array", "items": {"enum": list(PLANTS)}},
                "numbers": {"type": "array", "items": {"type": "string"}},
                "condition": {"type": "string"}, "topic": {"type": "string"},
                "runs_over": {"type": "boolean"}, "text_layer_differs": {"type": "string"},
                "header_page": {"type": "integer"}}}},
        "not_applicable": {"type": "array", "items": {
            "type": "object", "required": ["text", "reason"],
            "properties": {"text": {"type": "string"}, "reason": {"type": "string"}}}}}}

VERIFY_SCHEMA = {
    "type": "object", "required": ["id", "verdict", "quote_as_printed", "reason"],
    "properties": {"id": {"type": "string"}, "verdict": {"enum": ["correct", "incorrect"]},
                   "quote_as_printed": {"type": "boolean"}, "reason": {"type": "string"}}}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(source, pno):
    """The page as PNG at DPI (path, sha256); rendered once into IMAGES."""
    import pypdfium2 as pdfium
    out = IMAGES / f"{Path(source).stem}-p{pno:03d}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        doc = pdfium.PdfDocument(str(OFFICIAL / source))
        try:
            doc[pno - 1].render(scale=DPI / 72).to_pil().convert("RGB").save(out, optimize=True)
        finally:
            doc.close()
    return out, sha256(out)


def layer_text(source, pno):
    """pdftotext -layout of one page ("" past the last page)."""
    r = subprocess.run(["pdftotext", "-layout", "-f", str(pno), "-l", str(pno), str(OFFICIAL / source), "-"],
                       capture_output=True, text=True)
    return r.stdout.replace("\f", "") if r.returncode == 0 else ""


def pdfminer_text(source, pno, cache={}):
    """pdfminer's text of one page (pdfplumber), the independent second reading."""
    key = (source, pno)
    if key not in cache:
        import pdfplumber
        with pdfplumber.open(str(OFFICIAL / source)) as pdf:
            cache[key] = (pdf.pages[pno - 1].extract_text() or "") if pno <= len(pdf.pages) else ""
    return cache[key]


def page_count(source):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(OFFICIAL / source))
    try:
        return len(doc)
    finally:
        doc.close()


def topics():
    t = json.loads((ROOT / "library" / "topics.json").read_text())["topics"]
    return [s for x in t for s in x["sub"]]


def scope(source):
    import csv
    with open(ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        row = next(r for r in csv.DictReader(f) if r["file"] == source)
    return list(PLANTS) if row["applies_to"].strip() == "ALL" else row["applies_to"].split(";")


def new_run(stage):
    run = RUNS / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')}-{stage}"
    (run / "batches").mkdir(parents=True)
    (run / "answers").mkdir()
    return run


def continues_table(source, pno):
    """A table may continue onto this page from the page before: that page has a table caption and this page has
    no caption before its first line with a number."""
    if pno < 2 or not CAPTION.search(layer_text(source, pno - 1)):
        return False
    for ln in layer_text(source, pno).splitlines():
        if CAPTION.match(ln):
            return False
        if re.search(r"\d", ln):
            return True
    return False


def prepare_draft(targets):
    run = new_run("vision-draft")
    pages, batch, n = [], [], 0
    instructions = (PROMPTS / "draft.md").read_text()
    for source, pno in targets:
        image, digest = render(source, pno)
        entry = {"id": f"{source}:{pno}", "source": source, "page": pno, "image": str(image.relative_to(ROOT)),
                 "image_sha256": digest, "dpi": DPI, "pdf_sha256": sha256(OFFICIAL / source),
                 "text_layer": layer_text(source, pno), "next_page_text": layer_text(source, pno + 1),
                 "previous_page_text": layer_text(source, pno - 1) if continues_table(source, pno) else "",
                 "plant_scope": scope(source)}
        pages.append({k: v for k, v in entry.items() if k not in ("text_layer", "next_page_text",
                                                                  "previous_page_text")})
        batch.append(entry)
        last = (source, pno) == targets[-1]
        if len(batch) == PAGES_PER_BATCH or last or targets[targets.index((source, pno)) + 1][0] != source:
            n += 1
            (run / "batches" / f"batch_{n:03d}.json").write_text(json.dumps(
                {"instructions": instructions, "topics": topics(), "schema": DRAFT_SCHEMA, "pages": batch},
                indent=1, ensure_ascii=False))
            batch = []
    import pypdfium2
    (run / "pages.json").write_text(json.dumps({"renderer": f"pypdfium2 {pypdfium2.version.PYPDFIUM_INFO}", "dpi": DPI,
                                                "pages": pages}, indent=1))
    print(run, n, "batches")
    return run


def _words(text):
    return re.findall(r"\w+", text.lower())


def body(reader, source, pno):
    """A page's text without its running lines (quotes.drop_running over the page and its neighbours)."""
    pages = [[ln for ln in (reader(source, p).splitlines() if p >= 1 else []) if ln.strip()]
             for p in (pno - 1, pno, pno + 1)]
    return "\n".join(quotes.drop_running(pages)[1])


def readings(reader, source, span):
    """The tokens of the pages in span as one reader gives them: whole, and without running lines."""
    return [quotes.toks(" ".join(reader(source, p) for p in span)),
            quotes.toks(" ".join(body(reader, source, p) for p in span))]


def table_rows(source, pno, grouped=False, cache={}):
    """The rows of the ruled tables pdfplumber finds on a page: per row a list of (pdfminer cell text, cell box)
    for its non-empty cells, in order; grouped: a list of tables, each a list of rows."""
    key = (source, pno)
    if key not in cache:
        import pdfplumber
        tables = []
        with pdfplumber.open(str(OFFICIAL / source)) as pdf:
            if pno <= len(pdf.pages):
                page = pdf.pages[pno - 1]
                for t in page.find_tables():
                    rows = []
                    for r in t.rows:
                        cells = [(page.crop(b).extract_text() or "", b) for b in r.cells if b]
                        rows.append([(x, b) for x, b in cells if x.strip()])
                    tables.append(rows)
        cache[key] = tables
    return cache[key] if grouped else [r for t in cache[key] for r in t]


def poppler_words(source, pno, cache={}):
    """poppler's words of a page with their boxes (pdftotext -bbox), the first reading inside table cells."""
    import html
    key = (source, pno)
    if key not in cache:
        out = subprocess.run(["pdftotext", "-bbox", "-f", str(pno), "-l", str(pno), str(OFFICIAL / source), "-"],
                             capture_output=True, text=True).stdout
        cache[key] = [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in re.findall(
            r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', out)]
    return cache[key]


def _in_box(w, b):
    return b[0] <= (w[0] + w[2]) / 2 <= b[2] and b[1] <= (w[1] + w[3]) / 2 <= b[3]


def table_quote_found(quote, source, pno, header_page=0):
    """(in pdftotext, in pdfminer) for a table quote: "header cells || row cells" (D46: a row quote carries its
    column headers) or "row cells". The row part must be a WHOLE row (every non-empty cell, from its label). The
    header part must be the table's whole header: the cells of every row above the first full-width row (as
    many non-empty cells as the quoted row), in order: a two-row header is quoted as both rows ("Grade | ≥ 0.5 µm
    | ≥ 5 µm | at rest | in operation | at rest | in operation"). An unruled
    table: the header line and the row line are whole lines of the page, the header line first."""
    head, _, row = quote.rpartition(" || ")
    pieces = [quotes.toks(x) for x in row.split(" | ")]
    if not head:
        return row_found(pieces, source, pno)
    header = _marks_out(head.replace(" | ", " "))
    if header_page and header_page != pno:                     # a table continued from an earlier page (D46+)
        return _continued(header, pieces, source, pno, header_page)
    if not table_rows(source, pno):
        return tuple(_unruled_header(header, [t for p in pieces for t in p], reader, source, pno, loose, pieces)
                     for reader, loose in ((layer_text, False), (pdfminer_text, True)))
    out = [False, False]
    for t in table_groups(source, pno):
        k = header_rows(t, header, len(pieces))
        if k:
            cells = [c for r in t[:k] for c in r]
            words = poppler_words(source, pno)
            head_layer = _marks_out(" ".join(" ".join(w[4] for w in words if _in_box(w, b)) for _, b in cells))
            for r in t[k:]:
                layer, miner = _row_match(r, pieces, source, pno)
                out = [out[0] or (layer and head_layer == header), out[1] or miner]
    return tuple(out)


MARK = re.compile(r"\(\s*[a-z]\s*\)|\^[a-z]\b")


def _marks_out(text):
    """Header tokens without footnote marks written "(a)" or "^a" ("at rest (a)"): one reader may not see a small
    mark inside a header cell, and a header mark carries no value. Other single letters ("Grade A | B") stay.
    Data cells are compared with their marks."""
    return quotes.toks(MARK.sub(" ", text))


def header_rows(table, header, width):
    """How many rows (1-3) at the top of a ruled table make its whole header: their cells read in order equal the
    quoted header, and the next row is a full-width data row (as many cells as the quoted row), so a header row
    left out of the quote ("at rest / in operation" under the grade header) fails. 0 if none."""
    for m in range(1, min(4, len(table))):
        if (_marks_out(" ".join(c for r in table[:m] for c, _ in r)) == header and len(table[m]) == width):
            return m
    return 0


def layout_row(line, pieces):
    """A pdftotext -layout line is the row: its columns (split at 2+ spaces) are the quoted cells, in order."""
    cols = [c for c in re.split(r"\s{2,}", line.strip()) if c]
    return len(cols) == len(pieces) and all(quotes.toks(c) == p for c, p in zip(cols, pieces))


def _continued(header, pieces, source, pno, hpage):
    """A row on page pno of a table whose header is printed on page hpage (at most 2 pages before): the header must
    be the whole header of the LAST table on hpage (ruled: the rows above its first full-width row; unruled: the
    lines after its caption up to the first data line), and the row a whole row on pno: of the FIRST ruled table
    with as many cells, or a whole line when unruled. No other table caption may stand on the pages in between or
    above the row on its own page."""
    if not 0 < pno - hpage <= 2 or any(CAPTION.search(layer_text(source, p)) for p in range(hpage + 1, pno)):
        return False, False
    flat = [t for p in pieces for t in p]
    here = [ln for ln in layer_text(source, pno).splitlines() if ln.strip()]
    at = next((i for i, ln in enumerate(here) if layout_row(ln, pieces)), None)
    if any(CAPTION.match(ln) for ln in here[:at if at is not None else len(here)]):
        return False, False                                    # another table starts above the row on its page
    if table_rows(source, hpage):
        t = table_groups(source, hpage)[-1]
        k = header_rows(t, header, len(pieces))
        if not k:
            return False, False
        words = poppler_words(source, hpage)
        head_layer = _marks_out(" ".join(" ".join(w[4] for w in words if _in_box(w, b)) for r in t[:k] for _, b in r))
        rows = [r for g in table_groups(source, pno)[:1] for r in g]
        hits = [_row_match(r, pieces, source, pno) for r in rows]
        return any(a for a, _ in hits) and head_layer == header, any(b for _, b in hits)
    lines = [ln for ln in layer_text(source, hpage).splitlines() if ln.strip()]
    caps = [i for i, ln in enumerate(lines) if CAPTION.match(ln)]
    if not caps:
        return False, False
    end = next((i for i in range(caps[-1] + 1, len(lines)) if re.search(r"\d", lines[i])), len(lines))
    block = [_marks_out(ln) for ln in lines[caps[-1] + 1:end]]
    if not (block and sorted(t for b in block for t in b) == sorted(header) and all(_in_order(b, header) for b in block)):
        return False, False
    if at is None or len(header) and len(pieces) != header_columns(lines[caps[-1] + 1:end]):
        return False, False
    return (True, any(len(quotes.toks(ln)) == len(flat) and quotes.contains(flat, quotes.toks(ln), True)
                      for ln in pdfminer_text(source, pno).splitlines()))


def header_columns(lines):
    """The number of columns of an unruled header: the most columns (split at 2+ spaces) on one of its lines."""
    return max((len([c for c in re.split(r"\s{2,}", ln.strip()) if c]) for ln in lines), default=0)


def _unruled_header(header, row, reader, source, pno, loose, pieces=None):
    """An unruled table's header and row: the header is ALL the lines from the line after the table's caption
    ("TABLE 1. ...", the nearest caption above the row) up to the first data line (a line with a number): the
    same tokens as the quoted header, each line's tokens in the quote's order; the row is a whole line below it,
    with no other caption in between."""
    lines = [ln for ln in reader(source, pno).splitlines() if ln.strip()]
    rows = [i for i, ln in enumerate(lines) if (not loose and layout_row(ln, pieces))
            or (loose and len(quotes.toks(ln)) == len(row) and quotes.contains(row, quotes.toks(ln), True))]
    for r in rows:
        cap = next((i for i in range(r - 1, -1, -1) if CAPTION.match(lines[i])), None)
        if cap is None:
            continue
        end = next((i for i in range(cap + 1, r + 1) if re.search(r"\d", lines[i])), r)
        block = [_marks_out(ln) for ln in lines[cap + 1:end]]
        if pieces is not None and not loose and header_columns(lines[cap + 1:end]) != len(pieces):
            continue
        if block and sorted(t for b in block for t in b) == sorted(header) and all(_in_order(b, header) for b in block):
            return True                                        # same tokens; each header line's in order (a unit
    return False                                               # on a second line, "(ppm)", sits in between)


def _in_order(sub, seq):
    it = iter(seq)
    return all(t in it for t in sub)


def table_groups(source, pno):
    """The rows of each ruled table on the page, table by table (table_rows' rows grouped)."""
    return table_rows(source, pno, grouped=True)


def _row_match(row, pieces, source, pno):
    """(poppler, pdfminer): the row's non-empty cells are exactly the pieces (all of them, in order), token for
    token."""
    if len(row) != len(pieces):
        return False, False
    cells = row
    miner = all(quotes.toks(x) == p for (x, _), p in zip(cells, pieces))
    words = poppler_words(source, pno)
    layer = miner and all(quotes.toks(" ".join(w[4] for w in words if _in_box(w, b))) == p
                          for (_, b), p in zip(cells, pieces))
    return layer, miner


def row_found(pieces, source, pno):
    """(in pdftotext, in pdfminer) for a table-row quote: its cells, in order and each whole (token for token),
    are all the non-empty cells of ONE row of a ruled table on the page, read by pdfminer (cell text) and by
    poppler (its words inside the same cell boxes). An unruled row (no such table) must stand on one line of the
    reading, cells in order."""
    in_layer = in_miner = False
    for row in table_rows(source, pno):                       # from the row's first cell (its label)
        layer, miner = _row_match(row, pieces, source, pno)
        in_layer, in_miner = in_layer or layer, in_miner or miner
    if not table_rows(source, pno):                           # unruled: a whole line of the page
        flat = [t for p in pieces for t in p]
        in_layer = any(layout_row(ln, pieces) for ln in layer_text(source, pno).splitlines())
        in_miner = any(len(quotes.toks(ln)) == len(flat) and quotes.contains(flat, quotes.toks(ln), loose=True)
                       for ln in pdfminer_text(source, pno).splitlines())
    return in_layer, in_miner


def _starts(source, p):
    """First tokens of the lines of a page that hold more than a number (a page-number line does not count)."""
    out = set()
    for ln in (layer_text(source, p).splitlines() if p >= 1 else []):
        t = ln.split()
        if len(t) > 1 or (t and not re.fullmatch(r"[\d\W]+", t[0])):
            out.add(t[0].strip("().:;,").lower())
    return out


def _lines(source, p):
    return [ln.strip().lower() for ln in (layer_text(source, p).splitlines() if p >= 1 else []) if ln.strip()]


def clause_findings(clause_number, source, pno):
    """The clause number as printed: its main number (the first part with a digit: "4.22" of "4.22 iii", "2" of
    "Table 2 Note 1") starts a line, or its reference up to that number does ("Table 2:"), on the page; and its
    first sub-part ("iii", "Note") starts a line on the page. The main number may stand on the page before only
    when a sub-part is given (a list running over the page break)."""
    parts = clause_number.split()
    main = next((i for i, t in enumerate(parts) if re.search(r"\d", t)), None)
    if main is None:
        return []
    num, ref = parts[main].strip("().:").lower(), " ".join(parts[:main + 1]).lower().rstrip(".:")
    subs = [t.strip("().:").lower() for t in parts[main + 1:] if t.strip("().:")]

    def printed(p):
        return num in _starts(source, p) or (main > 0 and any(re.match(re.escape(ref) + r"\b", ln)
                                                             for ln in _lines(source, p)))
    ok = printed(pno) or (bool(subs) and printed(pno - 1))
    if ok and subs:
        ok = subs[0] in _starts(source, pno)
    return [] if ok else [("clause", f"clause number {clause_number!r} is not printed as such on page {pno}")]


SCOPING = {"condition", "unless", "only"}   # lead-in wording that limits where every row or item applies
LIST_MARK = re.compile(r"^\s*(?:\(?[a-z]\)|\(?[ivx]+\)|\(?\d{1,2}\)|[ivx]+\.|[a-z]\.|[•■▪●◦‣\-–])\s", re.I)


def lead_in(item, source, pno):
    """The lead-in that governs a table row or list item (D46, owner): for a table row, the sentences of the page
    (and the page before) that point to a table ("as shown in Table 1"); for a list item (its quote starts with a
    list mark, or the page text before it ends with ":"), the sentence ending in that ":". "" when none."""
    text = re.sub(r"\s+", " ", " ".join(body(layer_text, source, p) for p in (pno - 1, pno) if p >= 1))
    sentences = obligations.sentences(text)
    if " | " in item["quote"]:
        n = table_number(source, pno)
        if n is None:
            return ""
        return " ".join(x for x in sentences if re.search(rf"\btables?\s+{n}\b(?!\.\d|\s*[.:]\s)", x, re.I)
                        and obligations.strength(x) and layer1_conditions(x))
    lines = [ln.strip() for ln in body(layer_text, source, pno).splitlines() if ln.strip()]
    q = quotes.toks(item["quote"])[:6]
    at = next((i for i, ln in enumerate(lines) if q and quotes.contains(q, quotes.toks(" ".join(lines[i:i + 3])))),
              None)
    if at is None:
        return ""
    for i in range(at - 1, max(at - 61, -1), -1):              # the nearest ":" line above, within the clause
        if re.match(r"\d+(?:\.\d+)+\.?\s", lines[i]) and not lines[i].endswith(":"):
            return ""                                          # another numbered clause starts: no lead-in
        if lines[i].endswith(":") and not lines[i].lower().startswith("note"):
            if LIST_MARK.match(item["quote"]) or i == at - 1 or LIST_MARK.match(lines[at]):
                start = max(i - 3, 0)                        # the sentence ending in ":" (up to 4 lines)
                joined = " ".join(lines[start:i + 1])
                return joined[joined.rfind(". ") + 2 if ". " in joined else 0:]
            return ""
    return ""


CAPTION = re.compile(r"^\s*(?:(?i:table)\s+(\d+)\s*[:.\-–]|TABLE\s+(\d+)\b)", re.M)


def table_number(source, pno):
    """The number of the table on a page: its caption line ("TABLE 2. Class 2 solvents", "Table 1: ...") when the
    page has exactly one; with none, the last caption of the page before (a table running over); else None."""
    here = [a or b for a, b in CAPTION.findall(layer_text(source, pno))]
    if len(set(here)) == 1:
        return here[0]
    if not here and pno > 1:
        before = [a or b for a, b in CAPTION.findall(layer_text(source, pno - 1))]
        return before[-1] if before else None
    return None


COND_CLAUSE = re.compile(r"\b(if|where|when|whenever|unless|only)\b(.*?)(?=,|;|\bthen\b|$)", re.I)


def lead_in_missing(lead, statement):
    """The scoping conditions of a lead-in that the statement does not carry: each condition clause ("if their
    use is unavoidable in order to produce a drug product with a significant therapeutic advance", "unless
    otherwise justified") must have its condition group in the statement and at least 80 % of its content words
    (4+ letters), so "when used" does not stand in for "if their use is unavoidable ..."."""
    import layer1
    if not lead:
        return []
    said = set(re.findall(r"[a-z]{4,}", statement.lower()))
    groups = layer1.conditions_in(statement)
    out = []
    for m in COND_CLAUSE.finditer(lead):
        word, rest = m.group(1), m.group(2)
        if len(re.findall(r"[a-z]{4,}", rest.lower())) < 2:     # "only if, after assessment, ...": take the
            rest = lead[m.start(2):].split(";")[0]               # clause on past the comma
            rest = re.split(r"\bthen\b|\.(?:\s|$)", rest)[0]
        clause = f"{word} {rest}".strip()
        group = layer1.conditions_in(clause) & SCOPING
        if not group:
            continue
        content = set(re.findall(r"[a-z]{4,}", rest.lower())) - {"their", "there", "this", "that", "these", "with",
                                                                   "from", "have", "been", "should", "shall", "must"}
        if not (group & groups) or (content and len(content & said) / len(content) < 0.8):
            out.append(clause)
    return out


def layer1_conditions(text):
    import layer1
    return layer1.conditions_in(text)


def check_item(item, source, pno):
    """Findings of one item (list of (check, message)) and whether its quote is in each reading."""
    import layer1
    span = [pno, pno + 1] if item["runs_over"] else [pno]
    if " | " in item["quote"]:
        in_layer, in_miner = table_quote_found(item["quote"], source, pno, item.get("header_page") or 0)
    else:
        q = quotes.toks(item["quote"])
        in_layer = any(quotes.contains(q, t) for t in readings(layer_text, source, span))
        in_miner = any(quotes.contains(q, t, loose=True) for t in readings(pdfminer_text, source, span))
    out = []
    if not (in_layer and in_miner):
        out.append(("quote", f"quote not found in {'pdftotext' if not in_layer else ''}"
                             f"{' and ' if not in_layer and not in_miner else ''}{'pdfminer' if not in_miner else ''}"))
    out += clause_findings(item["clause_number"], source, pno)
    for n in re.findall(r"\d+(?:[.,]\d+)?", item["statement"]):
        if not layer1.number_found(n, [item["quote"]]):
            out.append(("numbers", f"{n} in the statement, not in the quote"))
    for n in re.findall(r"(?<![\w.^])\d+(?:[.,]\d+)?", item["quote"]):          # not a footnote mark "^1"
        if not layer1.number_found(n, [item["statement"]]):
            out.append(("numbers", f"{n} in the quote, not in the statement"))
    lead = lead_in(item, source, pno)
    words = (layer1.strength_of(item["quote"]) or (layer1.strength_of(lead) if lead and " | " not in item["quote"]
                                                   else None)
             or ("mandatory" if source in layer1.INSPECTION_CHECKLISTS else None))
    if words and words != item["strength"]:
        out.append(("strength", f"quote says {words}, item {item['strength']}"))
    missing = lead_in_missing(lead, item["statement"])
    if missing:
        out.append(("lead-in", f"the statement lacks the lead-in's condition: {'; '.join(missing)[:160]}"))
    said = layer1.conditions_in(item["statement"])
    missing = layer1.conditions_missing(item["quote"], said)
    if missing:
        out.append(("conditions", "quote has " + ", ".join(missing) + " wording the statement lacks"))
    return out, in_layer, in_miner


DESCRIPTIVE = re.compile(r"\b(?:may|can|could)\s+(?:also\s+|even\s+|well\s+)?(?:include|contain|exist|occur|"
                         r"indicate|form|react|result|lead|cause|arise|vary|differ|affect|increase|decrease|"
                         r"necessitate|represent|appear|reflect|incorporate|help|be\s+(?:present|found|formed|due|"
                         r"caused|called|generated|introduced|seen|observed|contacted|something|"
                         r"added\s+intentionally|used\s+to\s+help|considered\s+to\s+be|more|less|higher|lower|"
                         r"useful|helpful|possible|difficult|facilitated))\b", re.I)


LEADING_REF = re.compile(r"^(?:\d+(?:\.\d+)+\.?|\(?[a-z]{1,4}\)|[ivx]+\.)\s+", re.I)
SIDE_TITLE = re.compile(r"WHO Technical Report Series,?\s*No\.\s*\d+,?\s*\d{4}", re.I)


def counts_for_coverage(sentence):
    """An obligation sentence the page's items must cover: shall/must/should (and their equivalents), or a "may"
    that grants or denies the site something ("quality reviews may be grouped", "the QP may not be the head of
    production"). Left out only: a sentence whose every clause with may/can/could states a possibility
    ("inspection coverage may include", "amines may be present"; a "not" never counts as descriptive). A table
    caption glued to its table and footnotes stays in (its footnote may hold an obligation)."""
    strength = obligations.strength(sentence)
    if not strength:
        return False
    if strength == "permissive":
        clauses = [c for c in re.split(r";|:|\bwhile\b|,\s*(?:and|but|whereas)\b", sentence)
                   if re.search(r"\b(?:may|can|could)\b", c, re.I)]
        if clauses and all(DESCRIPTIVE.search(c) and not re.search(r"\b(?:may|can|could)\s+not\b", c, re.I)
                           for c in clauses):
            return False
    return True


def coverage(source, pno, items_here, items_before, na):
    """Obligation sentences of the page's text layer not covered (see the module docstring)."""
    text = re.sub(r"\s+", " ", body(layer_text, source, pno))     # without running lines
    import layer1
    quotes_here = [i["quote"] for i in items_here + items_before]
    bags = [set(_words(q)) for q in quotes_here]
    na_keys = [" ".join(quotes.toks(x["text"])[:8]) for x in na]
    gaps = []
    for s in obligations.sentences(text):
        if not counts_for_coverage(s):
            continue
        s = LEADING_REF.sub("", SIDE_TITLE.sub(" ", s)).strip()    # "4.34 The ...", a glued WHO side title
        ws = _words(s)
        if not ws:
            continue
        conds = layer1.conditions_in(s)
        if any(sum(w in b for w in ws) / len(ws) >= COVERED_SHARE and not (conds - layer1.conditions_in(q))
               for b, q in zip(bags, quotes_here)):
            continue                                          # covered, with the sentence's conditions
        st = quotes.toks(s)                                   # several obligations of one sentence (or a lead-in
        parts = [q for q in quotes_here if quotes.contains(quotes.toks(q), st)]   # and its list), drafted one by
        if parts:                                             # one: the quotes printed inside it, together
            union = set().union(*(set(_words(q)) for q in parts))
            numbers = set(re.findall(r"\d+(?:[.,]\d+)?", s)) - set(re.findall(r"\d+(?:[.,]\d+)?", " ".join(parts)))
            if (sum(w in union for w in ws) / len(ws) >= UNION_SHARE and not numbers
                    and not (conds - layer1.conditions_in(" ".join(parts)))):
                continue                                      # 90 % of its words, every number, its conditions
        if any(k and k in " ".join(quotes.toks(s)) for k in na_keys):
            continue
        gaps.append(s[:300])
    return gaps


def ingest_draft(run):
    run = Path(run)
    items, failed, report = [], [], {"pages": 0, "items": 0, "quote_both": 0, "quote_layer_only": 0,
                                     "quote_pdfminer_only": 0, "quote_neither": 0, "text_layer_differs": [],
                                     "findings": {}, "coverage_gaps": [], "not_applicable": 0}
    for bf in sorted((run / "batches").glob("batch_*.json")):
        batch = json.loads(bf.read_text())
        af = run / "answers" / bf.name
        answers = {a["page"]: a for a in json.loads(af.read_text())["answers"]} if af.exists() else {}
        by_page = {}
        for p in batch["pages"]:
            a = answers.get(p["id"])
            if a is None:
                failed.append({"page": p["id"], "reason": "no answer"})
                continue
            by_page[p["page"]] = a
        for p in batch["pages"]:
            a = by_page.get(p["page"])
            if a is None:
                continue
            report["pages"] += 1
            report["not_applicable"] += len(a["not_applicable"])
            for k, it in enumerate(a["items"], start=1):
                found, in_layer, in_miner = check_item(it, p["source"], p["page"])
                key = ("quote_both" if in_layer and in_miner else "quote_layer_only" if in_layer
                       else "quote_pdfminer_only" if in_miner else "quote_neither")
                report[key] += 1
                import layer1
                rec = {"id": f"{p['id']}#{k}", "source": p["source"], "page": p["page"], **it,
                       "inspection_checklist": p["source"] in layer1.INSPECTION_CHECKLISTS,
                       "image_sha256": p["image_sha256"], "findings": found, "in_pdftotext": in_layer,
                       "in_pdfminer": in_miner}
                items.append(rec)
                if not (in_layer and in_miner) or it["text_layer_differs"]:
                    report["text_layer_differs"].append({"id": rec["id"], "quote": it["quote"][:200],
                                                         "drafter_note": it["text_layer_differs"],
                                                         "in_pdftotext": in_layer, "in_pdfminer": in_miner})
                for check, _ in found:
                    report["findings"][check] = report["findings"].get(check, 0) + 1
            before = by_page.get(p["page"] - 1, {"items": []})["items"]
            before = [i for i in before if i["runs_over"]]
            for g in coverage(p["source"], p["page"], a["items"], before, a["not_applicable"]):
                report["coverage_gaps"].append({"page": p["id"], "sentence": g})
    report["items"] = len(items)
    report["failed"] = failed
    with open(run / "items.jsonl", "w", encoding="utf-8") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    (run / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}, indent=1))
    return report


def prepare_verify(run, sources=None):
    """Verifier A and B batches, one per document (so a verifier opens at most that document's page images): each
    item with its page image path and text layer (blind: no drafter notes, no check results). A and B never share
    a batch. sources: only these documents (a sample)."""
    run = Path(run)
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    items = [i for i in items if not sources or i["source"] in sources]
    pages = {p["id"]: p for p in json.loads((run / "pages.json").read_text())["pages"]}
    vdir = run / "verify"
    (vdir / "batches").mkdir(parents=True, exist_ok=True)
    (vdir / "answers").mkdir(exist_ok=True)
    n = 0
    for role in ("a", "b"):
        instructions = (PROMPTS / f"verify_{role}.md").read_text()
        for source in sorted({i["source"] for i in items}):
            group = [i for i in items if i["source"] == source]
            n += 1
            chunk = [{"id": it["id"], "image": pages[f"{it['source']}:{it['page']}"]["image"],
                      "text_layer": layer_text(it["source"], it["page"]),
                      "next_page_text": layer_text(it["source"], it["page"] + 1) if it["runs_over"] else "",
                      "item": {**{k: it[k] for k in ("statement", "quote", "clause_number", "strength",
                                                       "plant_types", "condition", "runs_over")},
                               "header_page": it.get("header_page") or 0},
                      "plant_scope": pages[f"{it['source']}:{it['page']}"]["plant_scope"],
                      "header_image": (str(render(it["source"], it["header_page"])[0].relative_to(ROOT))
                                       if 1 <= (it.get("header_page") or 0) < it["page"] else ""),
                      "header_page_text": (layer_text(it["source"], it["header_page"])
                                           if 1 <= (it.get("header_page") or 0) < it["page"] else "")}
                     for it in group]
            (vdir / "batches" / f"batch_{n:03d}_{role}.json").write_text(json.dumps(
                {"role": role, "instructions": instructions, "schema": VERIFY_SCHEMA, "items": chunk},
                indent=1, ensure_ascii=False))
    print(vdir, n, "batches")


def ingest_verify(run):
    run = Path(run)
    verdicts = {"a": {}, "b": {}}
    for af in sorted((run / "verify" / "answers").glob("batch_*.json")):
        role = af.stem.rsplit("_", 1)[1]
        for a in json.loads(af.read_text())["answers"]:
            verdicts[role][a["id"]] = a
    items = [json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip()]
    rep = {"items": len(items), "both_correct": 0, "both_incorrect": 0, "disagree": 0, "unanswered": 0,
           "cases": []}
    for it in items:
        a, b = verdicts["a"].get(it["id"]), verdicts["b"].get(it["id"])
        if not a or not b:
            rep["unanswered"] += 1
            continue
        if a["verdict"] == b["verdict"] == "correct":
            rep["both_correct"] += 1
        else:
            rep["both_incorrect" if a["verdict"] == b["verdict"] else "disagree"] += 1
            rep["cases"].append({"id": it["id"], "a": a["verdict"], "a_reason": a["reason"], "b": b["verdict"],
                                 "b_reason": b["reason"]})
    (run / "verify-report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in rep.items() if k != "cases"}, indent=1))
    return rep


def record_model(run, role, model):
    """Records in RUN/agents.json which model answered a stage (D46: the audit trail names it; owner, D30)."""
    path = Path(run) / "agents.json"
    doc = json.loads(path.read_text()) if path.exists() else {}
    doc[role] = {"model": model, "recorded": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    path.write_text(json.dumps(doc, indent=1) + "\n")


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "prepare-draft":
        targets = [(a.rsplit(":", 1)[0], int(a.rsplit(":", 1)[1])) for a in args] or \
                  [(s, p) for s, ps in TRIAL.items() for p in ps]
        prepare_draft(targets)
    elif cmd == "ingest-draft":
        ingest_draft(args[0])
    elif cmd == "prepare-verify":
        prepare_verify(args[0], args[1:] or None)
    elif cmd == "ingest-verify":
        ingest_verify(args[0])
    elif cmd == "record-model":
        record_model(*args)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
