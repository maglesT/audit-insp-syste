"""AUDIT LAYER repair merge. Usage: python3 -I merge.py <draftDir> <repairDir> <newDir>
Builds <newDir>/raw.json = the draft's points / no_point of every block, minus the ones the repair replaced
(repairDir/key.json replace_points, replace_no_point), plus the repaired points (new stable ids "<block>-R<round><k>")
and repaired no_point entries. Then run: python3 -I assemble.py <newDir> (coverage + code checks again), and re-check
only the new points: OUT=<dir> node layer.mjs check-block-build <newDir> <newDir>/new-ids.json.
A repaired block with an API error keeps its old points and is listed in new-ids.json "unrepaired".
"""
import json, sys, os, re, collections


def main(dd, rd, nd):
    D = json.load(open(f"{dd}/drafts.json"))
    key = {k["id"]: k for k in json.load(open(f"{rd}/key.json"))}
    rep = {r["id"]: r for r in json.load(open(f"{rd}/raw.json"))["results"]}
    rnd = 1 + max([int(m.group(1)) for p in D["points"] for m in [re.search(r"-R(\d+)\d\d$", p["id"])] if m] or [0])
    blocks = collections.OrderedDict()
    for r in json.load(open(f"{dd}/raw.json"))["results"]:
        blocks[r["id"]] = {"points": [], "no_point": []}
    keep = ("id", "units", "question", "verify", "evidence", "grade_hint", "modality")
    for p in D["points"]:
        blocks.setdefault(p["block"], {"points": [], "no_point": []})["points"].append({k: p[k] for k in keep if k in p})
    for x in D.get("no_point", []):
        blocks[x["block"]]["no_point"].append({"unit": x["unit"], "reason": x["reason"]})
    new_ids, unrepaired = [], []
    for bid, k in key.items():
        r = rep.get(bid)
        if not r or r.get("error"):
            unrepaired.append(bid); continue
        b = blocks[bid]
        b["points"] = [p for p in b["points"] if p["id"] not in set(k["replace_points"])]
        b["no_point"] = [x for x in b["no_point"] if x["unit"] not in set(k["replace_no_point"])]
        for i, p in enumerate(r["data"]["points"], 1):
            p = {**p, "id": f"{bid}-R{rnd}{i:02d}"}
            b["points"].append(p); new_ids.append(p["id"])
        for x in r["data"].get("no_point", []):
            b["no_point"].append(x); new_ids.append(x["unit"])
    os.makedirs(nd, exist_ok=True)
    json.dump({"usage": {"merged_from": [dd, rd]}, "results": [{"id": bid, "data": v} for bid, v in blocks.items()]},
              open(f"{nd}/raw.json", "w"), ensure_ascii=False, indent=1)
    json.dump(new_ids, open(f"{nd}/new-ids.json", "w"), indent=1)
    print(json.dumps({"round": rnd, "repaired_blocks": len(key) - len(unrepaired), "unrepaired": unrepaired, "new_items": len(new_ids)}))


if __name__ == "__main__":
    main(*[a.rstrip("/") for a in sys.argv[1:4]])
