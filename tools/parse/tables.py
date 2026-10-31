"""Table-aware extraction with pdfplumber (D21): one clause per table row.

Some sources are tables, not numbered paragraphs (the PIC/S Annex 1 interpretation table, the ICH Q7 Q&A, the
PIC/S aide-memoires, the CDSCO checklists), and numbered texts contain tables too (EU Annex 1 grade limits, ICH Q10
Table I). `pdftotext -layout` prints table columns side by side, so a sentence in the "Answers" column is cut into
line fragments mixed with the "Questions" column. Here pdfplumber finds the ruled tables (their cell boxes) and every
row becomes one clause whose cells are kept apart. The words in each cell come from poppler (`pdftotext -bbox`), the
same extractor as the rest of the text: pdfplumber's own text garbles some fonts and reverses rotated cells. The text
around the tables is still read with `pdftotext -layout`, band by band between the tables, so the numbered parser
sees the same text as before. Deterministic, no AI.

Rules:
- A table has at least 2 columns; a single row counts (a long question and answer can fill a page as one row).
  Tables nested inside another table's cell are dropped (pdfplumber also reports the inner grid of a merged cell).
  A table with words inside its outline that no cell holds is not a table (highlight boxes behind running text):
  its page part is read as text, so the words are not lost. A cell left out for a missing rule gets its
  column's box (_row_boxes).
  Tables on pages that are not English are skipped with the page (bilingual gazettes).
- Where a table sat, the page text gets a marker line; the clause the marker lands in becomes the table's parent
  (field `parent`). When the marker lands in a contents list or an unnumbered segment, the parent is the nearest
  clause before it that has a reference of its own ("" if none). The marker is removed again.
- A table continues the previous one over a page break only when it is the first table on its page, the previous
  table was the last on its page, both have the same number of columns, and at most a running header and footer
  lie between them (no caption such as "Table III"). It then keeps the table number.
- A row whose first cell is empty continues the last data row of the same table (rows split by a page break, or an
  item spread over several ruled lines); its cells are appended to that row's cells.
- A row with text in the first cell only is a group caption ("2. Quality Management System"); it becomes a clause of
  its own and its text is the `section` (group) of the rows below it. A caption repeated at the top of the next page
  is skipped.
- Header rows ("Questions | Answers") are rows at the top of a table (only captions and headers above them) made of
  short cells whose text is also one of the top two rows of another table (a one-cell row counts when it directly
  follows a header row, e.g. "Date of / Approval", or has an empty first cell and is followed by a header row
  of several cells, e.g. the CDSCO "Quality Rating" band above the rating columns, which would otherwise continue
  the last row of the page before); each is kept once per table as kind "table_header". A data row
  that happens to repeat (grade "C" limits in two Annex 1 tables) is not a header, because data rows come first.
- Rows that are mostly Devanagari are dropped (counted as dropped text).
- The row label is the first cell (cut to its first words, about 40 characters, with "…"), or "row <n>" when the
  first cell is empty. The reference is "Table <k> <label>"; a label already used gets "#2", "#3".
- Text beside a table (in the same vertical band, outside the table) is read with pdfplumber and kept after the
  marker, so nothing is dropped. Turned text outside the tables is added as lines of its own (_put_turned).
"""
import html
import math
import re
import subprocess
import sys
from pathlib import Path

import pdfplumber

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CITABLE, Clause, devanagari_share, english_page, normalise, pdf_pages, unshift_glyphs  # noqa: E402

LABEL_MAX = 40
ROW_LABEL = re.compile(r"\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\.?")
HEADER_CELL_MAX = 40
GAP_LINES = 3          # lines allowed between two tables that continue each other (running header and footer)
MARKER = "[[TABLE {}]]"
MARKER_RX = re.compile(r"\[\[TABLE (\d+)\]\]")
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')


def _inside(a, b, tol=1.0):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


def page_tables(page):
    """Real tables on a page in reading order: at least 2 columns, not nested in another table."""
    found = [t for t in page.find_tables() if len(t.columns) >= 2]
    found = [t for t in found if not any(o is not t and o.bbox != t.bbox and _inside(t.bbox, o.bbox) for o in found)]
    return sorted(found, key=lambda t: (round(t.bbox[1]), t.bbox[0]))


