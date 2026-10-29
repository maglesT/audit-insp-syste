"""Parse every pilot source into clauses and write a completeness report (S1).

  python3 tools/parse/run.py            # writes library/clauses/*.jsonl and library/parse-report.md

Scope: pilot regulators, priority must/should. Parsers: eCFR XML (ecfr.py), fda.gov HTML (fdahtml.py), the EMA
Q&A page (emahtml.py), FDA PDFs (headings.py), all other PDFs (numbered.py, or qa.py / articles.py when they fit
better, see text_parser); tables in PDFs are read by tables.py. A file no parser handles is listed as "pending".
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import crosscheck  # noqa: E402
import obligations  # noqa: E402
import ecfr  # noqa: E402
import emahtml  # noqa: E402
import fdahtml  # noqa: E402
import headings  # noqa: E402
import numbered  # noqa: E402
import tables  # noqa: E402
import articles  # noqa: E402
import qa  # noqa: E402

PILOT = {"FDA", "EU", "EMA", "PICS", "WHO", "INDIA", "ICH"}
LARGE = 4000            # characters; a clause this long probably swallowed the next ones
LARGE_SECTION = 15000   # FDA texts: a clause is a whole section (heading to heading), so the limit is larger
MIN_NUMBERED = 0.80     # share of body text inside numbered clauses


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


ALTERNATIVE_GAIN = 0.05   # an alternative text parser must cover this much more of the text than the numbered one


def usable_share(result):
    """Share of the body text in citable clauses that can be cited as they are: a unique reference and at most
    LARGE characters. One oversized clause (a Q&A answer that swallowed the rest of a guideline) or duplicate
    references then cannot make a parse look good."""
    clauses, body, _ = result
    refs = [c.ref for c in clauses if c.kind in common.CITABLE]
    dup = {r for r in refs if refs.count(r) > 1}
    good = sum(len(c.text.replace(" ", "").replace("|", "")) for c in clauses
               if c.kind in common.CITABLE and c.ref not in dup and len(c.text) <= LARGE)
    return good / body if body else 0.0


def text_parser(path, pages=None):
    """Numbered parser by default; the Q&A or the article parser when it finds at least 2 clauses of its own kind
    (Q<n> / Article <n>) and puts at least ALTERNATIVE_GAIN more of the text into usable clauses (usable_share).
    Deterministic: same input, same choice. The choice is noted on the first clause."""
    best = numbered.parse(path, pages=pages)
    best_share, name = usable_share(best), "numbered"
    for alt, prefix in ((qa, "Q"), (articles, "Article ")):
        result = alt.parse(path, pages=pages)
        own = sum(1 for c in result[0] if c.kind == "clause" and c.ref.startswith(prefix))
        share = usable_share(result)
        if own >= 2 and share >= best_share + ALTERNATIVE_GAIN:
            best, best_share, name = result, share, alt.__name__
    if name != "numbered" and best[0]:
        best[0][0].notes.append(f"parser: {name}")
    return best


def parser_for(row):
    f = row["file"]
    if f.endswith(".xml"):
        return ecfr.parse
    if f.endswith(".html"):
        return {"FDA": fdahtml.parse, "EMA": emahtml.parse}.get(row["regulator"])
    if row["regulator"] == "FDA":
        return lambda path: tables.parse(path, headings.parse)
    return lambda path: tables.parse(path, text_parser)


def main():
    rows = [r for r in csv.DictReader(open(common.ROOT / "sources" / "catalog.csv", encoding="utf-8"))
            if r["regulator"] in PILOT and r["priority"] in ("must", "should") and r["phase"] == "pilot"]
    results, pending = [], []
    for row in rows:
        parse = parser_for(row)
        if parse is None:
            pending.append(row["file"])
            continue
        clauses, body, dropped = parse(common.OFFICIAL / row["file"])
        common.write_clauses(row["file"], clauses)
        rep = common.report(row["file"], clauses, body, dropped)
        limit = LARGE_SECTION if row["regulator"] == "FDA" and not row["file"].endswith(".xml") else LARGE
        rep["large"] = [c.ref for c in clauses if c.kind in ("clause", "table_row") and len(c.text) > limit]
        obl = obligations.extract(clauses)
        rep["obligations"] = len(obl)
        rep["obligations_outside_numbered"] = sum(1 for o in obl if o["ref"].startswith("_"))
        rep["missed_obligations"] = crosscheck.missed_obligations(common.OFFICIAL / row["file"], clauses)
        write_jsonl(common.ROOT / "library" / "obligations" / (Path(row["file"]).stem + ".jsonl"), obl)
        rep["flag"] = bool(rep["duplicate_refs"] or rep["large"] or rep["numbered_share"] < MIN_NUMBERED
                           or rep["missed_obligations"] or rep["assigned_share"] < 1.0)
        results.append(rep)
    out = common.ROOT / "library" / "parse-report.json"
    out.write_text(json.dumps({"parsed": results, "pending": pending}, indent=1), encoding="utf-8")
    lines = ["# Parse report (S1)", "", "Generated by `tools/parse/run.py`. A flag means the source needs a look: "
             "duplicate references, clauses over 4,000 characters (FDA guidance sections: 15,000), "
             "or under 80 % of the text in numbered clauses "
             "or table rows. Table rows come from pdfplumber (`tools/parse/tables.py`), one clause per row.",
             "Obligations = sentences with shall/must/should/may wording found by NLP (`tools/parse/obligations.py`); "
             "outside = how many sit in unnumbered segments; missed = obligation sentences found by an independent "
             "second extraction (`pdftotext -raw`) but not in the parsed clauses (`tools/parse/crosscheck.py`).",
             "", "| Source | Clauses | Table rows | Numbered share | Obligations | Outside | Missed | Flag | Duplicates | Large clauses |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: (not r["flag"], r["source"])):
        lines.append(f"| {r['source']} | {r['clauses']} | {r['table_rows']} | {r['numbered_share']:.2f} | {r['obligations']} "
                     f"| {r['obligations_outside_numbered']} | {len(r['missed_obligations'])} | {'yes' if r['flag'] else ''} "
                     f"| {', '.join(r['duplicate_refs'][:5])} | {', '.join(r['large'][:5])} |")
    if pending:
        lines += ["", f"Pending (no parser yet): {', '.join(pending)}."]
    (common.ROOT / "library" / "parse-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    flagged = sum(r["flag"] for r in results)
    missed = sum(len(r["missed_obligations"]) for r in results)
    lines.insert(4, f"Totals: {len(results)} sources, {sum(r['clauses'] for r in results)} clauses, "
                    f"{sum(r['obligations'] for r in results)} obligation sentences, {missed} possibly missed.")
    (common.ROOT / "library" / "parse-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"parsed {len(results)} sources, {sum(r['clauses'] for r in results)} clauses, {flagged} flagged, "
          f"{len(pending)} pending")


if __name__ == "__main__":
    main()
