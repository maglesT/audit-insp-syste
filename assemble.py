"""AUDIT LAYER step 3: code checks on the drafted points (no API). Usage: python3 -I assemble.py <draftDir>
Reads <draftDir>/raw.json (layer.mjs collect) + blocks.json. Writes <draftDir>/drafts.json and prints a summary.

Code checks per point (problems listed on the point; a point with problems is not sent to the blind check):
 A1 units non-empty; every unit id exists in the point's own block and is a DUTY unit.
 A2 modality: unit is SHOULD if it has "should" and no shall/must/required/"is to"/"are to"; a point must not mix
    SHOULD and MUST units; a SHOULD point's question carries "(recommended)"; a MUST point must not.
 A3 evidence has 1-4 entries; question ends with "?"; verify starts with "Verify that" or with a condition clause
    followed by ", verify that" (R3p: "Where X is done, verify that ...").
 A5 no_point (owner 19 Nov): a DUTY unit may instead be listed in the block's "no_point" with a reason; coverage =
    point OR no_point; the blind check judges each no_point.
 A7 a should-point (modality from the model) must not use must / shall / required in question or verify.
 A8 (proof sample 20 Nov): if a covered unit says minimise / as far as possible / where possible / preferably /
    normally / generally, the QUESTION keeps that qualifier (or a close word); else the question hardens the duty.
 A9 (lead 20 Nov): in a should-point EVERY verify sentence carries "(recommended)" (a9.py splitter).
 A10 (lead 20 Nov): a unit's scope negation / exclusion ("not covered", "does not apply", "not applicable",
    "excluded", "except", "other than", "with the exception of") is kept in the question or verify.
 A11 (lead 20 Nov): "(recommended)" never on a point whose units have a must/shall/required duty word and no
    should / may / can / could / permitted wording.
 A6 a duty unit is covered by points OR listed in no_point, never both (lead ruling for the site).
 A4 copy guard: no run of 10+ consecutive words of a unit text inside the QUESTION (own words). The verify sentence
    may keep the regulation's exact terms (precision for the no-less rule; Schedule M / FDA / EU text may be shown);
    its longest copied run is stored as "verify_copy_run" for information. (Decision reported to the lead 19 Nov.)
 A2 modality per unit: shall/must/is|are|be required/is to be -> must; should alone -> should; no modal word -> the
    modality of the nearest earlier modal unit (or lead-in) of the same item (list entries); none -> must.
 N1 format only: "...? (recommended)" is rewritten "... (recommended)?".
Per block: every DUTY unit covered by >= 1 point (missing units listed in "uncovered"); a block with an API error is
listed in "errors" (all its duty units uncovered).
Point metadata (area, system, plant_types, audience, regulator) is copied from the block (blocks are uniform: B1).
"""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
MUST = re.compile(r"\b(shall|must|(is|are|be) required|is to be|are to be|have to|has to)\b", re.I)
SHOULD = re.compile(r"\bshould\b", re.I)
NEG = [(r"\bnot (be )?covered\b", r"\bnot (be )?covered|\bexclud|\bdo(es)? not (apply|cover)|\boutside\b"),
       (r"\bdo(es)? not apply\b", r"\bdo(es)? not apply|\bnot appl|\bexclud|\bexcept"),
       (r"\bnot applicable\b", r"\bnot appl|\bdo(es)? not apply|\bexclud"),
       (r"\bexclud(ed|es|ing)\b", r"\bexclud|\bnot (be )?covered|\bdo(es)? not (apply|cover)|\bexcept|\bother than"),
       (r"\bexcept\b", r"\bexcept|\bunless|\bother than|\bexclud|\bnot\b"),
       (r"\bother than\b", r"\bother than|\bexcept|\bexclud|\bnot\b"),
       (r"\bwith the exception of\b", r"\bexcept|\bexclud|\bother than|\bnot\b")]