def _drop_empty_columns(rows):
    width = max((len(r) for r in rows), default=0)
    rows = [r + [""] * (width - len(r)) for r in rows]
    keep = [j for j in range(width) if any(r[j] for r in rows)]
    return [[r[j] for j in keep] for r in rows]


def _in_box(obj, box):
    x, y = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def _band(path, pno, width, top, bottom):
    """pdftotext -layout text of a full-width horizontal band of one page."""
    if bottom - top < 1:
        return ""
    y = math.floor(top)
    out = subprocess.run(["pdftotext", "-layout", "-f", str(pno), "-l", str(pno), "-x", "0", "-y", str(y),
                           "-W", str(math.ceil(width) + 1), "-H", str(math.ceil(bottom) - y), str(path), "-"],
                          capture_output=True, text=True, check=True).stdout.replace("\f", "")
    return unshift_glyphs(out)


def _words(path, pno):
    """poppler's words of one page with their boxes, in poppler's reading order."""
    out = subprocess.run(["pdftotext", "-bbox", "-f", str(pno), "-l", str(pno), str(path), "-"],
                         capture_output=True, text=True, check=True).stdout
    return [(float(a), float(b), float(c), float(d), unshift_glyphs(html.unescape(w)))
            for a, b, c, d, w in WORD.findall(out)]


def _row_boxes(table):
    """The cell boxes of each row. pdfplumber leaves a cell out (None) when one of its rules is missing; such a
    gap gets the box of its column within the row, unless another cell of the table overlaps that box (a cell
    merged across columns or rows). Without this the text of the cell is lost (CDSCO circular, example row 27.4)."""
    cols = [c.bbox if c else None for c in table.columns]
    cells = [b for row in table.rows for b in row.cells if b]
    out = []
    for row in table.rows:
        boxes = list(row.cells)
        for j, box in enumerate(boxes):
            if box is None and j < len(cols) and cols[j]:
                gap = (cols[j][0], row.bbox[1], cols[j][2], row.bbox[3])
                if not any(_overlap(gap, o) for o in cells):
                    boxes[j] = gap
        out.append(boxes)
    return out


def _overlap(a, b, tol=1.0):
    return a[0] < b[2] - tol and b[0] < a[2] - tol and a[1] < b[3] - tol and b[1] < a[3] - tol


def stray_words(table, words):
    """Words inside a table's outline that no cell holds. A real table has none; a "table" that pdfplumber built
    from highlight boxes behind running text (FDA compliance programs, the 2024 nitrosamine guidance) leaves the
    unhighlighted words between the boxes in no cell, and storing its "rows" would lose them."""
    boxes = [b for r in _row_boxes(table) for b in r if b]
    return [w for w in words if _centre_in(w, table.bbox) and not any(_centre_in(w, b) for b in boxes)]


def _cells(table, words):
    """Cell texts of a table, row by row; a word belongs to the cell that holds its centre.

    A ruled row whose first cell holds several numbered labels ("3.3", "3.4", ... with no rule between them, PIC/S
    PI 038) is split at the height of each label, so every item becomes a row of its own.
    """
    rows = []
    for row, cells in zip(table.rows, _row_boxes(table)):
        first = cells[0] if cells else None
        if first is None:
            rows.append([_text(box, words) if box else "" for box in cells])
            continue
        labels = sorted({round(w[1], 1) for w in words if ROW_LABEL.fullmatch(w[4]) and _centre_in(w, first)
                         and w[0] - first[0] < 25})
        if len(labels) < 2:
            rows.append([_text(box, words) if box else "" for box in cells])
            continue
        cuts = [None] + [y - 0.5 for y in labels[1:]] + [None]       # cut just above each further label
        for top, bottom in zip(cuts, cuts[1:]):
            rows.append([_text(box, words, top, bottom) if box else "" for box in cells])
    return rows


def _centre_in(w, box):
    return box[0] <= (w[0] + w[2]) / 2 <= box[2] and box[1] <= (w[1] + w[3]) / 2 <= box[3]


