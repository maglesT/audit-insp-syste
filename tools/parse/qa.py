"""Parser for question-and-answer documents (EMA and PIC/S Q&A PDFs) (deterministic, no AI).

A clause is one question with its answer: "Q7". A line starts question n when it carries the next question number,
in one of the forms these documents use:
- "Q7" alone, or "Q7." / "Q7:" followed by the question ("A7" then marks the answer and stays in the clause);
- "7." followed by text, when the question mark comes within the next three lines (so numbered lists inside answers,
  which rarely ask questions, do not start clauses).
Numbers are accepted only in sequence (skipping at most one, noted as a gap). A contents list of the questions (dot
leaders) is skipped. Text before the first question (background) is an unnumbered segment.
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, normalise, pdf_pages  # noqa: E402
from headings import body_lines, contents_block  # noqa: E402

Q_LABEL = re.compile(r"^Q\s?(\d{1,3})\b[.:)]?\s*(.*)$")
Q_NUMBER = re.compile(r"^(\d{1,3})\.\s+(\S.*)$")
LOOK = 3


def parse(path, pages=None):
    """Questions with their answers as clauses: (clauses, body_chars, dropped_chars)."""
    pages = pdf_pages(path) if pages is None else pages
    lines, dropped = body_lines(pages)
    toc = contents_block(lines)
    clauses, cur, unnumbered, body, expected = [], None, 0, 0, 1

    def start(kind, ref, line, pno):
        nonlocal cur
        cur = {"kind": kind, "ref": ref, "lines": [line], "page_start": pno, "page_end": pno, "notes": []}
        clauses.append(cur)

    for i, (pno, line) in enumerate(lines):
        body += len(line.replace(" ", ""))
        if toc and toc[0] <= i <= toc[1]:
            if cur and cur["kind"] == "toc":
                cur["lines"].append(line)
            else:
                start("toc", f"_toc:{len(clauses) + 1}", line, pno)
            continue
        n = None
        m = Q_LABEL.match(line)
        if m:
            n = int(m.group(1))
        else:
            m = Q_NUMBER.match(line)
            if m and any("?" in ln for _, ln in lines[i:i + LOOK]):
                n = int(m.group(1))
        if n is not None and expected <= n <= expected + 1:
            start("clause", f"Q{n}", line, pno)
            if n > expected:
                cur["notes"].append(f"gap before Q{n}")
            expected = n + 1
            continue
        if cur is None or cur["kind"] == "toc":
            unnumbered += 1
            start("unnumbered", f"_unnumbered:{unnumbered}", line, pno)
        else:
            cur["lines"].append(line)
            cur["page_end"] = pno
    return [Clause(source=Path(path).name, ref=c["ref"], section="", number=c["ref"] if c["kind"] == "clause" else "",
                   heading=c["lines"][0][:160], text=normalise(" ".join(c["lines"])), page_start=c["page_start"],
                   page_end=c["page_end"], kind=c["kind"], notes=c["notes"]) for c in clauses], body, dropped
