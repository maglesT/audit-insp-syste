"""Parser for documents organised in numbered paragraphs (EudraLex, PIC/S, WHO TRS, ICH, Schedule M).

A line starts a clause when it begins with a number like "4.9", "10.5." or "2.10" AND that number is a
plausible successor of the previous clause in the same section: the next sibling, the first child, or the next
number at a higher level. This rejects numbers that appear inside text ("2.5 mg", list items). Single numbers
("3.") count only when the line looks like a heading. Section markers ("PART II", "ANNEX 1") reset numbering.
A run of numbers that restarts at 1 is treated as a table of contents if the same numbers appear again later.
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Clause, english_page, normalise, pdf_pages, repeated_lines  # noqa: E402

NUM = re.compile(r"^(\d{1,2}(?:\.\d{1,3}){0,4})\.?(?=\s|$)\s*(.*)$")
SECTION = [
    (re.compile(r"^PART[\s-]+([IVXL]+)\b"), "Part {}"),
    (re.compile(r"^ANNEX\s+(\d+[A-Z]?)\*?\s*$", re.I), "Annex {}"),
    (re.compile(r"^CHAPTER\s+(\d+)\b"), "Chapter {}"),
]
PRINCIPLE = re.compile(r"^(Principles?|PRINCIPLES?)\.?\s*$")
BACK_MATTER = re.compile(r"^(\d{1,2}\.?\s+)?(Glossary|GLOSSARY|Definitions|DEFINITIONS|Abbreviations|ABBREVIATIONS|References|REFERENCES|Bibliography|Appendix\b.*|APPENDIX\b.*)\s*$")
MAX_GAP = 3


def parse_number(s):
    return [int(x) for x in s.split(".")]


def plausible(prev, cand):
    """Is cand a plausible next clause number after prev? Returns (ok, gap)."""
    if prev is None:
        return cand[-1] <= MAX_GAP, False
    for k in range(len(prev), 0, -1):          # next number at level k (sibling or higher)
        head = prev[:k - 1]
        if cand[:k - 1] == head and len(cand) >= k:
            step = cand[k - 1] - prev[k - 1]
            rest = cand[k:]
            if 1 <= step <= MAX_GAP and all(x == 1 for x in rest):
                return True, step > 1
    if cand[:len(prev)] == prev and len(cand) == len(prev) + 1 and cand[-1] == 1:   # first child
        return True, False
    # ICH Q7 style decimals: heading 2.1, paragraphs 2.10, 2.11 ..., next heading 2.2, paragraphs 2.20 ...
    if len(cand) == len(prev) and cand[:-1] == prev[:-1]:
        p, c = prev[-1], cand[-1]
        if 1 <= p <= 9 and c == p * 10:
            return True, False
        if p >= 10 and c in (p // 10 + 1, (p // 10 + 1) * 10):
            return True, False
    return False, False


def heading_like(rest):
    rest = rest.strip()
    return bool(rest) and len(rest) < 90 and not rest.endswith((".", ";", ",", ":"))


def parse(path):
    pages = pdf_pages(path)
    english = [english_page(p) for p in pages]
    noise = repeated_lines([p for p, e in zip(pages, english) if e])
    clauses, cur, section, prev = [], None, "", None
    seen_in_section, unnumbered, run = set(), 0, 0
    body_chars = 0

    def start(kind, ref, number, line, page):
        nonlocal cur
        cur = {"kind": kind, "ref": ref, "section": section, "number": number, "run": run,
               "lines": [line], "page_start": page, "page_end": page, "notes": []}
        clauses.append(cur)

    lines = []
    for pno, (page, is_en) in enumerate(zip(pages, english), start=1):
        if not is_en:
            continue
        for raw in page.splitlines():
            line = raw.strip()
            if not line or re.sub(r"\d+", "#", line) in noise or re.fullmatch(r"[-–—\s\d]+", line):
                continue
            lines.append((pno, line))

    def child_follows(i, top):
        """A single number like "10." is a heading only if the next multi-part number below it is 10.x."""
        for _, nxt in lines[i + 1:i + 80]:
            mm = NUM.match(nxt)
            if mm and "." in mm.group(1):
                return mm.group(1).split(".")[0] == str(top)
        return False

    for i, (pno, line) in enumerate(lines):
        if True:
            body_chars += len(line.replace(" ", ""))
            sec = next((fmt.format(m.group(1)) for rx, fmt in SECTION if (m := rx.match(line))), None)
            if sec and sec.startswith("Chapter") and section.startswith(("Annex", "Part")):
                sec = None   # a chapter heading inside an annex or part does not restart numbering
            if sec:
                section, prev, seen_in_section = sec, None, set()
                unnumbered += 1
                start("unnumbered", f"_unnumbered:{unnumbered}", "", line, pno)
                continue
            if BACK_MATTER.match(line):
                unnumbered += 1
                start("unnumbered", f"_unnumbered:{unnumbered}", "", line, pno)
                prev, run, seen_in_section = None, run + 1, set()
                continue
            if PRINCIPLE.match(line):
                ref = f"{section} Principle".strip()
                start("principle", ref, "", line, pno)
                continue
            m = NUM.match(line)
            if m:
                num, rest = m.group(1), m.group(2)
                cand = parse_number(num)
                ok, gap = plausible(prev, cand)
                restart = (not ok and cand in ([1], [1, 1]) and heading_like(rest)
                           and tuple(cand) in seen_in_section)
                upper = sum(ch.isupper() for ch in rest) >= 0.8 * max(1, sum(ch.isalpha() for ch in rest))
                single_run = (prev is None and cand == [1]) or (prev is not None and len(prev) == 1
                                                                 and cand == [prev[0] + 1])
                follows = len(cand) == 1 and child_follows(i, cand[0])
                as_heading = heading_like(rest) and (follows or upper)
                as_paragraph = single_run and not follows
                if len(cand) == 1 and not (as_heading or as_paragraph):
                    ok = restart = False
                if ok or restart:
                    if restart:   # numbering starts again: one of the runs is a table of contents
                        run += 1
                        seen_in_section = set()
                    ref = f"{section} {num}".strip()
                    start("clause", ref, num, line, pno)
                    if gap:
                        cur["notes"].append(f"gap before {num} (previous {'.'.join(map(str, prev))})")
                    prev = cand
                    seen_in_section.add(tuple(cand))
                    continue
            if cur is None:
                unnumbered += 1
                start("unnumbered", f"_unnumbered:{unnumbered}", "", line, pno)
            else:
                cur["lines"].append(line)
                cur["page_end"] = pno

    # Where numbering restarted inside a section, keep the run with the most text; the others are contents lists.
    runs = {}
    for c in clauses:
        if c["kind"] == "clause":
            key = (c["section"], c["run"])
            runs[key] = runs.get(key, 0) + sum(len(x) for x in c["lines"])
    best = {}
    for (sec, r), size in runs.items():
        if sec not in best or size > runs[(sec, best[sec])]:
            best[sec] = r
    count = {}
    for c in clauses:
        if c["kind"] == "clause":
            count[(c["section"], c["run"])] = count.get((c["section"], c["run"]), 0) + 1
    for c in clauses:
        key = (c["section"], c["run"])
        if c["kind"] == "clause" and best.get(c["section"]) != c["run"] and runs[key] / count[key] < 250:
            c["kind"] = "toc"
    out = []
    for c in clauses:
        out.append(Clause(source=Path(path).name, ref=c["ref"] if c["kind"] != "toc" else f"_toc:{c['ref']}",
                          section=c["section"], number=c["number"], heading=c["lines"][0][:160],
                          text=normalise(" ".join(c["lines"])), page_start=c["page_start"],
                          page_end=c["page_end"], kind=c["kind"], notes=c["notes"]))
    return out, body_chars
