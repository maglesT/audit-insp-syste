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
INLINE = re.compile(r"^([A-Z][^()]{0,160}?(?:[.?]\s+|—))\((\d{1,2}|[a-z]|[A-Z])\)\s*")


LETTER_BEFORE = {"i": "h", "v": "u", "x": "w", "l": "k"}


def level(mark, stack, italic=False):
    """eCFR nesting: (a) -> (1) -> (i) -> (A), then the italic levels (a) -> (1) -> (i) as in
    314.81(b)(2)(vii)(a)(8)(i). The XML marks italic markers ("(<I>a</I>)"): italic letter = 4, number = 5, roman = 6.

    i, v, x and l are ambiguous: a letter right after (h), (u), (w) or (k) at the same level, otherwise a roman
    numeral under the current number. Longer roman marks (ii, iv) are always roman.
    """
    if italic:
        if mark.isdigit():
            return 5
        if ROMAN.match(mark) and (len(mark) > 1 or any(lv == 5 for lv, _ in stack)) and not (
                next((mk for lv, mk in reversed(stack) if lv == 4), None) == LETTER_BEFORE.get(mark)):
            return 6
        return 4
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


def _pieces(el, italic=False):
    yield el.text or "", italic
    for child in el:
        yield from _pieces(child, italic or child.tag == "I")
        yield child.tail or "", italic


def italic_flags(p, marks):
    """For each marker (in order of appearance), whether the XML prints it in italics: "(ii)(<I>a</I>)"."""
    raw, mask = "", []
    for text, italic in _pieces(p):
        raw += text
        mask += [italic] * len(text)
    flags, pos = [], 0
    for mark in marks:
        at = raw.find(f"({mark})", pos)
        if at < 0:
            at = raw.find(mark, pos)
            flags.append(at >= 0 and mask[at])
            continue
        flags.append(mask[at + 1])
        pos = at + len(mark) + 2
    return flags


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
            italic = italic_flags(p, marks)
            pos = 0                                 # split txt so parent and child texts do not overlap
            for k, mark in enumerate(marks):
                lvl = level(mark, stack, italic=italic[k])
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
