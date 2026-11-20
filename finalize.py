"""AUDIT LAYER final assembly (session audit-layer-65, 20 Nov 2026). Usage: python3 -I finalize.py
Reads: full/draft/drafts.json (final merged drafts), the check results of every part in CHECK_ORDER (later results
override earlier ones for the same id), blocks.json, merged/checklist.json (references), merged/checkpoints.json,
merged/sources.json (ONLY the EU / Schedule M source_text of joined items, to find sub-clause boundaries; never WHO /
PIC/S text). Writes: points.json (web-59 contract), owner-review.json, /root/screenshots/audit/audit-layer-owner-review.md,
final-status.json.

Status of an item (point id, or no_point unit id):
  pass    = its latest blind check is PASS (points: all criteria; no_point: PASS and not major) and no code problem
  review  = it was already repaired once (point id contains "-R", or a no_point unit re-listed by a repair) and still
            fails (latest check FAIL or a code problem) -> owner-review list (owner rule: ONE repair only)
  pending = failed / never checked and not yet repaired -> final-status.json lists them; points.json is not final
REF1 (lead): references of a point / other requirement = union of its clause items' references; for a joined item a
reference whose "via" is one of the joined sub-clauses is kept only if a covered unit lies inside that sub-clause's
text span; a reference with via None on a joined item is kept only if ALL duty units of the item are covered by the
same point (hand decisions in ref-hand.json override, each with its reason).
"""
import json, os, re, collections

ROOT = "/root/audit-admin"
HERE = f"{ROOT}/audit-layer"
# later entries override earlier ones; repair-only folders (a8-fix, np-fix) carry repair/key.json (stub checks)
CHECK_ORDER = ["full/part-1", "full/part-2", "full/part-3", "full/final-recheck", "full/a8-fix", "full/np-census",
               "full/np-fix", "full/recheck2", "full/fix3", "full/recheck3",
               "full/np-op2", "full/np-op3", "full/who-fix", "full/np-fix2", "full/recheck4",
               "full/proof-20261123", "full/np-class3", "full/fix4", "full/recheck5", "full/recheck6"]
OWNER_MD = "/root/screenshots/audit/audit-layer-owner-review.md"
J = lambda p: json.load(open(p))


def latest_status():
    pts, nps = {}, {}
    for part in CHECK_ORDER:
        f = f"{HERE}/{part}/check/checks.json"
        if not os.path.exists(f):
            continue
        c = J(f)
        for r in c["results"]:
            pts[r["id"]] = {"ok": r["ok"], "part": part, "why": r.get("error") or " | ".join(
                f"{k}: {r[k]['reason']}" for k in r.get("fail", []))}
        for r in c.get("no_point_results", []):
            nps[r["unit"]] = {"ok": r["ok"], "major": r.get("major", False), "part": part, "k": CHECK_ORDER.index(part),
                              "why": r.get("reason", "")}
    return pts, nps


def repaired_np_units():
    """unit id -> index (in CHECK_ORDER) of the part whose repair round re-drafted it"""
    out = {}
    for k_part, part in enumerate(CHECK_ORDER):
        f = f"{HERE}/{part}/repair/key.json"
        if os.path.exists(f):
            for k in J(f):
                for u in set(k["replace_no_point"]) | set(k["units"]):
                    out[u] = k_part
    return out


