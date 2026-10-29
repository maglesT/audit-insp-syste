"""Parser for eCFR XML (21 CFR parts). Each section paragraph becomes a clause: "211.68(b)", "211.42(c)(10)".

The paragraph markers (a), (1), (i), (A) give the nesting. A paragraph without a marker continues the previous one.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, normalise, resolve_duplicates  # noqa: E402

MARK = re.compile(r"^\(([a-z]{1,2}|\d{1,2}|[ivxl]{1,5}|[A-Z])\)\s*")
ROMAN = re.compile(r"^[ivxl]+$")
INLINE = re.compile(r"^([A-Z][^()]{0,160}?(?:\.\s+|—))\((\d{1,2}|[a-z]|[A-Z])\)\s*")


LETTER_BEFORE = {"i": "h", "v": "u", "x": "w", "l": "k"}


def level(mark, stack):
    """eCFR nesting: (a) -> (1) -> (i) -> (A); below a roman numeral, lettered sub-items (level 4), then italic
    numbers (5) and italic romans (6), as in 314.81(b)(2)(vii)(a)(8)(i).

    i, v, x and l are ambiguous: a letter right after (h), (u), (w) or (k) at letter level, otherwise a roman
    numeral under the current number. Longer roman marks (ii, iv) are always roman.
    """
    if mark.isdigit():
        # an italic number below a lettered sub-item or a capital: 314.81(b)(2)(vii)(a)(1), (b)(3)(v)(A)(1)
        if any(lv in (3, 4) for lv, _ in stack):
            italic = next((mk for lv, mk in reversed(stack) if lv == 5), None)
            if mark == "1" or (italic is not None and int(mark) == int(italic) + 1):
                return 5
        return 1
    if mark.isupper():
        return 3
    if ROMAN.match(mark):
        if stack and stack[-1][0] in (5, 6) and (mark == "i" or stack[-1][0] == 6):
            return 6                                # an italic roman below an italic number: ...(a)(8)(i)
        if len(mark) > 1:
            return 2
        last_letter = next((mk for lv, mk in reversed(stack) if lv == 0), None)
        if last_letter == LETTER_BEFORE.get(mark):
            return 0
        return 2 if any(lv == 1 for lv, _ in stack) else 0
    if len(mark) == 1 and any(lv >= 2 for lv, _ in stack):
        # A letter below a roman numeral, e.g. 314.81(b)(2)(ii)(a): a sub-item, unless it is the next top-level
        # paragraph and no sub-item list is open whose next letter it would be.
        deep = next((mk for lv, mk in reversed(stack) if lv == 4), None)
        if deep is not None and ord(mark) == ord(deep) + 1:
            return 4
        last_letter = next((mk for lv, mk in reversed(stack) if lv == 0), None)
        if last_letter is None or ord(mark) != ord(last_letter) + 1:
            return 4
    return 0


def defined_term(p):
    """The term of a definition paragraph: it opens with the term in italics (<P><I>Term</I> means ...)."""
    if (p.text or "").strip() or not len(p) or p[0].tag != "I":
        return None
    term = normalise("".join(p[0].itertext())).rstrip(".,:")
    return term if 0 < len(term) <= 80 else None


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
        current, prefix, definitions_base, item = None, num, [], 0
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
                term = defined_term(p)
                if term:
                    # an unmarked definition ("<I>Foreign</I> for the purposes of ...", 207.1): its own clause under
                    # the paragraph it sits in; "(1)", "(2)" ... in sequence nest below it
                    if prefix == num:
                        definitions_base = list(stack)
                    prefix = num + "".join(f"({mk})" for _, mk in definitions_base) + f' "{term}"'
                    stack, item = [], 0
                    current = Clause(source=Path(path).name, ref=prefix, section="", number=prefix,
                                     heading=txt[:160], text=txt, page_start=0, page_end=0, kind="clause")
                    clauses.append(current)
                    continue
                if current is None:
                    current = clauses[-1]
                current.text = normalise(current.text + " " + txt)
                continue
            if prefix != num:                       # inside a run of definitions
                if len(marks) == 1 and marks[0].isdigit() and int(marks[0]) == item + 1:
                    item += 1
                else:                               # anything else ends the run
                    prefix, stack = num, list(definitions_base)
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
                    ref = prefix + "".join(f"({mk})" for _, mk in stack)
                    clauses.append(Clause(source=Path(path).name, ref=ref, section="", number=ref,
                                          heading=head_text[:160], text=head_text, page_start=0, page_end=0,
                                          kind="clause"))
            ref = prefix + "".join(f"({mk})" for _, mk in stack)
            body = txt[pos:].strip()
            current = Clause(source=Path(path).name, ref=ref, section="", number=ref, heading=body[:160], text=body,
                             page_start=0, page_end=0, kind="clause")
            clauses.append(current)
    return resolve_duplicates(clauses), body_chars, 0
