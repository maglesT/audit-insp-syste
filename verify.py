"""AUDIT LAYER verify (lead 20 Nov). Usage: python3 -I verify.py   -> proof.json ("PROVEN": true only if all pass)
Re-checks by code (reads points.json, owner-review.json, merged/checklist.json, merged/checkpoints.json, blocks.json,
sample.json + the proof-sample results):
 V1  every clause item / unit of a point or other requirement exists in merged/checkpoints.json and is a DUTY unit
 V2  coverage: every duty unit is in >= 1 point OR in other_requirements OR in owner-review.json
 V3  never both (A6): no unit is in a point and in other_requirements
 V4  modality (A2/A7): "(recommended)" in the question iff modality "should"; a should-point never uses
     must / shall / as required / is|are|be required in question or verify
 V5  copy guard (A4): no question copies a run of 10+ words of one of its units
 V6  regulator ("Schedule M" / "US FDA" / "EU") = the clause items' regulator; area, system, plant_types, audience =
     those of the clause items' block (blocks.json); every point has question, verify, evidence, grade_hint
 V7  REF1: every reference is a reference of its clause item; joined items follow the via / span rule (finalize.py)
 V8  owner-review items are not in points.json
 V9  points.json is exactly what finalize.py builds from the current drafts + checks (run twice, identical)
 V11 (A8) a question keeps the softening qualifier of its units (minimise, as far as possible, where possible,
     preferably, normally, generally)
 V12 (A9) in a should-point every verify sentence carries "(recommended)"
 V13 (A10) scope negation of a unit kept; V14 (A11) no "(recommended)" on must-only units
 Fallback points ("-F", owner-review fallback, exact unit text built by code): V11 and the must-word part of V4 are
     not applied (the question is a fixed frame; the verify is the unit's own text).
 V10 proof sample (sample.json, one request per item): 59 points with 0 FAIL and 59 no_point units with 0 FAIL;
     the sample was drawn from the current points.json (sha256)
"""
import json, re, os, hashlib, collections, subprocess, sys
sys.path.insert(0, "/root/audit-admin/audit-layer")

ROOT = "/root/audit-admin"
HERE = f"{ROOT}/audit-layer"
J = lambda p: json.load(open(p))
W = lambda s: re.findall(r"[a-z0-9]+", s.lower())
from assemble import SOFT, NEG, PERMIT, MUST as MUSTDUTY, SHOULD as SHOULDW
from a9 import unmarked                                # A8 qualifier list (single source)
MUSTWORDS = re.compile(r"\b(must|shall|as required|(is|are|be) required)\b", re.I)


def copied(unit_text, q, n=10):
    u, o = W(unit_text), " ".join(W(q))
    return any(" ".join(u[i:i + n]) in o for i in range(0, max(0, len(u) - n + 1)))


RULE = ("2-of-3 rule (owner 20 Nov, decided before the sample): a sample FAIL gets 2 more independent per-item "
        "opinions (the same request sent again). ERROR = at least 2 of the 3 opinions FAIL. If they split (1 of 3), "
        "the item goes to owner review (a point leaves points.json; a no_point stays in other_requirements, listed). "
        "Any ERROR = fix the class + a fresh sample.")
P_CRIT = ("no_more", "no_less", "answerable", "own_words")


def opinion_fail(r):
    if not r or r.get("error"):
        return True, (r or {}).get("error", "no answer")
    d = r["data"]
    if "result" in d:
        return d["result"] != "PASS" or d["major"], d["reason"] + (" (MAJOR)" if d["major"] else "")
    bad = [k for k in P_CRIT if d[k]["result"] != "PASS"]
    return bool(bad), " | ".join(f"{k}: {d[k]['reason']}" for k in bad)


