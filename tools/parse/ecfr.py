"""Parser for eCFR XML (21 CFR parts). Each section paragraph becomes a clause: "211.68(b)", "211.42(c)(10)".

The paragraph markers (a), (1), (i), (A) give the nesting. A paragraph without a marker continues the previous one.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, normalise  # noqa: E402

MARK = re.compile(r"^\(([a-z]{1,2}|\d{1,2}|[ivxl]{1,5}|[A-Z])\)\s*")
ROMAN = re.compile(r"^[ivxl]+$")


def level(mark, stack):
    """eCFR nesting: (a) -> (1) -> (i) -> (A). Single letters i, v, x are roman only directly under a number."""
    if mark.isdigit():
        return 1
    if mark.isupper():
        return 3
    if ROMAN.match(mark) and stack and (stack[-1][0] >= 1 or (mark not in ("i", "v", "x") or len(stack) > 1)):
        if len(stack) >= 2 or (stack and stack[-1][0] == 1):
            return 2
    return 0


def text_of(el):
    return normalise("".join(el.itertext()))


def parse(path):
    root = ET.parse(path).getroot()
    clauses, body_chars = [], 0
    for sec in root.iter("DIV8"):
        num = sec.get("N")
        head = sec.find("HEAD")
        title = text_of(head) if head is not None else num
        stack = []          # [(level, mark)]
        current = None
        clauses.append(Clause(source=Path(path).name, ref=num, section="", number=num, heading=title, text=title,
                              page_start=0, page_end=0, kind="clause"))
        body_chars += len(title.replace(" ", ""))
        for p in sec.findall("P"):
            txt = text_of(p)
            if not txt:
                continue
            body_chars += len(txt.replace(" ", ""))
            marks, rest = [], txt
            while (m := MARK.match(rest)):          # "(a)(1) ..." can open two levels at once
                marks.append(m.group(1))
                rest = rest[m.end():]
            if not marks:
                if current is None:
                    current = clauses[-1]
                current.text = normalise(current.text + " " + txt)
                continue
            for mark in marks:
                lvl = level(mark, stack)
                while stack and stack[-1][0] >= lvl:
                    stack.pop()
                stack.append((lvl, mark))
            ref = num + "".join(f"({mk})" for _, mk in stack)
            current = Clause(source=Path(path).name, ref=ref, section="", number=ref, heading=txt[:160], text=txt,
                             page_start=0, page_end=0, kind="clause")
            clauses.append(current)
    return clauses, body_chars
