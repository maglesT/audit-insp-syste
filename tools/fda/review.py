"""Review queue (D47, "nothing ships unless proven"): the human route for items the automatic route did not prove.

  python3 tools/fda/review.py next RUN                      # the next undecided item, with its source text beside it
  python3 tools/fda/review.py decide RUN ID correct --by NAME [--note TEXT]
  python3 tools/fda/review.py decide RUN ID fix --by NAME --statement TEXT [--quote TEXT] [--note TEXT]
  python3 tools/fda/review.py decide RUN ID reject --by NAME [--note TEXT]
  python3 tools/fda/review.py status RUN                    # automatic, queued, decided, shipped
  python3 tools/fda/review.py import-artifact FILE          # the owner's review-page decisions (db export)

The queue is every item of RUN/route.json routed to "review". Each decision is appended to
library/review/decisions.jsonl with the reviewer's name and the UTC time (attributable, never edited in place; a
later decision on the same item supersedes an earlier one). A decision counts only for its run and for the item as
it was decided (fingerprint of statement, quote, clause, strength, plant types). An item ships when its latest
decision is "correct" or "fix" (with the corrected statement; a corrected quote must still be found in the source
text), or when its route is "auto" and it has not been rejected. Everything else does not ship.

import-artifact reads an export of the owner's review page (claude.ai artifact, db collection "decisions", pulled
with the artifact db tools): a JSON list, {"docs": [...]} or JSON lines, each a record {id, run, item_hash,
decision, by, note, at, statement} or a db document {"id", "data": record}. Each valid record is appended with its
original "at" (and "via": "review page"); the run and item_hash rules apply: a record for a run or item that does
not exist, or for an item that changed since it was shown (item_hash), is not imported and is listed. A record
already in the file is not appended twice. "at" must be a full timestamp with a time zone and not lie in the
future (more than SKEW seconds ahead of this machine). "Latest" means latest by "at" (file order breaks ties), so an imported
decision made earlier than one already recorded does not supersede it.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DECISIONS = ROOT / "library" / "review" / "decisions.jsonl"


def load(run):
    """(run, items, route); an id whose item is gone or changed since routing (hash in route.json) is "review"
    and never "auto"."""
    run = Path(run)
    items = {i["id"]: i for i in (json.loads(ln) for ln in (run / "items.jsonl").read_text().splitlines() if ln.strip())}
    doc = json.loads((run / "route.json").read_text())
    hashes = doc.get("hashes", {})
    route = {}
    for k, v in doc["route"].items():
        if k not in items:
            continue
        if v == "auto" and hashes.get(k) != fingerprint(items[k]):
            v = "review"
        route[k] = v
    return run, items, route


def fingerprint(item):
    """Always recomputed from the item's content (a stored hash could be stale)."""
    sys.path.insert(0, str(HERE))
    import xmlprofile
    return xmlprofile.item_hash(item)


def decisions(path=DECISIONS, run=None, items=None):
    """{item id: latest decision}; with run and items, only decisions recorded for that run on the item as it is
    now (same fingerprint), so a decision never carries over to a redrafted item with the same id."""
    out = {}
    if Path(path).exists():
        for ln in Path(path).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                d = json.loads(ln)
                if run is not None and (d.get("run") != Path(run).name or d["id"] not in items
                                        or d.get("item_hash") != fingerprint(items[d["id"]])):
                    continue
                if d["id"] not in out or when(d) >= when(out[d["id"]]):
                    out[d["id"]] = d
    return out


