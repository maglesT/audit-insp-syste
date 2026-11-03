"""CDSCO risk-based inspection checklist (circular 2024-03): extraction from the PDF's own table structure (D52).

  python3 tools/extract/cdsco.py write     # library/extract/<file>.json + docs/extract/<file>.md
  python3 tools/extract/cdsco.py check     # re-extract and compare with the stored file (CI)

Part 1 (PDF pages 23-74) is the checklist: No. | Reference | Question | Observations | Rating. Part 2 (pages
77-142) prints the same questions again, typeset separately, with sample observations; it is used only as an
independent cross-check, never as content.

Rules (all deterministic, each counted in the report):
- a row is a question when its first cell is a number like 4.18 or 4.17.1 and the row has the five part-1 cells;
- cells are assigned to columns by position on the page (a cell reaching past x=200 is the question; one starting
  past x=100 the reference; else the number), not by their order in the structure;
- text rows at the top of a page before any question or heading continue the last question (page breaks);
  a text row of its own mid-page is a question with no printed number (flagged for review);
- a section heading is a lone cell like "4 Water & Compressed air system: -";
- a numbered row with no reference whose text ends in ":" or ":-" is a sub-heading, not a question;
- the PDF prints numbers rounded to one decimal (39.11 as "39.1"): a printed X.Y that is the half-up rounding
  of the next number in its section is restored; both numbers are kept;
- a number the PDF prints for two questions (11.11) is kept and flagged; the second gets the id "11.11#2";
- Symbol-font bullets become dashes and bullets (`tagged.GLYPHS`).
Every question keeps the text exactly as printed (whitespace collapsed).
"""
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extract"))
import tagged  # noqa: E402

SOURCE = "india-cdsco-circ-2024-03-risk-based-inspection.pdf"
PART1 = range(23, 75)
PART2_FROM = 77
OUT_JSON = ROOT / "library" / "extract" / (SOURCE + ".json")
OUT_MD = ROOT / "docs" / "extract" / (SOURCE + ".md")

NUMBER = re.compile(r"^\d{1,2}\.\d{1,2}(\.\d)?$")
HEADING = re.compile(r"^\d{1,2}\.?\s*[A-Za-z]")


def clean(text):
    return re.sub(r"\s+", " ", tagged.fix_glyphs(text)).strip()


def column(box):
    if box[2] > 200:
        return "question"
    return "reference" if box[0] > 100 else "no"


def restore_number(printed, prev):
    """The PDF rounds X.YY to one decimal; return the true number when `printed` is the rounding of prev+1."""
    if not prev or printed.count(".") != 1:
        return printed
    section, last = prev
    x, y = printed.split(".")
    nxt = last + 1
    if x != section or int(y) == nxt or nxt < 10:
        return printed
    rounded = Decimal(f"{section}.{nxt:02d}").quantize(Decimal("0.1"), ROUND_HALF_UP)
    return f"{section}.{nxt}" if str(rounded) == printed else printed


def build(pages):
    items, section = [], ""
    for page in pages:
        if page["page"] not in PART1:
            continue
        started = False
        for row in page["rows"]:
            cells = [c for c in row if c["text"].strip() and c["box"]]
            if not cells:
                continue
            first = clean(cells[0]["text"])
            if NUMBER.match(first) and len(row) == 5:
                item = {"no": "", "reference": "", "question": ""}
                for c in cells:
                    key = column(c["box"])
                    item[key] = (item[key] + " " + clean(c["text"])).strip()
                item.update(page=page["page"], printed_no=item["no"], section=section, flags=[])
                items.append(item)
                started = True
            elif len(cells) == 1 and HEADING.match(first) and len(first) < 80 and cells[0]["box"][0] < 180:
                section, started = first, True
            elif page["page"] == PART1[0]:
                continue  # the site-details form above the checklist
            elif not started and items:
                for c in cells:
                    key = column(c["box"])
                    items[-1][key] = (items[-1][key] + " " + clean(c["text"])).strip()
                items[-1]["flags"].append(f"continues on page {page['page']}")
            else:
                items.append({"no": "", "reference": "", "question": " ".join(clean(c["text"]) for c in cells),
                              "page": page["page"], "printed_no": "", "section": section,
                              "flags": ["no number printed"]})
    prev = None
    for item in items:
        if not item["reference"] and item["no"] and item["question"].endswith((":", ":-")) and len(item["question"]) < 60:
            item["flags"].append("sub-heading, not a question")
        if item["printed_no"]:
            true = restore_number(item["printed_no"], prev)
            if true != item["printed_no"]:
                item["no"] = true
                item["flags"].append(f"number printed rounded as {item['printed_no']}")
            if item["no"].count(".") == 1:
                prev = (item["no"].split(".")[0], int(item["no"].split(".")[1]))
    questions = [i for i in items if "sub-heading, not a question" not in i["flags"]]
    seen = {}
    for q in questions:
        base = q["no"] or f"p{q['page']}-unnumbered"
        seen[base] = seen.get(base, 0) + 1
        q["id"] = base if seen[base] == 1 else f"{base}#{seen[base]}"
    for q in questions:
        if q["no"] and seen.get(q["no"], 0) > 1:
            q["flags"].append("the PDF prints this number for more than one question")
    return questions, items


