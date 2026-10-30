"""Per-regulator library items from a draft run (D37): one item per drafted obligation, no cross-regulator merging.

  python3 tools/ai/items.py write <draft dir> --topics <consolidation dir>   # library/requirements/, coverage/

Each drafted mapping (pilot.py ingest-draft: mappings.jsonl, and twin-mappings.jsonl for twins, D36) becomes one
item: the drafter's statement is the item text, and the mapping (source, clause, clause sha256, quote, strength,
plant types) is its one internal source link. A twin's item has the same text and strength as its lead's, so
identical clauses give identical items (Layer 1 check 8). Items are numbered by top topic ("SI-001") in draft
order, each lead followed by its twins. Status is "draft" until Layer 2 verifies the item.

The sub-topic of each item: the S3 draft run predates topic drafting, so it is taken from the topic that the
(dropped) consolidation run gave the obligation's requirement (--topics); later drafts carry their own "topic".
Coverage: each drafted clause lists its items; a clause the drafter found no obligation in is "na" with the
drafter's reason, and so are its twins. Writing merges into the library (merge): items keep their ids and
statuses by source link, new items take new ids, and items of re-drafted clauses that are gone are retired.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
import runner  # noqa: E402
import sessions  # noqa: E402

MAPPING_KEYS = ("source", "clause_ref", "clause_sha256", "quote", "strength", "plant_types")


def topics_from_consolidation(state):
    """{draft mapping index: sub-topic} from a consolidation state (obligation "O012" is mapping 12)."""
    topic = {r["id"]: r["topic"] for r in state["requirements"]}
    return {int(oid[1:]): topic[d["requirement"]] for oid, d in state["decisions"].items()}


def build(draft_dir, topic_of):
    """(items, coverage): items in draft order, each lead followed by its twins; coverage {stem: {ref: entry}}."""
    draft_dir = Path(draft_dir)
    mappings = runner.read_jsonl(draft_dir / "mappings.jsonl")
    twins_file = draft_dir / "twin-mappings.jsonl"
    twins = {}
    for t in (runner.read_jsonl(twins_file) if twins_file.exists() else []):
        twins.setdefault(t["twin_of"], []).append(t)
    used, items, coverage = {}, [], {}
    for n, m in enumerate(mappings):
        topic = m.get("topic") or topic_of.get(n)
        if not topic:
            raise SystemExit(f"mapping {n} ({m['source']} {m['ref']}) has no topic")
        for row in [m] + twins.get(n, []):
            prefix = topic.split(".")[0]
            used[prefix] = used.get(prefix, 0) + 1
            rid = f"{prefix}-{used[prefix]:03d}"
            link = {"source": row["source"], "clause_ref": row["ref"], "clause_sha256": row["clause_sha256"],
                    "quote": row["quote"], "strength": row["strength"], "plant_types": list(row["plant_types"])}
            items.append({"id": rid, "topic": topic, "item_text": m["statement"].strip(), "strength": row["strength"],
                          "plant_types": list(row["plant_types"]), "parameters": {}, "general": False,
                          "status": "draft", "mappings": [link]})
            entry = coverage.setdefault(Path(row["source"]).stem, {}).setdefault(row["ref"], {"requirements": []})
            entry["requirements"].append(rid)
    requests = {r.custom_id: r for r in sessions.load_requests(draft_dir)}
    twins_of = {}
    topic_file = draft_dir / "topic.json"
    if topic_file.exists():
        for u in json.loads(topic_file.read_text(encoding="utf-8"))["units"]:
            twins_of[(u["source"], u["ref"])] = [(t["source"], t["ref"]) for t in u["twins"]]
    for res in runner.read_jsonl(draft_dir / "results.jsonl"):
        if res["ok"] and not res["answer"]["obligations"]:
            meta = requests[res["custom_id"]].meta
            reason = res["answer"]["no_obligation_reason"].strip() or "no obligation"
            for source, ref in [(meta["source"], meta["ref"])] + twins_of.get((meta["source"], meta["ref"]), []):
                coverage.setdefault(Path(source).stem, {}).setdefault(ref, {"na": reason})
    return items, coverage


def link_key(item):
    m = item["mappings"][0]
    return (m["source"], m["clause_ref"], " ".join(m["quote"].split()))


def merge(old, new):
    """New items merged into the library's items by source link (source, clause, quote). A matched item keeps its
    id, and its status when text, strength and plant types are unchanged (else it is a draft again); a new item
    gets the next id of its prefix after the highest in use; an old item of a re-drafted clause that the new
    draft no longer has is retired. Items of clauses not in this draft are kept as they are."""
    by_key = {link_key(r): r for r in old}
    redrafted = {link_key(r)[:2] for r in new}
    used = {}
    for r in old:
        prefix, _, number = r["id"].partition("-")
        used[prefix] = max(used.get(prefix, 0), int(number))
    out, seen = [], set()
    for r in new:
        key = link_key(r)
        seen.add(key)
        hit = by_key.get(key)
        if hit:
            same = all(hit[f] == r[f] for f in ("item_text", "strength", "plant_types", "topic"))
            out.append({**r, "id": hit["id"], "status": hit["status"] if same else "draft"})
            continue
        prefix = r["topic"].split(".")[0]
        used[prefix] = used.get(prefix, 0) + 1
        out.append({**r, "id": f"{prefix}-{used[prefix]:03d}"})
    renamed = {link_key(r): r["id"] for r in out}
    for r in old:
        key = link_key(r)
        if key in seen:
            continue
        out.append({**r, "status": "retired"} if key[:2] in redrafted else r)
    return out, renamed


def write(items, coverage, root):
    """Merge these items into library/requirements/<TOP>.json (merge) and their clauses' entries into
    library/coverage/<stem>.json; everything else in the library is kept."""
    import model
    root = Path(root)
    old = model.requirements(root) if (root / "requirements").exists() else []
    merged, renamed = merge(old, items)
    ids = {it["id"]: renamed[link_key(it)] for it in items}            # positional build ids -> library ids
    for sub in ("requirements", "coverage"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    by_top = {}
    for it in merged:
        by_top.setdefault(it["topic"].split(".")[0], []).append(it)
    for path in (root / "requirements").glob("*.json"):
        if path.stem not in by_top:
            path.unlink()                                                # every item it held is in merged
    for top, reqs in by_top.items():
        reqs.sort(key=lambda r: int(r["id"].partition("-")[2]))
        (root / "requirements" / f"{top}.json").write_text(
            json.dumps({"requirements": reqs}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for stem, entries in coverage.items():
        path = root / "coverage" / f"{stem}.json"
        old_entries = json.loads(path.read_text(encoding="utf-8"))["clauses"] if path.exists() else {}
        fixed = {ref: ({"requirements": [ids[r] for r in e["requirements"]]} if "requirements" in e else e)
                 for ref, e in entries.items()}
        path.write_text(json.dumps({"clauses": {**old_entries, **fixed}}, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return {"items": len(items), "library_items": len(merged), "retired": sum(r["status"] == "retired" for r in merged),
            "topics": sorted(by_top), "coverage_files": len(coverage)}


def main():
    import model
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["write"])
    ap.add_argument("draft_dir")
    ap.add_argument("--topics", help="consolidation run dir whose decisions give each obligation's sub-topic")
    a = ap.parse_args()
    topic_of = {}
    if a.topics:
        topic_of = topics_from_consolidation(json.loads((Path(a.topics) / "state.json").read_text(encoding="utf-8")))
    items, coverage = build(a.draft_dir, topic_of)
    print(json.dumps(write(items, coverage, model.LIBRARY)))


if __name__ == "__main__":
    main()
