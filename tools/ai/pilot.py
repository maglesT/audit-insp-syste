"""Paid pilot: measure the real cost per mapping before the full run (D29).

  python3 tools/ai/pilot.py check                 # one tiny call: is the API key accepted?
  python3 tools/ai/pilot.py run [--budget 15]     # draft + two blind verifiers on the self-inspection clauses

Stage 1 (plan 2.2): Opus reads ONE clause and returns its obligations (statement, exact quote, strength, plant
types, numbers). Each quote is checked word for word against the clause (Layer 1 rule 1) before verification.
Stage 4 (plan 2.5): two blind verifiers with differently framed prompts (A: item -> clause, B: clause -> item)
judge every drafted mapping. The run stops before sending anything if the worst-case cost exceeds the budget.
Output: library/ai-runs/<run>/ (audit trail, D29) and pilot-report.json with cost per mapping and agreement.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import runner  # noqa: E402
from common import normalise  # noqa: E402

PROMPTS = HERE / "prompts"
PLANT_TYPES = ["OSD", "LIQ", "SEMI", "INJ", "API"]
DRAFT_TOKENS, VERIFY_TOKENS = 8000, 6000           # output caps, thinking included; a cut-off answer is a failure
# the self-inspection clauses of the pilot regulators: about 25 clauses, about 50 mappings
PILOT = {
    "eu-cap9_en.pdf": ["Chapter 9 Principle", "Chapter 9 9.1", "Chapter 9 9.2", "Chapter 9 9.3"],
    "who-trs986-a2-gmp-main.pdf": [f"8.{n}" for n in range(1, 10)],
    "india-schedule-m-2023-GSR922E.pdf": [f"Part I 10.{n}" for n in range(1, 8)] + ["Part I 10.8.1",
                                                                                  "Part I 10.8.2"],
    "ich-q7.pdf": ["2.40", "2.41"],
}

DRAFT_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["obligations", "no_obligation_reason"],
    "properties": {
        "no_obligation_reason": {"type": "string"},
        "obligations": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["statement", "quote", "strength", "plant_types", "numbers"],
            "properties": {
                "statement": {"type": "string"},
                "quote": {"type": "string"},
                "strength": {"type": "string", "enum": ["mandatory", "recommended", "optional"]},
                "plant_types": {"type": "array", "items": {"type": "string", "enum": PLANT_TYPES}},
                "numbers": {"type": "array", "items": {"type": "string"}}}}}}}

VERIFY_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["required_by_clause", "item_adds", "item_omits", "strictness", "plant_types_ok", "strength_ok",
                 "verdict", "reason"],
    "properties": {
        "required_by_clause": {"type": "boolean"},
        "item_adds": {"type": "string"},
        "item_omits": {"type": "string"},
        "strictness": {"type": "string", "enum": ["same", "stricter", "looser"]},
        "plant_types_ok": {"type": "boolean"},
        "strength_ok": {"type": "boolean"},
        "verdict": {"type": "string", "enum": ["correct", "incorrect"]},
        "reason": {"type": "string"}}}


def prompt(name):
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def clause_block(source, clause, scope):
    heading = f"Section: {clause['section']}\n" if clause.get("section") else ""
    return (f"Source: {source['regulator']} - {source['title']}\nApplies to plant types: {scope}\n{heading}"
            f"Clause {clause['ref']}:\n{clause['text']}")


def draft_requests(pilot, sources, clauses_of):
    out = []
    for file, refs in pilot.items():
        tree = clauses_of(file)
        scope = ", ".join(sorted(runner_scope(sources[file]["applies_to"])))
        for ref in refs:
            clause = tree[ref]
            out.append(runner.Request(f"draft-{len(out):03d}", prompt("draft"),
                                      clause_block(sources[file], clause, scope), DRAFT_SCHEMA,
                                      max_tokens=DRAFT_TOKENS, meta={"source": file, "ref": ref, "clause_sha256": clause["sha256"]}))
    return out


def runner_scope(applies_to):
    return set(PLANT_TYPES) if applies_to.strip() == "ALL" else set(applies_to.split(";"))


def mappings_from(drafts, results, clauses_of):
    """Drafted obligations as mappings; a quote that is not in the clause word for word is rejected here."""
    by_id = {r.custom_id: r for r in results}
    mappings, rejected = [], []
    for req in drafts:
        res = by_id[req.custom_id]
        if not res.ok:
            continue
        clause = clauses_of(req.meta["source"])[req.meta["ref"]]
        for ob in res.answer["obligations"]:
            m = {**req.meta, **ob, "draft": req.custom_id}
            (mappings if normalise(ob["quote"]) in normalise(clause["text"]) else rejected).append(m)
    return mappings, rejected


def verify_requests(mappings, sources, clauses_of):
    out = []
    for n, m in enumerate(mappings):
        clause = clauses_of(m["source"])[m["ref"]]
        scope = ", ".join(sorted(runner_scope(sources[m["source"]]["applies_to"])))
        item = (f"ITEM: {m['statement']}\nStrength: {m['strength']}\n"
                f"Plant types: {', '.join(m['plant_types'])}")
        clause_text = clause_block(sources[m["source"]], clause, scope)
        for role, first, second in (("a", item, clause_text), ("b", clause_text, item)):
            out.append(runner.Request(f"verify-{role}-{n:03d}", prompt(f"verify_{role}"), f"{first}\n\n{second}",
                                      VERIFY_SCHEMA, max_tokens=VERIFY_TOKENS,
                                      meta={"mapping": n, "verifier": role}))
    return out


def report(mappings, rejected, draft_summary, verify_results, verify_summary):
    verdicts = {}
    for r in verify_results:
        if r.ok:
            n, role = int(r.custom_id.rsplit("-", 1)[1]), r.custom_id.split("-")[1]
            verdicts.setdefault(n, {})[role] = r.answer["verdict"]
    both = [v for v in verdicts.values() if len(v) == 2]
    total = draft_summary["cost_usd"] + verify_summary["cost_usd"]
    return {
        "clauses": draft_summary["requests"], "mappings": len(mappings), "quotes_rejected": len(rejected),
        "verified_by_both": len(both),
        "both_correct": sum(v["a"] == v["b"] == "correct" for v in both),
        "both_incorrect": sum(v["a"] == v["b"] == "incorrect" for v in both),
        "disagree": sum(v["a"] != v["b"] for v in both),
        "failed_calls": draft_summary["failed"] + verify_summary["failed"],
        "cost_usd": round(total, 4),
        "cost_per_mapping_usd": round(total / len(mappings), 4) if mappings else None,
        "tokens": {"draft": draft_summary["usage"], "verify": verify_summary["usage"]},
    }


def run(run_with, budget, pilot=PILOT, sources=None, clauses_of=None):
    """run_with: a runner (BatchRunner or MockRunner). Returns the report; writes the audit trail."""
    import layer1
    sources = sources or layer1.catalog()
    clauses_of = clauses_of or layer1.clauses_of
    model = getattr(run_with, "model", runner.MODEL)
    drafts = draft_requests(pilot, sources, clauses_of)
    # verification is two calls per obligation; assume up to 3 obligations per clause for the bound
    per_verify = runner.cost({"input_tokens": 2000, "output_tokens": VERIFY_TOKENS})
    bound = runner.worst_case(drafts) + len(drafts) * 3 * 2 * per_verify
    if bound > budget:
        raise SystemExit(f"worst-case cost US${bound:.2f} is over the budget US${budget:.2f}; nothing was sent")
    d_dir = runner.new_run("pilot-draft")
    d_results = run_with.run(drafts)
    d_summary = runner.record(d_dir, drafts, d_results, model, run_with.batch)
    mappings, rejected = mappings_from(drafts, d_results, clauses_of)
    runner.write_jsonl(d_dir / "mappings.jsonl", mappings)
    runner.write_jsonl(d_dir / "rejected-quotes.jsonl", rejected)
    verifies = verify_requests(mappings, sources, clauses_of)
    spent = d_summary["cost_usd"]
    if spent + runner.worst_case(verifies) > budget:
        raise SystemExit(f"drafting cost US${spent:.2f}; verification could exceed the budget; stopped before it")
    v_dir = runner.new_run("pilot-verify")
    v_results = run_with.run(verifies)
    v_summary = runner.record(v_dir, verifies, v_results, model, run_with.batch)
    rep = report(mappings, rejected, d_summary, v_results, v_summary)
    rep["runs"] = [d_dir.name, v_dir.name]
    (v_dir / "pilot-report.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "run"])
    ap.add_argument("--budget", type=float, default=15.0, help="US$; nothing is sent above this worst case")
    args = ap.parse_args()
    if args.command == "check":
        print("API key accepted; model:", runner.check_access())
        return
    print(json.dumps(run(runner.BatchRunner(), args.budget), indent=1))


if __name__ == "__main__":
    main()
