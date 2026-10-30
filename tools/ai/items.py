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
drafter's reason, and so are its twins. The written files replace the library's requirement and coverage files.
"""
import argparse
import json
import shutil
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


def write(items, coverage, root):
    """Replace library/requirements/<TOP>.json and library/coverage/<stem>.json with these items."""
    root = Path(root)
    for sub in ("requirements", "coverage"):
        shutil.rmtree(root / sub, ignore_errors=True)
        (root / sub).mkdir(parents=True)
    by_top = {}
    for it in items:
        by_top.setdefault(it["topic"].split(".")[0], []).append(it)
    for top, reqs in by_top.items():
        (root / "requirements" / f"{top}.json").write_text(
            json.dumps({"requirements": reqs}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for stem, entries in coverage.items():
        (root / "coverage" / f"{stem}.json").write_text(
            json.dumps({"clauses": entries}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"items": len(items), "topics": sorted(by_top), "coverage_files": len(coverage)}


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