def _text(box, words, top=None, bottom=None):
    """Words of a cell, optionally only those whose centre lies in [top, bottom) (half-open: a word on a cut
    line belongs to exactly one slice)."""
    def inside(w):
        y = (w[1] + w[3]) / 2
        return _centre_in(w, box) and (top is None or y >= top) and (bottom is None or y < bottom)
    return normalise(" ".join(w[4] for w in words if inside(w)))


def _lines(text):
    return [ln for ln in text.splitlines() if ln.strip()]


def read(path):
    """Tables of a PDF and its page texts with each table replaced by a marker line.

    Returns (pages, tables, dropped): tables = [{"page": n, "rows": [[cell, ...], ...], "before": lines above it on
    its page if it is the first table there, "after": lines below it if it is the last}] in reading order; table i
    is marked in its page text as MARKER.format(i). dropped = characters of non-English table rows.
    """
    layout = pdf_pages(path)
    pages, tables, dropped = [], [], 0
    with pdfplumber.open(str(path)) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            plain = layout[pno - 1] if pno <= len(layout) else ""
            found = page_tables(page) if english_page(plain) else []
            words = _words(path, pno) if found else []
            found = [t for t in found if not stray_words(t, words)]
            exps = exponents(page)
            if not found:
                pages.append(mark_exponents(plain, exps)[0])
                continue
            parts, top, first = [], 0.0, None
            for n, t in enumerate(found):
                above = _band(path, pno, page.width, top, t.bbox[1]) if t.bbox[1] > top else ""
                parts.append(above)
                rows = []
                for r in _drop_empty_columns(_cells(t, words)):
                    if not any(r):
                        continue
                    if devanagari_share(" ".join(r)) >= 0.3:
                        dropped += sum(len(c.replace(" ", "")) for c in r)
                        continue
                    rows.append(r)
                if rows:
                    parts.append(MARKER.format(len(tables)))
                    tables.append({"page": pno, "rows": rows, "before": _lines(above) if first is None else None,
                                   "after": None})
                    first = first if first is not None else len(tables) - 1
                band = (0, max(top, t.bbox[1]), page.width, t.bbox[3])
                beside = page.filter(lambda o, band=band: o.get("object_type") == "char" and _in_box(o, band)
                                     and not any(_in_box(o, u.bbox) for u in found))
                text = _beside_text(beside)
                if text.strip():
                    parts.append(text)
                top = max(top, t.bbox[3])
            below = _band(path, pno, page.width, top, page.height)
            parts.append(below)
            if first is not None:
                tables[-1]["after"] = _lines(below)
            text, exps = mark_exponents(_put_turned(page, "\n".join(parts), found), exps)
            pages.append(text)
            for t in tables[first if first is not None else len(tables):]:
                for r in t["rows"]:
                    for j, c in enumerate(r):
                        r[j], exps = mark_exponents(c, exps)
    return pages, tables, dropped


EXP_CHARS = "-−–0123456789"


def exponents(page):
    """Powers of ten printed with a raised, smaller exponent ("10" then "-6" set small above the line), in reading
    order: ["-6", "7", ...]. poppler prints them flat ("10-6", "107"), which reads as another number."""
    chars = [c for c in page.chars if c.get("upright", True)]
    out = []
    for i in range(2, len(chars)):
        one, zero, c = chars[i - 2], chars[i - 1], chars[i]
        if (one["text"], zero["text"]) != ("1", "0") or c["text"] not in EXP_CHARS:
            continue
        if not (c["size"] < 0.85 * zero["size"] and c["bottom"] < zero["bottom"] - 1 and abs(c["x0"] - zero["x1"]) < 2):
            continue
        j, exp = i, ""
        while j < len(chars) and chars[j]["text"] in EXP_CHARS and chars[j]["size"] < 0.85 * zero["size"]:
            exp, j = exp + chars[j]["text"], j + 1
        if re.search(r"\d", exp):
            out.append(exp)
    return out