def subclause_spans(item, source_text):
    """[(sub_id, start, end)] of the joined sub-clauses inside item['text'] (located by each sub-clause's first words)."""
    subs, text, spans = item["joined"], item["text"], []
    lines = source_text.split("\n")
    starts = []
    for sid in subs:
        num = sid.split(" ")[-1].split("-")[-1]                      # "EU C7 7.5" -> "7.5"; "SchM-I-19.4.2" -> "19.4.2"; "EU A2 A9" -> "A9"
        line, used = None, num
        for cand in (num, re.sub(r"^[A-Z]+", "", num)):      # "A8" is printed as "8." in EU Annex 2
            line = next((l for l in lines if re.match(rf"^\s*{re.escape(cand)}\.?\s", l)), None)
            if line is not None:
                used = cand; break
        if line is None:
            raise SystemExit(f"REF1: sub-clause {sid} not found in source_text of {item['id']}")
        head = re.sub(rf"^\s*{re.escape(used)}\.?\s+", "", line)[:40]
        pos = text.find(head)
        if pos < 0:
            raise SystemExit(f"REF1: start of {sid} not found in the text of {item['id']}")
        starts.append((sid, pos))
    starts.sort(key=lambda x: x[1])
    for i, (sid, pos) in enumerate(starts):
        spans.append((sid, pos, starts[i + 1][1] if i + 1 < len(starts) else len(text)))
    return spans


