"""AUDIT LAYER: score a blind CHECK batch. Usage: python3 -I score.py <checkDir> <draftDir>
Reads <checkDir>/raw.json (layer.mjs collect; kind check = one result per point, kind checkblock = one result per block
with "points" and "no_point") + <draftDir>/drafts.json. Writes <checkDir>/checks.json.
A point passes only if all criteria (five from round 4: + useful) are PASS; a no_point entry passes if the checker says PASS (truly not
actionable). A point / no_point the checker did not answer counts as a FAIL ("no answer").
"""
import json, sys, collections

C = ["no_more", "no_less", "answerable", "own_words"]   # owner 19 Nov (final): round-3 criteria; "useful" dropped


def main(cd, dd):
    raw = json.load(open(f"{cd}/raw.json"))
    rep = json.load(open(f"{cd}/build-report.json"))
    key = {k["id"]: k for k in json.load(open(f"{cd}/key.json"))}
    D = json.load(open(f"{dd}/drafts.json"))
    pts = {p["id"]: p for p in D["points"]}
    npi = {x["unit"]: x for x in D.get("no_point", [])}
    out, npo, by = [], [], collections.Counter()

    def judge(pid, d):
        bad = [k for k in C if k in d and d[k]["result"] != "PASS"]   # round 1-3 checks had no "useful"
        by.update(bad)
        out.append({"id": pid, "ok": not bad, "fail": bad, **{k: d[k] for k in C if k in d}})

    for r in raw["results"]:
        if rep["kind"] == "check":
            if r.get("error"):
                out.append({"id": r["id"], "ok": False, "error": r["error"]})
            else:
                judge(r["id"], r["data"])
            continue
        k = key[r["id"]]
        if r.get("error"):
            out += [{"id": p, "ok": False, "error": r["error"]} for p in k["points"]]
            npo += [{"unit": u, "ok": False, "error": r["error"]} for u in k.get("no_point", [])]
            continue
        got = {x["id"]: x for x in r["data"]["points"]}
        for p in k["points"]:
            if p in got:
                judge(p, got[p])
            else:
                out.append({"id": p, "ok": False, "error": "no answer"})
        gn = {x["unit"]: x for x in r["data"].get("no_point", [])}
        for u in k.get("no_point", []):
            x = gn.get(u)
            npo.append({"unit": u, "ok": bool(x) and x["result"] == "PASS", "major": bool(x) and x.get("major", False),
                        "reason": x["reason"] if x else "no answer",
                        "writer_reason": npi[u]["reason"]})
    fails = [{**o, "question": pts[o["id"]]["question"], "verify": pts[o["id"]]["verify"],
              "evidence": pts[o["id"]]["evidence"], "units": pts[o["id"]]["units"]} for o in out if not o["ok"]]
    s = {"checked": len(out), "pass": sum(o["ok"] for o in out), "errors": sum(1 for o in out if o.get("error")),
         "fail_by_criterion": by, "no_point_checked": len(npo), "no_point_pass": sum(o["ok"] for o in npo),
         "no_point_P2_major_overrides": sum(1 for o in npo if o.get("major")),
         "usage": raw.get("usage")}
    json.dump({"summary": s, "fails": fails, "no_point_fails": [o for o in npo if not o["ok"]], "results": out,
               "no_point_results": npo}, open(f"{cd}/checks.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"))