def _key(text):
    return re.sub(r"\W+", "", text).lower()


def cross_check(questions, pages):
    """Compare each question with its separately typeset copy in part 2."""
    copy = []
    for page in pages:
        if page["page"] < PART2_FROM:
            continue
        for row in page["rows"]:
            if row and NUMBER.match(row[0]["text"].strip()) and len(row) >= 6:
                copy.append((clean(row[0]["text"]), clean(row[2]["text"])))
    used, result = set(), []
    for q in questions:
        free = [j for j in range(len(copy)) if j not in used]
        best = max(free, key=lambda j: SequenceMatcher(None, _key(q["question"]), _key(copy[j][1])).ratio()
                   + (0.5 if copy[j][0] == q["no"] else 0))
        ratio = SequenceMatcher(None, _key(q["question"]), _key(copy[best][1])).ratio()
        if ratio < 0.6 and copy[best][0] != q["no"]:
            result.append({"no": q["no"], "status": "no counterpart"})
            continue
        used.add(best)
        if copy[best][0] != q["no"]:
            status = "number differs"
        elif _key(q["question"]) == _key(copy[best][1]):
            status = "exact"
        else:
            status = "wording differs"
        result.append({"no": q["no"], "status": status, "part2_no": copy[best][0], "part2_question": copy[best][1]})
    return result


def extract():
    pages = tagged.read_rows(ROOT / "sources" / "official" / SOURCE)
    questions, _ = build(pages)
    checks = cross_check(questions, pages)
    for q, c in zip(questions, checks):
        q["cross_check"] = c["status"]
        if c["status"] == "wording differs":
            q["part2_question"] = c["part2_question"]
    leftover = {p["page"]: clean(p["outside"]) for p in pages if p["page"] in PART1}
    stray = {pg: t for pg, t in leftover.items()
             if re.sub(r"Risk Based Joint Inspection Report Page \d+ of 55", "", t).strip()}
    counts = {}
    for q in questions:
        counts[q["cross_check"]] = counts.get(q["cross_check"], 0) + 1
    report = {"questions": len(questions), "cross_check": counts,
              "numbers_restored": sum(1 for q in questions if any(f.startswith("number printed") for f in q["flags"])),
              "page_break_joins": sum(1 for q in questions for f in q["flags"] if f.startswith("continues")),
              "text_outside_cells": stray}
    return {"source": SOURCE, "method": "tagged PDF structure (D52)", "report": report, "questions": questions}


def markdown(data):
    r = data["report"]
    lines = [f"# Extraction: {data['source']}", "", f"Method: {data['method']}; tool `tools/extract/cdsco.py`.", "",
             f"- Questions: {r['questions']}",
             f"- Cross-check against the part-2 copy: {r['cross_check']}",
             f"- Numbers restored (printed rounded): {r['numbers_restored']}",
             f"- Page-break joins: {r['page_break_joins']}",
             f"- Text outside table cells on checklist pages (besides running headers): {r['text_outside_cells']}",
             "", "## Needs the owner's review", ""]
    for q in data["questions"]:
        if q["cross_check"] == "no counterpart":
            lines.append(f"- p{q['page']} {q['no'] or '(no number)'} | {q['reference'] or '-'} | {q['question']}")
    lines += ["", "## Wording differs from the part-2 copy (part 1 kept as printed)", ""]
    for q in data["questions"]:
        if q["cross_check"] == "wording differs":
            lines.append(f"- {q['no']}: part 1 \"{q['question']}\" / part 2 \"{q['part2_question']}\"")
    return "\n".join(lines) + "\n"


def main(argv):
    if not argv or argv[0] not in ("write", "check"):
        print(__doc__)
        return 2
    data = extract()
    if argv[0] == "write":
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        OUT_MD.write_text(markdown(data))
        print(json.dumps(data["report"], ensure_ascii=False))
        return 0
    stored = json.loads(OUT_JSON.read_text())
    if stored != json.loads(json.dumps(data, ensure_ascii=False)):
        print("library extract differs from a fresh extraction; run: python3 tools/extract/cdsco.py write")
        return 1
    print("cdsco extract current")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