PERMIT = re.compile(r"\bmay\b|\bcan\b|\bcould\b|\bpermitted\b", re.I)
SOFT = [(r"\bminimi[sz]", r"\b(minimi[sz]|reduc|limit|low|as little|risk)"),
        (r"\bas far as (is )?(possible|practicable)", r"\b(as far as|possible|practicable)"),
        (r"\bwhere(ver)? (possible|practicable|feasible)", r"\b(possible|practicable|feasible)"),
        (r"\bpreferabl", r"\bpreferabl"), (r"\bnormally\b", r"\bnormally\b"), (r"\bgenerally\b", r"\bgenerally\b")]
W = lambda s: re.findall(r"[a-z0-9]+", s.lower())


def modality(text, inherit="must"):
    """must / should / None (no modal word: the unit inherits the modality of the nearest earlier modal unit of its
    item, e.g. list entries "i. Allow ..." under "The system should be designed to:"; none earlier -> must)."""
    m, s = MUST.search(text), SHOULD.search(text)
    if s and not m:
        return "should"
    if m:
        return "must"
    return inherit


def unit_modalities(block):
    out = {}
    for it in block["items"]:
        cur = "must"
        if it.get("lead"):
            cur = modality(it["lead"], cur)
        for u in it["units"]:
            cur = modality(u["text"], cur)
            out[u["uid"]] = cur
    return out


def longest_run(unit_text, out_text):
    u, o = W(unit_text), " " + " ".join(W(out_text)) + " "
    best = 0
    for i in range(len(u)):
        n = best + 1
        while i + n <= len(u) and " " + " ".join(u[i:i + n]) + " " in o:
            best = n; n += 1
    return best


def copied(unit_text, out_text, n=10):
    u, o = W(unit_text), " ".join(W(out_text))
    return any(" ".join(u[i:i + n]) in o for i in range(0, max(0, len(u) - n + 1)))