def judge_sample():
    """-> (judgement dict, split dict for finalize) or (None, None) if no sample results yet"""
    if not os.path.exists(f"{HERE}/sample.json"):
        return None, None
    S = J(f"{HERE}/sample.json")
    d = f"{HERE}/full/proof-{S['seed']}"
    if not os.path.exists(f"{d}/raw.json"):
        return None, None
    item_of = {k["id"]: k.get("item", k["id"]) for k in J(f"{d}/key.json")}
    first = {item_of[r["id"]]: r for r in J(f"{d}/raw.json")["results"]}
    extra = collections.defaultdict(list)
    od = f"{d}/opinions"
    if os.path.exists(f"{od}/raw.json"):
        okey = {k["id"]: k["item"] for k in J(f"{od}/key.json")}
        for r in J(f"{od}/raw.json")["results"]:
            extra[okey[r["id"]]].append(r)
    out, split = {"seed": S["seed"], "rule": RULE, "items": []}, {"points": {}, "no_point": {}}
    for kind, ids in (("P", S["points"]), ("N", S["no_point"])):
        for iid in ids:
            f0, why0 = opinion_fail(first.get(f"{kind}:{iid}"))
            ops = [{"opinion": 1, "fail": f0, "why": why0}]
            for n, r in enumerate(extra.get(f"{kind}:{iid}", []), 2):
                fx, wx = opinion_fail(r)
                ops.append({"opinion": n, "fail": fx, "why": wx})
            nf = sum(o["fail"] for o in ops)
            if not f0:
                verdict = "pass"
            elif len(ops) < 3:
                verdict = "opinions pending"
            else:
                verdict = "ERROR" if nf >= 2 else "split"
            if verdict == "split":
                split["points" if kind == "P" else "no_point"][iid] = why0
            out["items"].append({"kind": "point" if kind == "P" else "no_point", "id": iid, "verdict": verdict, "opinions": ops})
    out["summary"] = {v: sum(1 for x in out["items"] if x["verdict"] == v) for v in ("pass", "split", "ERROR", "opinions pending")}
    return out, split


