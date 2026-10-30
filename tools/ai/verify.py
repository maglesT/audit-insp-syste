"""Stage 4 (plan 2.5): Layer 2 on library requirements, two blind verifiers per mapping, in session batches.

  python3 tools/ai/verify.py prepare [--status draft]             # verifier batch files for the library mappings
  python3 tools/ai/verify.py ingest <verify run dir>              # verdicts -> verdicts.jsonl and a report
  python3 tools/ai/verify.py apply <verify run dir>               # requirement status: verified / unverified

Each item is judged against its own source clause (D37): the item text with the mapping's strength and plant
types, and the COVERS line naming the quote (the same verifier prompts A and B as the session pilot, D30, D31).
Items with the same text, quote, strength and plant types (twins, D36) are judged once.

An item passes when both verifiers answer "correct". It is "verified" when it passes and has no Layer 1 finding
and no option-A finding in its text (`blocked`), "unverified" otherwise
(adjudication and repair rounds, D13, take the unverified ones). Verdicts change the library only through `apply`.
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

def judged_text(req, m):
    return req["item_text"].strip()


def units(reqs):
    """[(key, item id, mapping index, judged mapping)] for every library mapping; twins share a key and so one
    verdict."""
    out = []
    for req in reqs:
        for i, m in enumerate(req["mappings"]):
            text = judged_text(req, m)
            key = json.dumps([text, normalise(m["quote"]), sorted(m["plant_types"]), m["strength"]])
            out.append((key, req["id"], i, {"statement": text, "quote": m["quote"], "strength": m["strength"],
                                            "plant_types": m["plant_types"], "source": m["source"],
                                            "ref": m["clause_ref"], "clause_sha256": m["clause_sha256"],
                                            "draft": f"{req['id']}#{i}"}))
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


def passes(answer):
    return answer["verdict"] == "correct"


def verdicts(run_dir):
    """{judged index: {"a": answer or None, "b": answer or None, "pass": bool}} after ingest."""
    judged = runner.read_jsonl(Path(run_dir) / "judged.jsonl")
    out = {n: {"a": None, "b": None} for n in range(len(judged))}
    for r in runner.read_jsonl(Path(run_dir) / "results.jsonl"):
        role, n = r["custom_id"].split("-")[1], int(r["custom_id"].rsplit("-", 1)[1])
        out[n][role] = r["answer"] if r["ok"] else None
    for n, v in out.items():
        v["pass"] = bool(v["a"] and v["b"] and passes(v["a"]) and passes(v["b"]))
        v["agree"] = bool(v["a"] and v["b"] and passes(v["a"]) == passes(v["b"]))
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


def blocked(reqs, root):
    """{item id: reasons} for items that may not be verified whatever Layer 2 says: a Layer 1 finding, or an
    option-A finding in the item text (it would reach a customer)."""
    import export
    import layer1
    sources = layer1.catalog()
    out = {}
    for req in reqs:
        for rid, _, check, why in layer1.check_requirement(req, sources):
            out.setdefault(rid, []).append(f"layer 1 {check}: {why}")
    for f in export.check_library(root, drafts=True):
        rid, _, why = f.partition(": ")
        out.setdefault(rid, []).append(f"option A: {why}")
    return out


def apply(run_dir, root):
    """Set each judged item's status: verified only when both verifiers pass it and nothing blocks it."""
    import model
    reqs = [r for r in model.requirements(root) if r["status"] != "retired"]
    st = statuses(reqs, run_dir)
    stop = blocked(reqs, root)
    st = {rid: "unverified" if rid in stop else s for rid, s in st.items()}
    changed = 0
    for path in sorted((Path(root) / "requirements").glob("*.json")):
        doc = model.load_json(path)
        for r in doc["requirements"]:
            if r["id"] in st and r["status"] != st[r["id"]]:
                r["status"] = st[r["id"]]
                changed += 1
        path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"verified": sum(s == "verified" for s in st.values()),
            "unverified": sum(s == "unverified" for s in st.values()), "blocked": len(stop), "changed": changed}


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