def mark_exponents(text, exps):
    """Writes the exponents found by exponents() as "10^-6" where the flat text has "10-6" (in order, each once);
    returns the text and the exponents not found in it."""
    rest = []
    for exp in exps:
        rx = re.compile(r"(?<![\d.,^])10 ?" + re.escape(exp) + r"(?![\d^])")
        m = rx.search(text)
        if m:
            text = text[:m.start()] + "10^" + exp + text[m.end():]
        else:
            rest.append(exp)
    return text, rest


def _beside_text(part):
    """Text of a page part beside a table, upright text only: turned text (the running title WHO prints up the
    margin) comes out backwards here ("4202 ,2501 .oN WHO Technical Report Series"); _put_turned adds it."""
    return part.filter(lambda o: o.get("upright", True)).extract_text() or ""


def _put_turned(page, text, found):
    """A table page's text with its turned lines outside the tables (the WHO side title up the margin) put right:
    the table bands cut such a line in pieces, poppler prints its piece inside a body line in reversed order ("No.
    1052, 2024 WHO Technical Report Series,"). Every run of tokens of a line that are words of a turned line, at
    least 2 and at least half of that line's words, is taken out, and each turned line is added once as a line of its own, in reading order, where the
    running-line rules recognise it."""
    outside = page.filter(lambda o: o.get("object_type") != "char" or not any(_in_box(o, t.bbox) for t in found))
    turned = _turned_lines(outside)
    if not turned:
        return text
    lines = text.split("\n")
    for words in turned:
        for i, ln in enumerate(lines):
            toks, keep, j = ln.split(), [], 0
            while j < len(toks):
                pool, k = list(words), j
                while k < len(toks) and toks[k] in pool:
                    pool.remove(toks[k])
                    k += 1
                if k - j >= max(2, len(words) / 2):
                    j = k
                else:
                    keep.append(toks[j])
                    j += 1
            if len(keep) < len(toks):
                lines[i] = " ".join(keep)
        lines.append(" ".join(words))
    return "\n".join(lines)


def _turned_lines(part):
    """The turned text of a page part (characters not upright) as lines of words in reading order."""
    turned = [c for c in part.chars if not c["upright"]]
    if not turned:
        return []
    up = sum(c["matrix"][1] > 0 for c in turned) > len(turned) / 2
    rest = part.filter(lambda o: not o.get("upright", True))
    words = rest.extract_words(line_dir_rotated="ltr" if up else "rtl", char_dir_rotated="btt" if up else "ttb")
    lines = {}
    for w in words:                                      # a line of turned text is a column of the page
        key = next((k for k in lines if abs(k - w["x0"]) <= 2), w["x0"])
        lines.setdefault(key, []).append(w)
    return [[w["text"] for w in sorted(lines[k], key=lambda w: -w["bottom"] if up else w["top"])]
            for k in sorted(lines, reverse=not up)]


def logical_numbers(tables):
    """Table numbers; a table that goes on over a page break keeps its number (rule in the module docstring)."""
    nums, k, prev = [], 0, None
    for t in tables:
        cont = (prev is not None and t["page"] == prev["page"] + 1 and len(t["rows"][0]) == len(prev["rows"][-1])
                and t.get("before") is not None and prev.get("after") is not None
                and len(t["before"]) + len(prev["after"]) <= GAP_LINES
                and not any(re.match(r"\s*(Table|TABLE|Figure)\b", ln) for ln in t["before"] + prev["after"]))
        k = k if cont else k + 1
        nums.append(k)
        prev = t
    return nums


def parse(path, text_parser=None):
    """Parse of the text around the tables (numbered parser unless another is given, e.g. headings.parse) plus one
    clause per table row: (clauses, body, dropped)."""
    if text_parser is None:
        import numbered
        text_parser = numbered.parse
    pages, tables, dropped_rows = read(path)
    if not tables:
        return text_parser(path)
    clauses, body, dropped = text_parser(path, pages=pages)
    parent, kept, last_ref = {}, [], ""
    for c in clauses:
        found = MARKER_RX.findall(c.text)
        if found:
            c.text = normalise(MARKER_RX.sub(" ", c.text))
            c.heading = normalise(MARKER_RX.sub(" ", c.heading))
            own = c.kind in CITABLE and bool(c.text)
            for i in found:
                parent[int(i)] = c.ref if own else last_ref
                body -= len(MARKER.format(i).replace(" ", ""))
        if c.kind in CITABLE and c.text:
            last_ref = c.ref
        if c.text:
            kept.append(c)
    rows = rows_to_clauses(Path(path).name, tables, parent)
    raw = sum(len(x.replace(" ", "").replace("|", "")) for t in tables for r in t["rows"] for x in r)
    kept_chars = sum(len(c.text.replace(" ", "").replace("|", "")) for c in rows)
    # header and caption rows repeated on every page are kept once; the repeats count as dropped, like running
    # page headers
    body += kept_chars
    return kept + rows, body, dropped + dropped_rows + max(0, raw - kept_chars)


