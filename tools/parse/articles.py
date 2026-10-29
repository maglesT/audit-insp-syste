"""Parser for EU legal acts (Directive (EU) 2017/1572, Regulation (EU) No 1252/2014): recitals and articles.

References follow EU citation practice: "Recital (7)", "Article 5", "Article 5(2)" for numbered paragraph 2, and
"Article 4(2)(a)" or "Article 7(1)(3)" for points. Chapter headings are unnumbered segments.

- Recitals "(1)", "(2)", ... before Article 1 are accepted only in sequence.
- Footnotes: the Official Journal numbers footnotes from (1) on each page, at the page bottom. A line "(1) OJ ...",
  "(1) Regulation ...", "(1) Commission ..." that is not the expected recital starts footnote mode, which lasts to the
  end of the page; text on the next page continues the clause the footnotes interrupted.
- Inside an article, "1.", "2." are paragraphs and "(a)", "(1)" points, each accepted only in sequence, so a number
  inside a sentence never starts a clause.
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, normalise, pdf_pages  # noqa: E402
from headings import body_lines  # noqa: E402

ARTICLE = re.compile(r"^Article\s+(\d{1,3})$")
CHAPTER = re.compile(r"^(CHAPTER|SECTION)\s+([IVX]+|\d+)\b")
PARAGRAPH = re.compile(r"^(\d{1,2})\.\s+(\S.*)$")
POINT = re.compile(r"^\((\d{1,2}|[a-z])\)\s+(\S.*)$")
FOOTNOTE = re.compile(r"^\(1\)\s+(OJ\s|Regulation\b|Directive\b|Commission\b|Council\b|Decision\b)")


def _successor(prev, cur):
    if prev is None:
        return cur in ("1", "a")
    if prev.isdigit() and cur.isdigit():
        return int(cur) == int(prev) + 1
    return prev.isalpha() and cur.isalpha() and ord(cur) == ord(prev) + 1


def parse(path, pages=None):
    """Recitals and articles as clauses: (clauses, body_chars, dropped_chars)."""
    pages = pdf_pages(path) if pages is None else pages
    lines, dropped = body_lines(pages, keep=ARTICLE)
    clauses, cur, resume, unnumbered, body = [], None, None, 0, 0
    article = paragraph = point = None
    recital, footnote_page = 0, None

    def start(kind, ref, line, pno):
        nonlocal cur
        cur = {"kind": kind, "ref": ref, "lines": [line], "page_start": pno, "page_end": pno}
        clauses.append(cur)

    for pno, line in lines:
        body += len(line.replace(" ", ""))
        if footnote_page is not None and pno != footnote_page:
            footnote_page, cur = None, resume          # the interrupted clause goes on after the footnotes
        if footnote_page is not None:
            cur["lines"].append(line)
            continue
        m = ARTICLE.match(line)
        if m:
            article, paragraph, point = m.group(1), None, None
            start("clause", f"Article {article}", line, pno)
            continue
        if CHAPTER.match(line):
            unnumbered += 1
            start("unnumbered", f"_unnumbered:{unnumbered}", line, pno)
            continue
        p = POINT.match(line)
        if article is None and p and p.group(1).isdigit() and int(p.group(1)) == recital + 1 and not (
                recital and FOOTNOTE.match(line)):
            recital += 1
            start("clause", f"Recital ({recital})", line, pno)
            continue
        if FOOTNOTE.match(line):
            resume, footnote_page = cur, pno
            unnumbered += 1
            start("unnumbered", f"_footnotes:{unnumbered}", line, pno)
            continue
        if article is not None:
            m = PARAGRAPH.match(line)
            if m and _successor(paragraph, m.group(1)):
                paragraph, point = m.group(1), None
                start("clause", f"Article {article}({paragraph})", line, pno)
                continue
            if p and _successor(point, p.group(1)):
                point = p.group(1)
                start("clause", f"Article {article}" + (f"({paragraph})" if paragraph else "") + f"({point})",
                      line, pno)
                continue
        if cur is None:
            unnumbered += 1
            start("unnumbered", f"_unnumbered:{unnumbered}", line, pno)
        else:
            cur["lines"].append(line)
            cur["page_end"] = pno
    return [Clause(source=Path(path).name, ref=c["ref"], section="", number=c["ref"] if c["kind"] == "clause" else "",
                   heading=c["lines"][0][:160], text=normalise(" ".join(c["lines"])), page_start=c["page_start"],
                   page_end=c["page_end"], kind=c["kind"]) for c in clauses], body, dropped