def main(d):
    raw = json.load(open(f"{d}/raw.json"))
    blocks = {b["id"]: b for b in json.load(open(f"{HERE}/blocks.json"))["blocks"]}
    points, uncovered, errors, no_point = [], [], [], []
    for r in raw["results"]:
        b = blocks[r["id"]]
        units = {u["uid"]: u for it in b["items"] for u in it["units"]}
        umod = unit_modalities(b)
        duty = [u for u in units if units[u]["mark"] == "duty"]
        if r.get("error"):
            errors.append({"block": b["id"], "error": r["error"]}); uncovered += [{"block": b["id"], "unit": u} for u in duty]
            continue
        cov, npl = set(), set()
        for x in r["data"].get("no_point", []):
            prob = []
            if x["unit"] not in units or units[x["unit"]]["mark"] != "duty":
                prob.append(f"A1 no_point unit unknown or not DUTY {x['unit']}")
            else:
                npl.add(x["unit"])
            no_point.append({"block": b["id"], "unit": x["unit"], "reason": x["reason"], "problems": prob})
        for k, p in enumerate(r["data"]["points"], 1):
            prob = []
            q = p["question"].strip()                    # N1 format only: "...? (recommended)" -> "... (recommended)?"
            if re.search(r"\?\s*\(recommended\)\.?$", q, re.I):
                p["question"] = re.sub(r"\?\s*\(recommended\)\.?$", " (recommended)?", q, flags=re.I)
            if not p["units"]:
                prob.append("A1 no units")
            for u in p["units"]:
                if u not in units:
                    prob.append(f"A1 unknown unit {u}")
                elif units[u]["mark"] != "duty":
                    prob.append(f"A1 INFO unit listed {u}")
            ok_units = [u for u in p["units"] if u in units and units[u]["mark"] == "duty"]
            mods = {umod[u] for u in ok_units}
            code_mod = "mixed" if len(mods) > 1 else (mods.pop() if mods else "must")
            mod = p.get("modality") or code_mod          # full run: the model's field; the blind check judges it
            if "modality" not in p and mod == "mixed":
                prob.append("A2 mixes should and must units")
            rec = "(recommended)" in p["question"].lower()
            if mod == "should" and not rec:
                prob.append("A2 should-point without (recommended)")
            if mod == "should" and re.search(r"\b(must|shall|as required|(is|are|be) required)\b", p["question"] + " " + p["verify"], re.I):
                prob.append("A7 should-point uses must/shall/required")
            if mod == "must" and rec:
                prob.append("A2 must-point marked (recommended)")
            ut = " ".join(units[u]["text"] for u in ok_units)        # A8 (proof sample 20 Nov): question keeps softeners
            for sa, sb in SOFT:
                if re.search(sa, ut, re.I) and not re.search(sb, p["question"], re.I):
                    prob.append(f"A8 question drops the qualifier '{sa}'"); break
            ut2 = " ".join(units[u]["text"] for u in ok_units)    # A10 (lead 20 Nov): scope negation kept
            for na, nb in NEG:
                if re.search(na, ut2, re.I) and not re.search(nb, p["question"] + " " + p["verify"], re.I):
                    prob.append(f"A10 drops the scope negation '{na}'"); break
            if rec and not any(SHOULD.search(units[u]["text"]) or PERMIT.search(units[u]["text"]) for u in ok_units) \
                    and any(MUST.search(units[u]["text"]) for u in ok_units):
                prob.append("A11 (recommended) on must-only units")      # A11 (lead 20 Nov)
            if mod == "should":                                    # A9 (lead 20 Nov): every verify sentence marked
                from a9 import unmarked
                if unmarked(p["verify"]):
                    prob.append("A9 should-point verify sentence without (recommended)")
            if not 1 <= len(p["evidence"]) <= 4:
                prob.append("A3 evidence count")
            if not p["question"].strip().endswith("?"):
                prob.append("A3 question without ?")
            if not re.match(r"(verify that|(where|when|if|for|in|unless|before|after)\b.*?,\s*verify that)", p["verify"].strip(), re.I):
                prob.append("A3 verify does not start 'Verify that'")
            for u in ok_units:
                if copied(units[u]["text"], p["question"]):
                    prob.append(f"A4 question copies 10+ words of {u}")
            p["verify_copy_run"] = max([longest_run(units[u]["text"], p["verify"]) for u in ok_units] or [0])
            cov |= set(ok_units)
            # point ids: kept when given (merge.py keeps ids stable), else <block>-P<k>
            points.append({"id": p.get("id") or f"{b['id']}-P{k:02d}", "block": b["id"], "regulator": b["regulator"], "part": b["part"],
                           "path": b["path"], "area": b["area"], "system": b["system"], "plant_types": b["plant_types"],
                           "audience": b["audience"], **p, "modality": mod, "code_modality": code_mod, "problems": prob})
        uncovered += [{"block": b["id"], "unit": u} for u in duty if u not in cov and u not in npl]
        for x in no_point:                            # A6 (lead 19 Nov): a duty unit is in a point OR no_point, never both
            if x["block"] == b["id"] and x["unit"] in cov:
                x["problems"].append("A6 unit is also covered by a point")
    nd = sum(1 for b in blocks.values() if b["id"] in {r["id"] for r in raw["results"]}
             for it in b["items"] for u in it["units"] if u["mark"] == "duty")
    pc = collections.Counter(re.sub(r" .*", "", x) for p in points for x in p["problems"])
    summary = {"blocks": len(raw["results"]), "api_errors": len(errors), "points": len(points),
               "points_with_problems": sum(1 for p in points if p["problems"]), "problem_classes": pc,
               "no_point_with_problems": sum(1 for x in no_point if x["problems"]),
               "duty_units": nd, "uncovered": len(uncovered), "no_point": len(no_point),
               "no_point_pct": round(100 * len(no_point) / max(1, nd), 2),
               "units_per_point": round(sum(len(p["units"]) for p in points) / max(1, len(points)), 2),
               "grade_hint": collections.Counter(p["grade_hint"] for p in points),
               "modality": collections.Counter(p["modality"] for p in points), "usage": raw.get("usage")}
    json.dump({"summary": summary, "errors": errors, "uncovered": uncovered, "no_point": no_point, "points": points},
              open(f"{d}/drafts.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"))