def main():
    res, fails = {}, collections.defaultdict(list)
    judged, split = judge_sample()
    if split is not None:
        json.dump(split, open(f"{HERE}/proof-split.json", "w"), ensure_ascii=False, indent=1)
    sha_before = hashlib.sha256(open(f"{HERE}/points.json", "rb").read()).hexdigest()
    subprocess.run([sys.executable, "-I", f"{HERE}/finalize.py"], check=True, capture_output=True)
    sha1 = hashlib.sha256(open(f"{HERE}/points.json", "rb").read()).hexdigest()
    subprocess.run([sys.executable, "-I", f"{HERE}/finalize.py"], check=True, capture_output=True)
    sha2 = hashlib.sha256(open(f"{HERE}/points.json", "rb").read()).hexdigest()
    if not (sha1 == sha2 == sha_before):
        fails["V9"].append(f"points.json differs from a fresh finalize run (before {sha_before[:12]}, runs {sha1[:12]} {sha2[:12]})")
    P, R = J(f"{HERE}/points.json"), J(f"{HERE}/owner-review.json")["items"]
    ck = {x["id"]: x for x in J(f"{ROOT}/merged/checklist.json")}
    cp = {x["id"]: {u["n"]: u for u in x["units"]} for x in J(f"{ROOT}/merged/checkpoints.json")}
    blk_of = {}
    for b in J(f"{HERE}/blocks.json")["blocks"]:
        for it in b["items"]:
            blk_of[it["id"]] = b
    sys.path.insert(0, HERE)
    import finalize
    src = J(f"{ROOT}/merged/sources.json")["items"]

    in_pt, in_np = set(), set()
    for p in P["points"]:
        uids = []
        for c in p["clauses"]:
            for n in c["units"]:
                u = cp.get(c["item"], {}).get(n)
                if not u or u["mark"] != "duty":
                    fails["V1"].append(f"{p['id']}: {c['item']}#{n} missing or not duty")
                    continue
                uids.append(f"{c['item']}#{n}"); in_pt.add(f"{c['item']}#{n}")
                ut_all = u["text"]
                for sa, sb in ([] if p["id"].endswith("-F") else SOFT):   # -F: exact-text fallback, generic question
                    if re.search(sa, ut_all, re.I) and not re.search(sb, p["question"], re.I):
                        fails["V11"].append(f"{p['id']}: question drops the qualifier of {c['item']}#{n}"); break
                if copied(u["text"], p["question"]):
                    fails["V5"].append(f"{p['id']}: question copies 10+ words of {c['item']}#{n}")
            b = blk_of.get(c["item"])
            if not b or b["regulator"] != p["regulator"] or ck[c["item"]]["regulator"] != p["regulator"] or \
                    [b["area"], b["system"], b["plant_types"], b["audience"]] != [p["area"], p["system"], p["plant_types"], p["audience"]]:
                fails["V6"].append(f"{p['id']}: regulator/area/system/plant_types/audience differ from {c['item']}")
        if p["regulator"] not in ("Schedule M", "US FDA", "EU"):
            fails["V6"].append(f"{p['id']}: regulator {p['regulator']}")
        if not (p["question"] and p["verify"] and p["evidence"] and p["grade_hint"] in ("critical", "major", "other")):
            fails["V6"].append(f"{p['id']}: missing field")
        rec = "(recommended)" in p["question"].lower()
        if rec != (p["modality"] == "should"):
            fails["V4"].append(f"{p['id']}: (recommended) does not match modality {p['modality']}")
        utx = [cp[c["item"]][n]["text"] for c in p["clauses"] for n in c["units"] if cp.get(c["item"], {}).get(n)]
        for na, nb in NEG:
            if re.search(na, " ".join(utx), re.I) and not re.search(nb, p["question"] + " " + p["verify"], re.I):
                fails["V13"].append(f"{p['id']}: drops the scope negation '{na}'"); break
        if rec and not any(SHOULDW.search(t) or PERMIT.search(t) for t in utx) and any(MUSTDUTY.search(t) for t in utx):
            fails["V14"].append(f"{p['id']}: (recommended) on must-only units")
        if p["modality"] == "should" and unmarked(p["verify"]):
            fails["V12"].append(f"{p['id']}: should-point verify sentence without (recommended)")
        if p["modality"] == "should" and not p["id"].endswith("-F") and MUSTWORDS.search(p["question"] + " " + p["verify"]):
            fails["V4"].append(f"{p['id']}: should-point uses must/shall/required")
        check_refs(p["id"], p["references"], uids, ck, cp, src, finalize, fails)
    for o in P["other_requirements"]:
        uid = f"{o['item']}#{o['unit']}"
        u = cp.get(o["item"], {}).get(o["unit"])
        if not u or u["mark"] != "duty":
            fails["V1"].append(f"other {uid} missing or not duty")
        in_np.add(uid)
        b = blk_of.get(o["item"])
        if not b or b["regulator"] != o["regulator"] or o["regulator"] not in ("Schedule M", "US FDA", "EU"):
            fails["V6"].append(f"other {uid}: regulator")
        check_refs(uid, o["references"], [uid], ck, cp, src, finalize, fails)
    review_units = {u for r in R for u in r["units"]}
    review_ids = {r["id"] for r in R}
    duty = {f"{i}#{n}" for i, us in cp.items() for n, u in us.items() if u["mark"] == "duty"}
    miss = duty - in_pt - in_np - review_units
    if miss:
        fails["V2"].append(f"{len(miss)} duty units not covered, e.g. {sorted(miss)[:5]}")
    both = in_pt & in_np
    if both:
        fails["V3"].append(f"{len(both)} units in a point and in other_requirements, e.g. {sorted(both)[:5]}")
    leak = review_ids & {p["id"] for p in P["points"]}
    if leak:
        fails["V8"].append(f"owner-review ids in points.json: {sorted(leak)[:5]}")
    res["counts"] = {"points": len(P["points"]), "other_requirements": len(P["other_requirements"]),
                     "owner_review": len(R), "duty_units": len(duty), "covered_by_points": len(in_pt),
                     "in_other_requirements": len(in_np)}
    res["sample"] = judged
    if judged is None:
        fails["V10"].append("no proof sample results yet")
    else:
        sys.path.insert(0, HERE)
        import finalize as fz
        nosplit = json.dumps(fz.main(apply_split=False, write=False), ensure_ascii=False, indent=1).encode()
        if hashlib.sha256(nosplit).hexdigest() != J(f"{HERE}/sample.json")["points_sha256"]:
            fails["V10"].append("sample.json was drawn from another points.json")
        s = judged["summary"]
        if s["ERROR"] or s["opinions pending"]:
            fails["V10"].append(f"sample: {s['ERROR']} ERROR, {s['opinions pending']} waiting for 2 more opinions, {s['split']} split")
    st = J(f"{HERE}/final-status.json")
    if st["pending"]:
        fails["pending"].append(f"{st['pending']} items still pending (not checked or not yet repaired)")
    res["checks"] = {k: ("PASS" if not fails.get(k) else fails[k][:10]) for k in
                     ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11", "V12", "V13", "V14", "pending"]}
    res["PROVEN"] = not any(fails.values())
    if os.path.exists(f"{HERE}/proof-label.json"):
        res["label"] = J(f"{HERE}/proof-label.json")         # honest status (owner option B)
    res["points_sha256"] = sha2
    json.dump(res, open(f"{HERE}/proof.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"PROVEN": res["PROVEN"], "counts": res["counts"],
                      "failed": {k: len(v) for k, v in fails.items() if v}}, indent=1))