def _row_key(row):
    return " | ".join(c.lower() for c in row if c)


def rows_to_clauses(source, tables, parent=None):
    """One clause per table row, with continuation rows merged and header rows marked."""
    parent = parent or {}
    counts = {}                                          # how often a row is one of the top two rows of a table
    for t in tables:
        for r in t["rows"][:2]:
            counts[_row_key(r)] = counts.get(_row_key(r), 0) + 1
    out, used, headers, first_of = [], {}, set(), {}
    last, group, current = None, "", None
    for idx, (k, t) in enumerate(zip(logical_numbers(tables), tables)):
        if k != current:                                 # a new table: nothing carries over from the last one
            current, last, group = k, None, ""
        first_of.setdefault(k, idx)
        par = parent.get(first_of[k], "")
        leading, prev_header = True, False
        for i, row in enumerate(t["rows"]):
            key = _row_key(row)
            filled = [j for j, c in enumerate(row) if c]
            caption = filled == [0] and len(row) > 1
            short = all(len(c) <= HEADER_CELL_MAX for c in row if c)
            header = (leading and short and not caption and counts.get(key, 0) > 1
                      and (len(filled) > 1 or prev_header or (row[0] == "" and _header_next(t["rows"], i, counts))))
            prev_header = header
            if header:
                if (k, key) not in headers:
                    headers.add((k, key))
                    out.append(_row(_unique(f"Table {k} header", used), par, group, row, t["page"], "table_header"))
                continue
            if caption:
                if leading and row[0] == group:          # the caption repeated at the top of the next page
                    continue
                group, last = row[0], None
                out.append(_row(_unique(f"Table {k} {_label(row[0])}", used), par, group, row, t["page"],
                                "table_row"))
                continue
            leading = False
            if row[0] == "" and last is not None and len(last["cells"]) == len(row):
                for j, c in enumerate(row):
                    if c:
                        last["cells"][j] = (last["cells"][j] + " " + c).strip()
                last["page_end"] = t["page"]
                continue
            label = _label(row[0]) if row[0] else f"row {i + 1}"
            last = _row(_unique(f"Table {k} {label}", used), par, group, row, t["page"], "table_row")
            out.append(last)
    return [Clause(source=source, ref=c["ref"], section=c["group"], number="",
                   heading=(c["cells"][0] or c["ref"])[:160], text=normalise(" | ".join(x for x in c["cells"] if x)),
                   page_start=c["page_start"], page_end=c["page_end"], kind=c["kind"], parent=c["parent"])
            for c in out]


def _header_next(rows, i, counts):
    """The row after row i is a header row of several short cells (one of the top two rows of another table)."""
    if i + 1 >= len(rows):
        return False
    nxt = rows[i + 1]
    return (sum(1 for c in nxt if c) > 1 and all(len(c) <= HEADER_CELL_MAX for c in nxt if c)
            and counts.get(_row_key(nxt), 0) > 1)


def _label(text):
    """A short label: the text itself, or its first words up to LABEL_MAX characters."""
    if len(text) <= LABEL_MAX:
        return text
    return text[:LABEL_MAX].rsplit(" ", 1)[0].rstrip(" ,;:-–") + "…"


def _row(ref, parent, group, row, page, kind):
    return {"ref": ref, "parent": parent, "group": group, "cells": list(row), "page_start": page, "page_end": page,
            "kind": kind}


def _unique(ref, used):
    used[ref] = used.get(ref, 0) + 1
    return ref if used[ref] == 1 else f"{ref} #{used[ref]}"
