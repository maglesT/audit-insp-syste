"""Read the tables a tagged PDF carries in its own structure tree (D52: raw structure first).

Many PDFs (Word, PDF CoDe, iLovePDF exports) are "tagged": the file itself says which text is a table row and
which a cell (TR / TD / TH), linked to the printed glyphs by marked-content ids. Reading that structure gives the
table exactly as made, with no layout guessing. The text of every cell is the printed glyphs (the text layer),
never recognised from an image.

  python3 tools/extract/tagged.py FILE.pdf            # summary: tagged?, tables, rows, cells

`read_rows(path)` returns, per page, the table rows in structure order; each cell has its text and its bounding
box (x0, top, x1, bottom) on the page, so a profile can check columns and rows geometrically. `outside` is the
page's text that lies in no table cell (running headers, notes), for the completeness check.
"""
import sys

import pdfplumber

# Symbol-font bullets that the text layer maps to private-use code points.
GLYPHS = {"": "—", "": "•", "": "▪", "": "•"}


def fix_glyphs(text):
    return "".join(GLYPHS.get(ch, ch) for ch in text)


def _mcids(node):
    found = list(node.get("mcids") or [])
    for child in node.get("children", []):
        found += _mcids(child)
    return found


def _find(node, kind):
    if node.get("type") == kind:
        return [node]
    found = []
    for child in node.get("children", []):
        found += _find(child, kind)
    return found


def is_tagged(path):
    with pdfplumber.open(path) as pdf:
        return any(page.structure_tree for page in pdf.pages[:3])


def read_rows(path, pages=None):
    out = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            if pages and number not in pages:
                continue
            by_mcid = {}
            for ch in page.chars:
                if ch.get("mcid") is not None:
                    by_mcid.setdefault(ch["mcid"], []).append(ch)
            used, rows = set(), []
            for root in page.structure_tree:
                for tr in _find(root, "TR"):
                    cells = []
                    for td in [c for c in tr.get("children", []) if c.get("type") in ("TD", "TH")]:
                        ids = _mcids(td)
                        used.update(ids)
                        chars = [c for m in ids for c in by_mcid.get(m, [])]
                        box = None
                        if chars:
                            box = [min(c["x0"] for c in chars), min(c["top"] for c in chars),
                                   max(c["x1"] for c in chars), max(c["bottom"] for c in chars)]
                        cells.append({"text": "".join(c["text"] for c in chars), "box": box})
                    rows.append(cells)
            outside = "".join(c["text"] for c in page.chars if c.get("mcid") not in used)
            out.append({"page": number, "rows": rows, "outside": outside})
    return out


if __name__ == "__main__":
    pages = read_rows(sys.argv[1])
    rows = sum(len(p["rows"]) for p in pages)
    cells = sum(len(r) for p in pages for r in p["rows"])
    print(f"{len(pages)} pages, {rows} table rows, {cells} cells")
