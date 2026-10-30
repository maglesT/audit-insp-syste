"""Stage 4 (plan 2.5): Layer 2 on library requirements, two blind verifiers per mapping, in session batches.

  python3 tools/ai/verify.py prepare [--status draft]             # verifier batch files for the library mappings
  python3 tools/ai/verify.py ingest <verify run dir>              # verdicts -> verdicts.jsonl and a report
  python3 tools/ai/verify.py apply <verify run dir>               # requirement status: verified / unverified

Each mapping is judged as the customer would read it for that regulator: the requirement's item text plus the
mapping's addendum when its relation is "stricter" or "adds", with the mapping's own strength and plant types,
and the COVERS line naming the quote (the same verifier prompts A and B as the session pilot, D30, D31).
Mappings with the same judged text, quote and plant types (twins, D36) are judged once.

A mapping passes when both verifiers pass it:
  - relation same, stricter or adds: verdict "correct" (the compiled item says exactly what the clause says);
  - relation looser or narrower: the item may ask for more than the clause, which is what the relation says, so
    it passes when the verifier finds strictness "stricter", nothing omitted, and plant types and strength
    right.
A requirement is "verified" when every mapping passes, "unverified" otherwise (adjudication and repair rounds,
D13, take the unverified ones). Verdicts never change the library except through `apply`.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import pilot  # noqa: E402
import runner  # noqa: E402
import sessions  # noqa: E402
from common import normalise  # noqa: E402

ADDS = ("stricter", "adds")


def judged_text(req, m):
    text = req["item_text"].strip()
    return f"{text} {m['addendum'].strip()}" if m["relation"] in ADDS and m["addendum"].strip() else text


def units(reqs):
    """[(key, req id, mapping index, judged mapping)]: one entry per distinct (text, quote, plant types, source
    scope) and every library mapping's key, so twins share one verdict."""
    out = []
    for req in reqs:
        for i, m in enumerate(req["mappings"]):
            text = judged_text(req, m)
            key = json.dumps([text, normalise(m["quote"]), sorted(m["plant_types"]), m["strength"], m["relation"]])
            out.append((key, req["id"], i, {"statement": text, "quote": m["quote"], "strength": m["strength"],
                                            "plant_types": m["plant_types"], "source": m["source"],
                                            "ref": m["clause_ref"], "clause_sha256": m["clause_sha256"],
                                            "relation": m["relation"], "draft": f"{req['id']}#{i}"}))
    return out


def prepare(reqs, sources, clauses_of):
    """The verify run dir: verifier A and B batch files for one judged mapping per key."""
    first, keys = {}, []
    for key, rid, i, m in units(reqs):
        keys.append({"key": key, "requirement": rid, "mapping": i})
        first.setdefault(key, m)
    judged = list(first.values())
    run_dir = sessions.prepare(pilot.verify_requests(judged, sources, clauses_of), "library-verify")
    runner.write_jsonl(run_dir / "judged.jsonl", [{"key": k, **m} for k, m in first.items()])
    runner.write_jsonl(run_dir / "keys.jsonl", keys)
    return run_dir


def passes(answer, relation):
    if relation in ("looser", "narrower"):
        return (answer["strictness"] == "stricter" and not answer["item_omits"].strip()
                and answer["plant_types_ok"] and answer["strength_ok"])
    return answer["verdict"] == "correct"


def verdicts(run_dir):
    """{judged index: {"a": answer or None, "b": answer or None, "pass": bool}} after ingest."""
    judged = runner.read_jsonl(Path(run_dir) / "judged.jsonl")
    out = {n: {"a": None, "b": None} for n in range(len(judged))}
    for r in runner.read_jsonl(Path(run_dir) / "results.jsonl"):
        role, n = r["custom_id"].split("-")[1], int(r["custom_id"].rsplit("-", 1)[1])
        out[n][role] = r["answer"] if r["ok"] else None
    for n, v in out.items():
        rel = judged[n]["relation"]
        v["pass"] = bool(v["a"] and v["b"] and passes(v["a"], rel) and passes(v["b"], rel))
        v["agree"] = bool(v["a"] and v["b"] and passes(v["a"], rel) == passes(v["b"], rel))
    return out


def ingest(run_dir):
    _, summary = sessions.ingest(run_dir, "library-verify")
    v = verdicts(run_dir)
    judged = runner.read_jsonl(Path(run_dir) / "judged.jsonl")
    runner.write_jsonl(Path(run_dir) / "verdicts.jsonl", [{"key": judged[n]["key"], **x} for n, x in v.items()])
    both = [x for x in v.values() if x["a"] and x["b"]]
    rep = {"judged": len(v), "answered_by_both": len(both), "both_pass": sum(x["pass"] for x in both),
           "both_fail": sum(x["agree"] and not x["pass"] for x in both),
           "disagree": sum(not x["agree"] for x in both), "failed_calls": summary["failed"]}
    (Path(run_dir) / "verify-report.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def statuses(reqs, run_dir):
    """{requirement id: "verified" | "unverified"} from a verify run's verdicts."""
    by_key = {json.loads(l)["key"]: json.loads(l)["pass"] for l in
              (Path(run_dir) / "verdicts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    out = {}
    for key, rid, _, _ in units(reqs):
        ok = by_key.get(key, False)
        out[rid] = "verified" if out.get(rid, "verified") == "verified" and ok else "unverified"
    return out


def apply(run_dir, root):
    import model
    reqs = model.requirements(root)
    st = statuses([r for r in reqs if r["status"] != "retired"], run_dir)
    changed = 0
    for path in sorted((Path(root) / "requirements").glob("*.json")):
        doc = model.load_json(path)
        for r in doc["requirements"]:
            if r["id"] in st and r["status"] != st[r["id"]]:
                r["status"] = st[r["id"]]
                changed += 1
        path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"verified": sum(s == "verified" for s in st.values()),
            "unverified": sum(s == "unverified" for s in st.values()), "changed": changed}


def main():
    import layer1
    import model
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["prepare", "ingest", "apply"])
    ap.add_argument("dirs", nargs="*")
    ap.add_argument("--status", default="draft", help="prepare: verify requirements with this status")
    a = ap.parse_args()
    if a.command == "prepare":
        reqs = [r for r in model.requirements() if r["status"] == a.status]
        print(prepare(reqs, layer1.catalog(), layer1.clauses_of))
    elif a.command == "ingest":
        print(json.dumps(ingest(a.dirs[0]), indent=1))
    else:
        print(json.dumps(apply(a.dirs[0], model.LIBRARY), indent=1))


if __name__ == "__main__":
    main()