def when(d):
    """A decision's time as an aware UTC datetime; a missing or unreadable time sorts first (never crashes)."""
    try:
        t = datetime.fromisoformat(re.sub(r"Z$", "+00:00", d["at"]))
    except (KeyError, TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


# a full timestamp with seconds and an explicit zone: "2026-10-31T12:00:00Z", "...12:00:00.123+02:00"
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
SKEW = 600          # seconds an imported time may lie ahead of this machine's clock


def source_text(item):
    """The text the reviewer checks the item against: the cited XML paragraph and its sub-paragraphs, or for a page
    item its page reference (the page image is in work/vision-pages, rendered by tools/pages/vision.py)."""
    if item.get("source", "").endswith(".html"):
        sys.path.insert(0, str(HERE))
        import htmlprofile
        ref = item["clause_number"].strip()
        if ref not in htmlprofile.cited(item["source"]):
            unit = htmlprofile.units(item["source"]).get(item.get("section", ""), [])
            return f"({ref!r} is not a paragraph of the page; the unit's text:)\n" + "\n".join(
                f"{p['ref']}  {p['text']}" for p in unit if p["cite"])
        own, after = htmlprofile.run_on(ref, item["source"])
        lead = htmlprofile.lead_in(ref, item["source"])
        return "\n".join(([f"(lead-in) {lead}"] if lead else []) + [f"{ref}  {own}"] + after)
    if item.get("source", "").endswith(".xml"):
        sys.path.insert(0, str(HERE))
        import xmlprofile
        ref = item["clause_number"]
        return "\n".join(f"{r}  {t}" for r, t in xmlprofile.paragraphs(item["source"])
                         if r == ref or r.startswith(ref + "(") or r == xmlprofile.parent(ref))
    return f"{item['source']} page {item.get('page')} (page image: work/vision-pages)"


def quote_in_source(item, quote):
    """A corrected quote must be in the item's source text (XML or HTML profile); page items are not checked here."""
    sys.path.insert(0, str(HERE))
    it = dict(item, quote=quote)
    if item["source"].endswith(".xml"):
        import xmlprofile
        return xmlprofile.check_item(it, it["source"])[1]
    if item["source"].endswith(".html"):
        import htmlprofile
        return htmlprofile.check_item(it, it["source"])[1]
    return True


def queue(run):
    run, items, route = load(run)
    return [items[k] for k, v in route.items() if v == "review"]


def shipped(run, path=DECISIONS):
    run, items, route = load(run)
    dec = decisions(path, run, items)
    out = []
    for k, v in route.items():
        d = dec.get(k, {}).get("decision")
        if d == "reject":                    # a reject (e.g. after the spot check) stops even an automatic item
            continue
        if v == "auto" or d in ("correct", "fix"):
            out.append(k)
    return out


def decide(run, item_id, decision, by, statement=None, quote=None, note="", path=DECISIONS):
    run, items, route = load(run)
    if item_id not in items:
        raise SystemExit(f"{item_id}: not in {run}")
    if not by.strip():
        raise SystemExit("a decision needs the reviewer's name (--by)")
    if decision == "fix" and not statement:
        raise SystemExit("fix needs the corrected statement (--statement)")
    if quote:
        if not quote_in_source(items[item_id], quote):
            raise SystemExit("the corrected quote is not in the source text")
    rec = {"id": item_id, "run": Path(run).name, "item_hash": fingerprint(items[item_id]), "decision": decision,
           "by": by.strip(),
           "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "note": note}
    if statement:
        rec["statement"] = statement
    if quote:
        rec["quote"] = quote
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


RUNS = ROOT / "library" / "ai-runs"
FIELDS = ("id", "run", "item_hash", "decision", "by", "at", "note", "statement", "quote")


def read_export(path):
    """The rows of a review-page export (see the module docstring): records, or None for an unreadable row."""
    text = Path(path).read_text(encoding="utf-8").strip()
    try:
        rows = doc = json.loads(text)
        if isinstance(doc, dict):                 # {"docs": [...]}, or one record / document on a single line
            rows = doc["docs"] if "docs" in doc else doc.get("documents", [doc])
    except json.JSONDecodeError:                  # JSON lines: an unreadable line is one unreadable row
        rows = []
        for ln in text.splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except json.JSONDecodeError:
                    rows.append(None)
    if not isinstance(rows, list):
        rows = [None]
    return [(r["data"] if isinstance(r, dict) and isinstance(r.get("data"), dict) else r) for r in rows]


def import_artifact(file, path=DECISIONS, runs=RUNS):
    """Appends the export's valid, new decisions to path; returns {"imported": [...], "skipped": [(record, why)]}."""
    seen = set()
    if Path(path).exists():
        seen = {dup_key(d) for d in (json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines()
                                     if ln.strip())}
    loaded, imported, skipped = {}, [], []
    now = datetime.now(timezone.utc)
    duplicates = []
    for r in read_export(file):
        why = ""
        if not isinstance(r, dict):
            r, why = {}, "not a record"
        elif not all(isinstance(r.get(k), str) and r[k].strip() for k in ("id", "run", "item_hash", "decision", "by",
                                                                           "at")):
            why = "missing id, run, item_hash, decision, by or at"
        elif any(r.get(k) is not None and not isinstance(r[k], str) for k in ("note", "statement", "quote")):
            why = "note, statement and quote must be text"
        elif not STAMP.match(r["at"]):
            why = f"time {r['at']!r} is not a full timestamp with a time zone"
        elif (when(r) - now).total_seconds() > SKEW:
            why = f"time {r['at']!r} lies in the future"
        elif r["decision"] not in ("correct", "fix", "reject"):
            why = f"unknown decision {r['decision']!r}"
        elif r["decision"] == "fix" and not (r.get("statement") or "").strip():
            why = "fix without the corrected statement"
        elif "/" in r["run"] or r["run"].startswith(".") or not (Path(runs) / r["run"] / "route.json").exists():
            why = f"no routed run {r['run']!r}"
        if not why:
            if r["run"] not in loaded:
                loaded[r["run"]] = load(Path(runs) / r["run"])[1]
            items = loaded[r["run"]]
            if r["id"] not in items:
                why = "no such item in the run"
            elif fingerprint(items[r["id"]]) != r["item_hash"]:
                why = "item changed since it was shown (item_hash)"
            elif r.get("quote") and not quote_in_source(items[r["id"]], r["quote"]):
                why = "the corrected quote is not in the source text"
        if why:
            skipped.append((r, why))
            continue
        rec = {k: (r[k].strip() if k == "by" else r[k]) for k in FIELDS if r.get(k) not in (None, "") or k == "note"}
        rec.setdefault("note", "")
        rec["via"] = "review page"
        key = dup_key(rec)
        if key in seen:
            duplicates.append(rec)
            continue
        seen.add(key)
        imported.append(rec)
    if imported:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            for rec in sorted(imported, key=when):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"imported": imported, "skipped": skipped, "duplicates": duplicates}


def dup_key(d):
    """Two records are the same decision when everything decided is the same and the time is the same instant."""
    return (d.get("run"), d.get("id"), d.get("item_hash"), d.get("decision"), d.get("by"), when(d),
            d.get("statement"), d.get("quote"), d.get("note") or "")


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
    sub.add_parser("import-artifact").add_argument("file")
    a = ap.parse_args()
    if a.cmd == "import-artifact":
        out = import_artifact(a.file)
        print(f"imported {len(out['imported'])}, already recorded {len(out['duplicates'])}, "
              f"skipped {len(out['skipped'])}")
        for r, why in out["skipped"]:
            print(f"  skipped {r.get('run')} {r.get('id')}: {why}")
        return
    if a.cmd == "next":
        run, items, _ = load(a.run)
        dec = decisions(DECISIONS, run, items)
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
        dec = decisions(DECISIONS, run, items)
        q = [k for k, v in route.items() if v == "review"]
        print({"items": len(items), "auto": sum(v == "auto" for v in route.values()), "queued": len(q),
               "decided": sum(k in dec for k in q), "shipped": len(shipped(a.run))})


if __name__ == "__main__":
    main()
