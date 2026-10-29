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
from common import (Clause, edge_lines, english_line, english_page, normalise, pdf_pages,  # noqa: E402
                    line_key, repeated_lines, resolve_duplicates, running_lines)

NUM = re.compile(r"^([1-9]\d?(?:\.(?:0|[1-9]\d{0,2})){0,4})\.?(?=\s|$)\s*(.*)$")
SECTION = [
    (re.compile(r"^PART[\s-]+([IVXL]+)\b"), "Part {}"),
    (re.compile(r"^ANNEX\s+(\d+[A-Z]?)\*?\s*$", re.I), "Annex {}"),
    (re.compile(r"^CHAPTER\s+(\d+)\b"), "Chapter {}"),
]
PRINCIPLE = re.compile(r"^(Principles?|PRINCIPLES?)\.?\s*$")
BACK_MATTER = re.compile(r"^(\d{1,2}\.?\s+)?(Glossary|GLOSSARY|Definitions|DEFINITIONS|Abbreviations|ABBREVIATIONS|References|REFERENCES|Bibliography)\s*$")
APPENDIX = re.compile(r"^(?:Appendix|APPENDIX)\s+([0-9IVX]+|[A-Z])\b")
DOT_LEADER = re.compile(r"(\.\s?){4,}\s*\d*\s*$|\s\d{1,3}\s*$")
MAX_GAP = 3
PAGE_END = re.compile(r"(\.\s?){4,}\s*\d*\s*$|\s{3,}\d{1,3}\s*$")   # a contents entry: leaders or a page number
UNDO_LINES = 60         # stray numbers are taken back only if the old numbering resumes within this many lines
DATE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)"
                  r"\s+\d{4}\b")


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
    if len(cand) >= 2 and len(cand) == len(prev) and cand[:-1] == prev[:-1]:
        p, c = prev[-1], cand[-1]
        if 1 <= p <= 9 and c == p * 10:
            return True, False
        if p >= 10 and c in (p // 10 + 1, (p // 10 + 1) * 10):
            return True, False
    return False, False


def heading_like(rest):
    rest = rest.strip()
    return bool(rest) and len(rest) < 90 and not rest.endswith((".", ";", ",", ":"))


def parse(path, pages=None):
    """pages: text per page from another extractor (table mode); default pdftotext -layout."""
    pages = pdf_pages(path) if pages is None else pages
    english = [english_page(p) for p in pages]
    noise = repeated_lines([p for p, e in zip(pages, english) if e])
    running = running_lines([p for p, e in zip(pages, english) if e])
    clauses, cur, section, prev = [], None, "", None
    seen_in_section, unnumbered, run, jumps = set(), 0, 0, []
    body_chars = 0

    def start(kind, ref, number, line, page):
        nonlocal cur
        cur = {"kind": kind, "ref": ref, "section": section, "number": number, "run": run,
               "lines": [line], "page_start": page, "page_end": page, "notes": []}
        clauses.append(cur)

    lines, dropped = [], 0
    for pno, (page, is_en) in enumerate(zip(pages, english), start=1):
        if not is_en:
            continue
        edges = {ln.strip() for ln in edge_lines(page)}
        for raw in page.splitlines():
            line = raw.strip()
            if not line or not english_line(line):
                continue
            masked = line_key(line)
            if masked in running or (line in edges and not line.startswith("[[TABLE ")
                                     and (masked in noise or re.fullmatch(r"[-–—\s\d]+", line))):
                dropped += len(line.replace(" ", ""))
                continue
            lines.append((pno, line))

    def next_multi(i):
        """The next multi-part number ("8.1") within 80 lines below line i, as a list; None if there is none."""
        for _, nxt in lines[i + 1:i + 80]:
            mm = NUM.match(nxt)
            if mm and "." in mm.group(1):
                return parse_number(mm.group(1))
        return None

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
            if sec and PAGE_END.search(line) and section:
                sec = None   # "ANNEX 2 .... 27" in a contents list does not change the section of what follows
            if sec and sec.startswith("Chapter") and section.startswith(("Annex", "Part")):
                sec = None   # a chapter heading inside an annex or part does not restart numbering
            if sec:
                section, prev, seen_in_section = sec, None, set()
                start("section", sec, "", line, pno)     # text under the heading, before clause 1, is citable
                continue
            ma = APPENDIX.match(line)
            if ma and heading_like(line) and not PAGE_END.search(line):
                base = re.sub(r"\s*Appendix \S+$", "", section)
                section, prev, seen_in_section = f"{base} Appendix {ma.group(1)}".strip(), None, set()
                start("section", section, "", line, pno)
                continue
            mb = BACK_MATTER.match(line)
            if mb:
                if mb.group(2).lower() in ("references", "bibliography"):
                    unnumbered += 1
                    start("unnumbered", f"_unnumbered:{unnumbered}", "", line, pno)
                else:                                  # definitions often carry "should" / "may": citable
                    start("section", f"{section} {mb.group(2).title()}".strip(), "", line, pno)
                continue
            if PRINCIPLE.match(line):
                ref = f"{section} Principle".strip()
                start("principle", ref, "", line, pno)
                continue
            m = NUM.match(line)
            if m and DATE.match(m.group(2)) and "." not in m.group(1):
                m = None                     # "1 July 2018" on a cover page is a date, not clause 1
            if m:
                num, rest = m.group(1), m.group(2)
                cand = parse_number(num)
                ok, gap = plausible(prev, cand)
                # only a single stray, or a run of single numbers ("10." to "15." of a list), is taken back: a run
                # of numbers like 17.4, 17.5 is real structure
                back = next((k for k in range(len(jumps) - 1, -1, -1) if i - jumps[k]["line"] <= UNDO_LINES
                             and plausible(jumps[k]["prev"], cand)[0]
                             and (k == len(jumps) - 1 or all("." not in j["clause"]["number"] for j in jumps[k:]))),
                            None) if not ok else None
                if back is not None and len(cand) > 1 and rest[:1].isupper():
                    # The last accepted numbers were strays (a footnote, a list "10. ... 15.", a running header, a
                    # wrapped line): the numbering goes on from before them. Take them back into the clause they
                    # interrupted.
                    first = clauses.index(jumps[back]["clause"])
                    taken = clauses[first:]
                    del clauses[first:]
                    if clauses:
                        for c in taken:
                            clauses[-1]["lines"] += c["lines"]
                        clauses[-1]["page_end"] = taken[-1]["page_end"]
                    prev = jumps[back]["prev"]
                    del jumps[back:]
                    ok, gap = plausible(prev, cand)
                restart = (not ok and cand in ([1], [1, 1]) and heading_like(rest)
                           and tuple(cand) in seen_in_section)
                upper = sum(ch.isupper() for ch in rest) >= 0.8 * max(1, sum(ch.isalpha() for ch in rest))
                single_run = (prev is None and cand == [1]) or (prev is not None and len(prev) == 1
                                                                 and cand == [prev[0] + 1])
                follows = len(cand) == 1 and child_follows(i, cand[0])
                # "8. Personnel" after 7.x: a new chapter in title case, unless the old chapter's numbering goes on
                # below it (then "8." was a list item)
                titled = (rest[:1].isupper() and prev is not None and len(prev) > 1 and cand == [prev[0] + 1]
                          and len(rest) < 70 and next_multi(i) not in (None,) and next_multi(i)[0] != prev[0])
                as_heading = heading_like(rest) and (follows or upper or titled)
                as_paragraph = single_run and not follows
                if len(cand) == 1 and not (as_heading or as_paragraph or restart):
                    ok = restart = False
                if ok or restart:
                    if restart:   # numbering starts again: one of the runs is a table of contents
                        run += 1
                        seen_in_section = set()
                    ref = f"{section} {num}".strip()
                    start("clause", ref, num, line, pno)
                    if gap:
                        cur["notes"].append(f"gap before {num} (previous {'.'.join(map(str, prev))})")
                    if prev is not None:
                        jumps.append({"line": i, "prev": prev, "clause": cur})
                        jumps[:] = [j for j in jumps if i - j["line"] <= UNDO_LINES]
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
    # A run counts as a contents list only on positive evidence: its numbers appear again in the run that is kept,
    # and either most entries end in dot leaders or a page number, or nearly all numbers repeat and entries are short
    # (a "document map" table).
    count, leaders, numbers = {}, {}, {}
    for c in clauses:
        if c["kind"] == "clause":
            key = (c["section"], c["run"])
            count[key] = count.get(key, 0) + 1
            leaders[key] = leaders.get(key, 0) + bool(DOT_LEADER.search(c["lines"][0]))
            numbers.setdefault(key, set()).add(c["number"])
    toc_like = {}
    for key in count:
        kept = (key[0], best.get(key[0]))
        repeats = len(numbers[key] & numbers.get(kept, set())) / len(numbers[key])
        short = runs[key] / count[key] < 400
        toc_like[key] = key != kept and repeats >= 0.5 and (leaders[key] >= 0.5 * count[key]
                                                           or (repeats >= 0.8 and short))
    for c in clauses:
        key = (c["section"], c["run"])
        if c["kind"] == "clause" and best.get(c["section"]) != c["run"] and toc_like.get(key):
            c["kind"] = "toc"
    out = []
    for c in clauses:
        out.append(Clause(source=Path(path).name, ref=c["ref"] if c["kind"] != "toc" else f"_toc:{c['ref']}",
                          section=c["section"], number=c["number"], heading=c["lines"][0][:160],
                          text=normalise(" ".join(c["lines"])), page_start=c["page_start"],
                          page_end=c["page_end"], kind=c["kind"], notes=c["notes"]))
    return resolve_duplicates(out), body_chars, dropped
