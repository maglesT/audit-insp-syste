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
MAX_OUTSIDE = 0.10      # share of obligation sentences allowed in unnumbered segments before a source is flagged


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


def flags(rep):
    """Why a source needs a look (empty list: it does not)."""
    why = []
    if rep["duplicate_refs"]:
        why.append("duplicate references")
    if rep["large"]:
        why.append("large clauses")
    if rep["obligations"] and rep["obligations_outside_numbered"] > MAX_OUTSIDE * rep["obligations"]:
        why.append("obligations outside citable clauses")
    if rep["missed_obligations"]:
        why.append("possible misses")
    if rep["assigned_share"] < 1.0:
        why.append("text not assigned")
    if rep.get("restarts") and rep["source"].endswith(".xml"):
        why.append("numbering restarts")             # the eCFR structure is explicit: a restart is a parse error
    return why


def explanations():
    path = common.ROOT / "library" / "parse-explanations.csv"
    if not path.exists():
        return {}
    return {r["source"]: r["explanation"] for r in csv.DictReader(open(path, encoding="utf-8"))}


def write_report(results, pending):
    """library/parse-report.md from the results, with the written explanation of every flagged source."""
    notes = explanations()
    for r in results:
        r["flags"] = flags(r)
        r["flag"] = bool(r["flags"])
        r["explanation"] = notes.get(r["source"], "")
    unexplained = [r["source"] for r in results if r["flag"] and not r["explanation"]]
    lines = ["# Parse report (S1)", "",
             "Generated by `tools/parse/run.py` (`--report` re-renders it from `parse-report.json` without parsing).",
             "",
             f"Totals: {len(results)} sources, {sum(r['clauses'] for r in results)} clauses "
             f"({sum(r['table_rows'] for r in results)} table rows), {sum(r['obligations'] for r in results)} "
             f"obligation sentences, {sum(len(r['missed_obligations']) for r in results)} possibly missed. "
             f"Flagged: {sum(r['flag'] for r in results)}; flagged without a written explanation: {len(unexplained)}.",
             "",
             "A flag means the source needs a look: duplicate references; clauses over 4,000 characters (FDA guidance "
             "sections: 15,000); more than 10 % of the obligation sentences outside citable clauses; obligation "
             "sentences that an independent second extraction (`pdftotext -raw`, `tools/parse/crosscheck.py`) finds "
             "but the parse does not (possible misses); or text not assigned to any clause. Restarts = clauses whose "
             "numbering starts again (references with \"#2\"; each carries a note naming the heading it follows). "
             "Explanations are kept in `library/parse-explanations.csv`.",
             "",
             "| Source | Clauses | Table rows | Restarts | Numbered share | Obligations | Outside | Missed | Flags "
             "| Explanation |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: (not r["flag"], r["source"])):
        lines.append(f"| {r['source']} | {r['clauses']} | {r['table_rows']} | {r.get('restarts', 0)} "
                     f"| {r['numbered_share']:.2f} | {r['obligations']} | {r['obligations_outside_numbered']} "
                     f"| {len(r['missed_obligations'])} | {', '.join(r['flags'])} | {r['explanation']} |")
    if pending:
        lines += ["", f"Pending (no parser yet): {', '.join(pending)}."]
    (common.ROOT / "library" / "parse-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = common.ROOT / "library" / "parse-report.json"
    out.write_text(json.dumps({"parsed": results, "pending": pending}, indent=1), encoding="utf-8")
    return unexplained


def main():
    if "--report" in sys.argv:
        data = json.loads((common.ROOT / "library" / "parse-report.json").read_text(encoding="utf-8"))
        unexplained = write_report(data["parsed"], data["pending"])
        print(f"report written; {len(unexplained)} flagged sources without explanation: {', '.join(unexplained)}")
        return
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
        rep["restarts"] = sum(1 for c in clauses if any(n.startswith("restart:") for n in c.notes))
        obl = obligations.extract(clauses)
        rep["obligations"] = len(obl)
        rep["obligations_outside_numbered"] = sum(1 for o in obl if o["ref"].startswith("_"))
        rep["missed_obligations"] = crosscheck.missed_obligations(common.OFFICIAL / row["file"], clauses)
        write_jsonl(common.ROOT / "library" / "obligations" / (Path(row["file"]).stem + ".jsonl"), obl)
        results.append(rep)
    unexplained = write_report(results, pending)
    print(f"parsed {len(results)} sources, {sum(r['clauses'] for r in results)} clauses, "
          f"{sum(r['flag'] for r in results)} flagged, {len(unexplained)} without explanation, {len(pending)} pending")


if __name__ == "__main__":
    main()
