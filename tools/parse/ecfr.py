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
INLINE = re.compile(r"^([A-Z][^()]{0,100}?\.)\s+\((\d{1,2})\)\s*")


LETTER_BEFORE = {"i": "h", "v": "u", "x": "w", "l": "k"}


def level(mark, stack):
    """eCFR nesting: (a) -> (1) -> (i) -> (A).

    i, v, x and l are ambiguous: a letter right after (h), (u), (w) or (k) at letter level, otherwise a roman
    numeral under the current number. Longer roman marks (ii, iv) are always roman.
    """
    if mark.isdigit():
        return 1
    if mark.isupper():
        return 3
    if ROMAN.match(mark):
        if len(mark) > 1:
            return 2
        last_letter = next((mk for lv, mk in reversed(stack) if lv == 0), None)
        if last_letter == LETTER_BEFORE.get(mark):
            return 0
        return 2 if any(lv == 1 for lv, _ in stack) else 0
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
            heads = []
            if marks and (h := INLINE.match(rest)):  # "(c) Labeling. (1) In order to ..." opens (c) and (c)(1)
                heads.append(len(marks))
                marks.append(h.group(2))
                rest = rest[h.end():]
            if not marks:
                if current is None:
                    current = clauses[-1]
                current.text = normalise(current.text + " " + txt)
                continue
            pos = 0                                 # split txt so parent and child texts do not overlap
            for k, mark in enumerate(marks):
                lvl = level(mark, stack)
                while stack and stack[-1][0] >= lvl:
                    stack.pop()
                stack.append((lvl, mark))
                if k < len(marks) - 1:              # an outer level opened in the same paragraph gets its own clause
                    end = txt.index(f"({marks[k + 1]})", pos + len(mark) + 2)
                    head_text = txt[pos:end].strip()
                    pos = end
                    ref = num + "".join(f"({mk})" for _, mk in stack)
                    clauses.append(Clause(source=Path(path).name, ref=ref, section="", number=ref,
                                          heading=head_text[:160], text=head_text, page_start=0, page_end=0,
                                          kind="clause"))
            ref = num + "".join(f"({mk})" for _, mk in stack)
            body = txt[pos:].strip()
            current = Clause(source=Path(path).name, ref=ref, section="", number=ref, heading=body[:160], text=body,
                             page_start=0, page_end=0, kind="clause")
            clauses.append(current)
    return clauses, body_chars, 0