def check_refs(owner, refs, uids, ck, cp, src, finalize, fails):
    by = collections.defaultdict(list)
    for u in uids:
        i, n = u.rsplit("#", 1)
        by[i].append(int(n))
    allowed = {}
    for i, ns in by.items():
        it = ck[i]
        spans = None
        if "joined" in it and any(r.get("via") and r["via"] != i for r in it["references"]):
            spans = {s: (a, b) for s, a, b in finalize.subclause_spans(it, src[i]["source_text"])}
        duty = {n for n, u in cp[i].items() if u["mark"] == "duty"}
        for r in it["references"]:
            ok = True
            if "joined" in it and r.get("via") is None:
                ok = duty <= set(ns)
            elif spans and r.get("via"):
                a, b = spans[r["via"]]
                ok = any(a <= cp[i][n]["start"] < b for n in ns)
            allowed[(i, r["ref"])] = ok
    hand = J(f"{HERE}/ref-hand.json") if os.path.exists(f"{HERE}/ref-hand.json") else {}
    for r in refs:
        k = (r["item"], r["ref"])
        if k not in allowed:
            fails["V7"].append(f"{owner}: {r['ref']} is not a reference of {r['item']}")
        elif not allowed[k] and f"{owner}|{r['ref']}" not in hand:
            fails["V7"].append(f"{owner}: {r['ref']} breaks the joined-item via/span rule")
    got = {(r["item"], r["ref"]) for r in refs}
    for k, ok in allowed.items():
        if ok and k not in got and f"{owner}|{k[1]}" not in hand:
            fails["V7"].append(f"{owner}: reference {k[1]} of {k[0]} missing")


def proof_sample(points_sha, fails):
    if not os.path.exists(f"{HERE}/sample.json"):
        fails["V10"].append("no sample.json yet"); return None
    S = J(f"{HERE}/sample.json")
    if S["points_sha256"] != points_sha:
        fails["V10"].append("sample.json was drawn from an older points.json"); return {"seed": S["seed"]}
    d = f"{HERE}/full/proof-{S['seed']}"
    if not os.path.exists(f"{d}/raw.json"):
        fails["V10"].append(f"sample results missing ({d}/raw.json)"); return {"seed": S["seed"]}
    item_of = {k["id"]: k.get("item", k["id"]) for k in J(f"{d}/key.json")}      # P001 -> "P:<point id>"
    raw = {item_of[r["id"]]: r for r in J(f"{d}/raw.json")["results"]}
    out = {"seed": S["seed"], "points": [], "no_point": []}
    for pid in S["points"]:
        r = raw.get(f"P:{pid}")
        bad = [k for k in ("no_more", "no_less", "answerable", "own_words") if not r or r.get("error") or r["data"][k]["result"] != "PASS"]
        out["points"].append({"id": pid, "ok": not bad, "fail": bad, "reasons": {k: r["data"][k]["reason"] for k in bad} if r and not r.get("error") else (r or {}).get("error")})
    for u in S["no_point"]:
        r = raw.get(f"N:{u}")
        ok = bool(r) and not r.get("error") and r["data"]["result"] == "PASS" and not r["data"]["major"]
        out["no_point"].append({"unit": u, "ok": ok, "major": r["data"]["major"] if r and not r.get("error") else None,
                                "reason": r["data"]["reason"] if r and not r.get("error") else (r or {}).get("error")})
    nf_p = sum(not x["ok"] for x in out["points"]); nf_n = sum(not x["ok"] for x in out["no_point"])
    out["summary"] = {"points_fail": nf_p, "no_point_fail": nf_n}
    if nf_p or nf_n:
        fails["V10"].append(f"sample errors: points {nf_p}/59, no_point {nf_n}/59")
    return out


if __name__ == "__main__":
    main()