def main(apply_split=True, write=True):
    """apply_split: move proof-sample items with split opinions (proof-split.json, 2-of-3 rule) to owner review.
    write=False: only return points.json content (verify.py uses it to compare with the sample's sha256)."""
    D = J(f"{HERE}/full/draft/drafts.json")
    blocks = {b["id"]: b for b in J(f"{HERE}/blocks.json")["blocks"]}
    ck = {x["id"]: x for x in J(f"{ROOT}/merged/checklist.json")}
    cp = {x["id"]: x for x in J(f"{ROOT}/merged/checkpoints.json")}
    src = J(f"{ROOT}/merged/sources.json")["items"]
    hand = J(f"{HERE}/ref-hand.json") if os.path.exists(f"{HERE}/ref-hand.json") else {}
    pst, nst = latest_status()
    rep_np = repaired_np_units()

    unit_of = lambda uid: (uid.rsplit("#", 1)[0], int(uid.rsplit("#", 1)[1]))
    spans = {}
    for iid, it in ck.items():
        if "joined" in it and any(r.get("via") and r["via"] != iid for r in it["references"]):
            spans[iid] = subclause_spans(it, src[iid]["source_text"])

    def refs_for(uids, owner):
        by = collections.defaultdict(list)
        for u in uids:
            i, n = unit_of(u)
            by[i].append(n)
        out = []
        for iid, ns in by.items():
            it = ck[iid]
            udict = {u["n"]: u for u in cp[iid]["units"]}
            duty = {u["n"] for u in cp[iid]["units"] if u["mark"] == "duty"}
            for r in it["references"]:
                keep, why = True, "whole-clause reference (REF1)"
                hk = f"{owner}|{r['ref']}"
                if hk in hand:
                    keep, why = hand[hk]["keep"], "hand: " + hand[hk]["reason"]
                elif "joined" in it and r.get("via") is None:
                    keep = duty <= set(ns)
                    why = "joined item, via unknown: kept only if all duty units covered"
                elif iid in spans and r.get("via"):
                    sp = {s: (a, b) for s, a, b in spans[iid]}
                    a, b = sp[r["via"]]
                    keep = any(a <= udict[n]["start"] < b for n in ns)
                    why = f"joined item: unit inside sub-clause {r['via']}"
                if keep:
                    out.append({"regulator": r["regulator"], "ref": r["ref"], "item": iid, "rule": why})
        return out

    D_block_of = {u: b["id"] for b in blocks.values() for it in b["items"] for u in (x["uid"] for x in it["units"])}
    review, points, others, pending = [], [], [], []
    split = J(f"{HERE}/proof-split.json") if apply_split and os.path.exists(f"{HERE}/proof-split.json") else {"points": {}, "no_point": {}}
    known = J(f"{HERE}/known-errors.json") if apply_split and os.path.exists(f"{HERE}/known-errors.json") else {}
    for p in D["points"]:
        if p["id"] in known:                           # confirmed proof-sample ERROR, no more rounds (owner, option B)
            review.append({"kind": "point", "id": p["id"], "units": p["units"], "question": p["question"], "verify": p["verify"],
                           "evidence": p["evidence"], "why": "confirmed proof-sample ERROR: " + known[p["id"]]})
            continue
        if p["id"] in split["points"]:                 # owner 20 Nov: split opinions -> owner review, out of points.json
            review.append({"kind": "point", "id": p["id"], "units": p["units"], "question": p["question"], "verify": p["verify"],
                           "evidence": p["evidence"], "why": "proof sample: opinions split (2-of-3 rule): " + split["points"][p["id"]]})
            continue
        st = pst.get(p["id"])
        bad = bool(p["problems"]) or not st or not st["ok"]
        if bad and "-R" in p["id"] and not st:          # repaired, not re-checked yet
            pending.append({"kind": "point", "id": p["id"], "why": "repaired, waiting for its re-check"}); continue
        if bad:
            row = {"kind": "point", "id": p["id"], "units": p["units"], "question": p["question"], "verify": p["verify"],
                   "evidence": p["evidence"], "why": "; ".join(filter(None, ["code: " + "; ".join(p["problems"]) if p["problems"] else "",
                                                                          (st or {}).get("why", "not checked yet")]))}
            (review if "-R" in p["id"] else pending).append(row)
            continue
        by = collections.OrderedDict()
        for u in p["units"]:
            i, n = unit_of(u)
            by.setdefault(i, []).append(n)
        points.append({"id": p["id"], "regulator": p["regulator"], "area": p["area"], "system": p["system"],
                       "plant_types": p["plant_types"], "audience": p["audience"], "question": p["question"],
                       "verify": p["verify"], "evidence": p["evidence"], "grade_hint": p["grade_hint"],
                       "modality": p["modality"], "clauses": [{"item": i, "units": ns} for i, ns in by.items()],
                       "references": refs_for(p["units"], p["id"])})
    for x in D["no_point"]:
        st = nst.get(x["unit"])
        if x["unit"] in rep_np and st and st["k"] <= rep_np[x["unit"]]:
            st = None                                  # only a check AFTER its repair counts
        bad = bool(x["problems"]) or not st or not st["ok"]
        if bad and x["unit"] in rep_np and not st:
            pending.append({"kind": "no_point", "id": x["unit"], "why": "repaired, waiting for its re-check"}); continue
        b = blocks[x["block"]]
        if bad:
            row = {"kind": "no_point", "id": x["unit"], "units": [x["unit"]], "reason": x["reason"],
                   "why": (st or {}).get("why", "not checked yet") + (" (MAJOR)" if st and st.get("major") else "")}
            (review if x["unit"] in rep_np else pending).append(row)
            continue
        i, n = unit_of(x["unit"])
        others.append({"item": i, "unit": n, "regulator": b["regulator"], "area": b["area"], "system": b["system"],
                       "plant_types": b["plant_types"], "audience": b["audience"], "reason": x["reason"],
                       "references": refs_for([x["unit"]], x["unit"])})
    for r in review:                                   # owner-review rows get the clause text for the owner
        r["clauses"] = []
        for u in r["units"]:
            i, n = unit_of(u)
            unit = next(v for v in cp[i]["units"] if v["n"] == n)
            r["clauses"].append({"item": i, "ref": ck[i]["ref"], "unit": n, "text": unit["text"]})
    if os.path.exists(f"{HERE}/np-2of3.json"):        # 2-of-3 on all other_requirements: split ones are listed too
        for u in J(f"{HERE}/np-2of3.json")["split"]:
            split["no_point"].setdefault(u, "1 of 3 per-item opinions FAIL (all other_requirements got 2-3 opinions)")
    for u, why in split["no_point"].items():          # split no_point items stay in other_requirements but are listed
        i, n = unit_of(u)
        unit = next(v for v in cp[i]["units"] if v["n"] == n)
        review.append({"kind": "no_point (kept in other requirements)", "id": u, "units": [], "reason": "",
                       "why": "proof sample: opinions split (2-of-3 rule): " + why,
                       "clauses": [{"item": i, "ref": ck[i]["ref"], "unit": n, "text": unit["text"]}]})
    # OWNER-REVIEW FALLBACK (owner/lead 20 Nov): an owner-review POINT is replaced by its code-built exact-text fallback
    # point (full/fallback/drafts.json, id "<old id>-F") when that fallback PASSED its per-item check.
    fb_file = f"{HERE}/full/fallback/drafts.json"
    if apply_split and os.path.exists(fb_file):
        fb = {p["fallback_of"]: p for p in J(fb_file)["points"]}
        keep = []
        for r in review:
            f = fb.get(r["id"]) if r["kind"] == "point" else None
            st = pst.get(f["id"]) if f else None
            if f and st and st["ok"]:
                by = collections.OrderedDict()
                for u in f["units"]:
                    i, n = unit_of(u)
                    by.setdefault(i, []).append(n)
                points.append({"id": f["id"], "regulator": f["regulator"], "area": f["area"], "system": f["system"],
                               "plant_types": f["plant_types"], "audience": f["audience"], "question": f["question"],
                               "verify": f["verify"], "evidence": f["evidence"], "grade_hint": f["grade_hint"],
                               "modality": f["modality"], "clauses": [{"item": i, "units": ns} for i, ns in by.items()],
                               "references": refs_for(f["units"], f["id"])})
            else:
                keep.append(r)
        review[:] = keep
    # OWNER/LEAD 20 Nov: owner-review POINTS that did not pass as a fallback are shown as "Other requirements (check the
    # clause)" (reason below); their record stays in owner-review.json with "resolved". Units already covered by a point
    # are not added again (never-both).
    if apply_split:
        in_points = {f"{c['item']}#{n}" for p in points for c in p["clauses"] for n in c["units"]}
        in_others = {f"{o['item']}#{o['unit']}" for o in others}
        for r in review:
            if r["kind"] not in ("point", "no_point"):      # lead 20 Nov: every duty unit must be VISIBLE
                continue
            r["resolved"] = "shown as other requirement (clause text), owner/lead 20 Nov"
            for u in r["units"]:
                if u in in_points or u in in_others:
                    continue
                i, n = unit_of(u)
                b = blocks[D_block_of[u]]
                others.append({"item": i, "unit": n, "regulator": b["regulator"], "area": b["area"], "system": b["system"],
                               "plant_types": b["plant_types"], "audience": b["audience"],
                               "reason": "owner review: shown as clause text", "references": refs_for([u], u)})
                in_others.add(u)
    out = {"_doc": __doc__, "points": points, "other_requirements": others}
    if not write:
        return out
    json.dump(out, open(f"{HERE}/points.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"_doc": "Items still failing after their ONE repair (owner rule 19 Nov): kept out of points.json; the "
               "clauses stay plain checklist items until the owner decides.", "items": review},
              open(f"{HERE}/owner-review.json", "w"), ensure_ascii=False, indent=1)
    md = ["# Audit layer: items for owner review", "",
          "These items failed the independent check again after their one repair. They are NOT in the audit points; "
          "their clauses stay as plain checklist items until you decide (keep / change / drop).", ""]
    for k, r in enumerate(review, 1):
        md.append(f"## {k}. {r['id']} ({r['kind']})" + (f" - RESOLVED: {r['resolved']}" if r.get("resolved") else ""))
        for c in r["clauses"]:
            md.append(f"- **{c['ref']}** (unit {c['unit']}): {c['text']}")
        if r["kind"] == "point":
            md += [f"- Question: {r['question']}", f"- Verify: {r['verify']}"]
        else:
            md.append(f"- Not made a point because: {r['reason']}")
        md += [f"- Checker: {r['why']}", ""]
    os.makedirs(os.path.dirname(OWNER_MD), exist_ok=True)
    open(OWNER_MD, "w").write("\n".join(md))
    stat = {"points": len(points), "other_requirements": len(others), "owner_review": len(review), "pending": len(pending),
            "pending_items": pending}
    json.dump(stat, open(f"{HERE}/final-status.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in stat.items() if k != "pending_items"}))


if __name__ == "__main__":
    main()
