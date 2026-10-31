"""Build the owner's review page (claude.ai artifact "FDA Item Review") from the current review queue.

  python3 tools/fda/review_page/build.py OUT.html

Every item routed to "review" in the runs listed in library/fda-status.json, with its source text, the check
findings and both verifiers' verdicts and reasons, embedded as JSON into template.html. Decisions made on the
page are stored in the artifact's db collection `decisions` and imported with `tools/fda/review.py import-artifact`.
Superseded runs (SKIP_RUNS) are left out.
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import review  # noqa: E402

SKIP_RUNS = {"20261031T095248.400139Z-xml-draft"}       # the 10-section 211 trial, superseded by the full build


def queue():
    status = json.loads((ROOT / "library" / "fda-status.json").read_text())["documents"]
    with open(ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        titles = {r["file"]: r["title"] for r in csv.DictReader(f)}
    out, order = [], list(status)
    for doc, v in status.items():
        for run in v.get("runs", []):
            if run in SKIP_RUNS:
                continue
            path = ROOT / "library" / "ai-runs" / run
            if not (path / "route.json").exists():
                continue
            _, items, route = review.load(path)
            cases = {}
            vr = path / "verify-report.json"
            if vr.exists():
                cases = {c["id"]: c for c in json.loads(vr.read_text()).get("cases", [])}
            for k, r in route.items():
                if r != "review":
                    continue
                it, c = items[k], cases.get(k, {})
                out.append({"id": k, "run": run, "item_hash": review.fingerprint(it), "document": titles.get(doc, doc),
                            "file": doc, "clause": it.get("clause_number", ""), "statement": it["statement"],
                            "quote": it["quote"], "strength": it["strength"], "plant_types": it["plant_types"],
                            "condition": it.get("condition", ""), "findings": it.get("findings", []),
                            "a": c.get("a"), "a_reason": c.get("a_reason", ""), "b": c.get("b"),
                            "b_reason": c.get("b_reason", ""), "source_text": review.source_text(it)})
    num = lambda c: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", c or "")]  # noqa: E731
    out.sort(key=lambda o: (order.index(o["file"]), num(o["clause"]), o["id"]))
    return out


def main():
    items = queue()
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    page = (HERE / "template.html").read_text(encoding="utf-8").replace("__DATA__", data)
    Path(sys.argv[1]).write_text(page, encoding="utf-8")
    print(f"{len(items)} items -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
