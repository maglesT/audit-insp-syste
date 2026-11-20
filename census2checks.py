"""Convert a per-item sample/census result folder (layer.mjs sample-build + collect: raw.json, key.json) into the
checks.json format that finalize.py / waves.mjs repair-tasks read. Usage: python3 -I census2checks.py <dir>
Writes <dir>/check/checks.json: results (points) + no_point_results / no_point_fails (no_point units)."""
import json, sys, os
d = sys.argv[1].rstrip("/")
item_of = {k["id"]: k["item"] for k in json.load(open(f"{d}/key.json"))}
res, npr = [], []
for r in json.load(open(f"{d}/raw.json"))["results"]:
    kind, iid = item_of[r["id"]].split(":", 1)
    if kind == "P":
        if r.get("error"):
            res.append({"id": iid, "ok": False, "error": r["error"]}); continue
        bad = [k for k in ("no_more", "no_less", "answerable", "own_words") if r["data"][k]["result"] != "PASS"]
        res.append({"id": iid, "ok": not bad, "fail": bad, **{k: r["data"][k] for k in ("no_more", "no_less", "answerable", "own_words")}})
    else:
        if r.get("error"):
            npr.append({"unit": iid, "ok": False, "major": False, "reason": r["error"], "writer_reason": ""}); continue
        npr.append({"unit": iid, "ok": r["data"]["result"] == "PASS" and not r["data"]["major"], "major": r["data"]["major"],
                    "reason": r["data"]["reason"], "writer_reason": ""})
os.makedirs(f"{d}/check", exist_ok=True)
out = {"summary": {"points": len(res), "points_pass": sum(x["ok"] for x in res), "no_point": len(npr),
                   "no_point_pass": sum(x["ok"] for x in npr), "major": sum(1 for x in npr if x["major"])},
       "fails": [], "no_point_fails": [x for x in npr if not x["ok"]], "results": res, "no_point_results": npr}
json.dump(out, open(f"{d}/check/checks.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out["summary"]))
