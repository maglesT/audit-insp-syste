"""Review queue (D47, "nothing ships unless proven"): the human route for items the automatic route did not prove.

  python3 tools/fda/review.py next RUN                      # the next undecided item, with its source text beside it
  python3 tools/fda/review.py decide RUN ID correct --by NAME [--note TEXT]
  python3 tools/fda/review.py decide RUN ID fix --by NAME --statement TEXT [--quote TEXT] [--note TEXT]
  python3 tools/fda/review.py decide RUN ID reject --by NAME [--note TEXT]
  python3 tools/fda/review.py status RUN                    # automatic, queued, decided, shipped

The queue is every item of RUN/route.json routed to "review". Each decision is appended to
library/review/decisions.jsonl with the reviewer's name and the UTC time (attributable, never edited in place; a
later decision on the same item supersedes an earlier one). An item ships when its route is "auto", or when its
latest decision is "correct", or "fix" (with the corrected statement; a corrected quote must still be found in the
source text). Everything else does not ship.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DECISIONS = ROOT / "library" / "review" / "decisions.jsonl"


def load(run):
    run = Path(run)
    items = {i["id"]: i for i in (json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip())}
    route = json.loads((run / "route.json").read_text())["route"]
    return run, items, route


def decisions(path=DECISIONS):
    """{item id: latest decision}."""
    out = {}
    if Path(path).exists():
        for ln in Path(path).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                d = json.loads(ln)
                out[d["id"]] = d
    return out


def source_text(item):
    """The text the reviewer checks the item against: the cited XML paragraph and its sub-paragraphs, or for a page
    item its page reference (the page image is in work/vision-pages, rendered by tools/pages/vision.py)."""
    if item.get("source", "").endswith(".xml"):
        sys.path.insert(0, str(HERE))
        import xmlprofile
        ref = item["clause_number"]
        return "\n".join(f"{r}  {t}" for r, t in xmlprofile.paragraphs(item["source"])
                         if r == ref or r.startswith(ref + "(") or r == xmlprofile.parent(ref))
    return f"{item['source']} page {item.get('page')} (page image: work/vision-pages)"


def queue(run):
    run, items, route = load(run)
    return [items[k] for k, v in route.items() if v == "review"]


def shipped(run, path=DECISIONS):
    run, items, route = load(run)
    dec = decisions(path)
    return [k for k, v in route.items() if v == "auto" or dec.get(k, {}).get("decision") in ("correct", "fix")]


def decide(run, item_id, decision, by, statement=None, quote=None, note="", path=DECISIONS):
    run, items, route = load(run)
    if item_id not in items:
        raise SystemExit(f"{item_id}: not in {run}")
    if not by.strip():
        raise SystemExit("a decision needs the reviewer's name (--by)")
    if decision == "fix" and not statement:
        raise SystemExit("fix needs the corrected statement (--statement)")
    if quote:
        sys.path.insert(0, str(HERE))
        import xmlprofile
        it = dict(items[item_id], quote=quote)
        if items[item_id]["source"].endswith(".xml") and not xmlprofile.check_item(it, it["source"])[1]:
            raise SystemExit("the corrected quote is not in the source text")
    rec = {"id": item_id, "run": Path(run).name, "decision": decision, "by": by.strip(),
           "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "note": note}
    if statement:
        rec["statement"] = statement
    if quote:
        rec["quote"] = quote
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("next", "status"):
        sub.add_parser(name).add_argument("run")
    d = sub.add_parser("decide")
    d.add_argument("run")
    d.add_argument("id")
    d.add_argument("decision", choices=["correct", "fix", "reject"])
    d.add_argument("--by", required=True)
    d.add_argument("--statement")
    d.add_argument("--quote")
    d.add_argument("--note", default="")
    a = ap.parse_args()
    if a.cmd == "next":
        dec = decisions()
        todo = [i for i in queue(a.run) if i["id"] not in dec]
        if not todo:
            print("queue empty")
            return
        it = todo[0]
        print(f"{len(todo)} left. {it['id']}\n\nITEM: {it['statement']}\nQUOTE: {it['quote']}\nCLAUSE: "
              f"{it.get('clause_number')}  STRENGTH: {it['strength']}  FINDINGS: {it.get('findings')}\n\nSOURCE:\n"
              f"{source_text(it)}")
    elif a.cmd == "decide":
        print(decide(a.run, a.id, a.decision, a.by, a.statement, a.quote, a.note))
    else:
        run, items, route = load(a.run)
        dec = decisions()
        q = [k for k, v in route.items() if v == "review"]
        print({"items": len(items), "auto": sum(v == "auto" for v in route.values()), "queued": len(q),
               "decided": sum(k in dec for k in q), "shipped": len(shipped(a.run))})


if __name__ == "__main__":
    main()
