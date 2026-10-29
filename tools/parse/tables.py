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
  follows a header row, e.g. "Date of / Approval"); each is kept once per table as kind "table_header". A data row
  that happens to repeat (grade "C" limits in two Annex 1 tables) is not a header, because data rows come first.
- Rows that are mostly Devanagari are dropped (counted as dropped text).
- The row label is the first cell (cut to its first words, about 40 characters, with "…"), or "row <n>" when the
  first cell is empty. The reference is "Table <k> <label>"; a label already used gets "#2", "#3".
- Text beside a table (in the same vertical band, outside the table) is read with pdfplumber and kept after the
  marker, so nothing is dropped.
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
from common import CITABLE, Clause, devanagari_share, english_page, normalise, pdf_pages  # noqa: E402

LABEL_MAX = 40
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
    return subprocess.run(["pdftotext", "-layout", "-f", str(pno), "-l", str(pno), "-x", "0", "-y", str(y),
                           "-W", str(math.ceil(width) + 1), "-H", str(math.ceil(bottom) - y), str(path), "-"],
                          capture_output=True, text=True, check=True).stdout.replace("\f", "")


def _words(path, pno):
    """poppler's words of one page with their boxes, in poppler's reading order."""
    out = subprocess.run(["pdftotext", "-bbox", "-f", str(pno), "-l", str(pno), str(path), "-"],
                         capture_output=True, text=True, check=True).stdout
    return [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in WORD.findall(out)]


def _cells(table, words):
    """Cell texts of a table, row by row; a word belongs to the cell that holds its centre."""
    rows = []
    for row in table.rows:
        cells = []
        for box in row.cells:
            if box is None:
                cells.append("")
                continue
            inside = [w for w in words if box[0] <= (w[0] + w[2]) / 2 <= box[2] and box[1] <= (w[1] + w[3]) / 2 <= box[3]]
            cells.append(normalise(" ".join(w[4] for w in inside)))
        rows.append(cells)
    return rows


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
            if not found:
                pages.append(plain)
                continue
            words = _words(path, pno)
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
                text = beside.extract_text() or ""
                if text.strip():
                    parts.append(text)
                top = max(top, t.bbox[3])
            below = _band(path, pno, page.width, top, page.height)
            parts.append(below)
            if first is not None:
                tables[-1]["after"] = _lines(below)
            pages.append("\n".join(parts))
    return pages, tables, dropped


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


def parse(path):
    """Numbered parse of the text around the tables plus one clause per table row: (clauses, body, dropped)."""
    import numbered
    pages, tables, dropped_rows = read(path)
    if not tables:
        return numbered.parse(path)
    clauses, body, dropped = numbered.parse(path, pages=pages)
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
    body += sum(len(x.replace(" ", "")) for t in tables for r in t["rows"] for x in r)
    return kept + rows, body, dropped + dropped_rows


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
                      and (len(filled) > 1 or prev_header))
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
