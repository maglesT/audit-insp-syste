"""Mutation test (plan 2.6, Layer 3) at pilot scale: do Layer 1 and the two blind verifiers catch planted errors?

  python3 tools/ai/mutate.py prepare-text <draft dir>                  # mutator batch for the text mutants
  python3 tools/ai/mutate.py prepare-verify <draft dir> <mutator dir>  # mutants + controls, shuffled, verifier batches
  python3 tools/ai/mutate.py agents <run dir> <model>                  # record which model answered the batches
  python3 tools/ai/mutate.py report <verify dir>                       # ingest verifier answers, mutation-report.json

Mutants are made from the correct mappings of a session-draft run, PER_TYPE per error type where the mappings
allow. Four types are made by code (changed number, strength, plant type, wrong clause); three are rewritten by a
mutator agent that sees only the item and its clause (dropped condition, added condition, looser wording). Every
untouched mapping is a control. Mutants and controls are shuffled together and go to the verifiers with exactly
the pilot's prompts and inputs, so the verifiers cannot tell them apart. The key (which item is which) is kept in
mutation-key.jsonl in the verify run folder; the verifier agents only ever see their own batch file.
"""
import argparse
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import pilot  # noqa: E402
import runner  # noqa: E402
import sessions  # noqa: E402

SEED = 26
PER_TYPE = 15
CODE_TYPES = ("changed_number", "strength", "plant_type", "wrong_clause")
TEXT_TYPES = {"dropped_condition": "dropped condition", "added_condition": "added condition",
              "looser_wording": "looser wording"}
TYPES = CODE_TYPES + tuple(TEXT_TYPES)
TEXT_ASKED = {"dropped_condition": None, "added_condition": 18, "looser_wording": 18}   # None: every mapping
# the clause the session pilot split into evaluation and criteria; its dropped-condition mutants always go in
FORCED = {"dropped_condition": [("who-trs986-a2-gmp-main.pdf", "8.9")]}

MUTATOR_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["possible", "statement", "change"],
    "properties": {"possible": {"type": "boolean"}, "statement": {"type": "string"}, "change": {"type": "string"}}}

FLIP = {"recommended": "mandatory", "mandatory": "recommended", "optional": "mandatory"}
MODAL = {"recommended": {"should": "must"}, "mandatory": {"must": "should", "shall": "should"},
         "optional": {"may": "must"}}
NUMBER_WORDS = {"once": "twice", "twice": "once", "one": "two", "two": "three", "three": "four", "four": "five",
                "five": "six", "six": "seven", "seven": "eight", "eight": "nine", "nine": "ten", "ten": "twelve",
                "twelve": "ten", "fifteen": "twenty"}
DIGITS = re.compile(r"(?<![\w.])\d+(?![\w.]*\d)")
WORD = re.compile(r"\b(" + "|".join(NUMBER_WORDS) + r")\b", re.I)


def _case(new, old):
    return new[:1].upper() + new[1:] if old[:1].isupper() else new


def change_number(statement):
    """The statement with its first number changed, or None when it has no number."""
    m = DIGITS.search(statement)
    if m:
        return statement[:m.start()] + str(int(m.group()) + 1) + statement[m.end():]
    m = WORD.search(statement)
    if m:
        return statement[:m.start()] + _case(NUMBER_WORDS[m.group().lower()], m.group()) + statement[m.end():]
    return None


def change_strength(m):
    """(strength, statement): the label flipped, and a modal verb in the statement flipped with it."""
    statement = m["statement"]
    for old, new in MODAL[m["strength"]].items():
        statement = re.sub(rf"\b{old}\b", lambda x, new=new: _case(new, x.group()), statement, flags=re.I)
    return FLIP[m["strength"]], statement


def outside_scope(applies_to):
    """A plant type outside the source's scope, or None when the source covers every type."""
    scope = pilot.runner_scope(applies_to)
    return next((p for p in pilot.PLANT_TYPES if p not in scope), None)


def other_clause(m, clauses_of, rng, avoid):
    """(ref, clause) of another clause of the same source with some text, preferably not one the pilot drafted;
    None when the source has no other clause."""
    tree = clauses_of(m["source"])
    others = sorted(r for r, c in tree.items() if r != m["ref"] and len(c["text"]) >= 80)
    refs = [r for r in others if r not in avoid] or others
    if not refs:
        return None
    ref = rng.choice(refs)
    return ref, tree[ref]


def code_mutants(mappings, sources, clauses_of, rng):
    """{type: [mutant]} for the four types made by code."""
    out = {t: [] for t in CODE_TYPES}
    drafted = {m["ref"] for m in mappings}
    order = list(range(len(mappings)))
    rng.shuffle(order)
    for i in order:
        m = mappings[i]
        statement = change_number(m["statement"])
        if statement and len(out["changed_number"]) < PER_TYPE:
            out["changed_number"].append(mutant("changed_number", i, {**m, "statement": statement},
                                                "first number in the item changed"))
        if len(out["strength"]) < PER_TYPE:
            strength, statement = change_strength(m)
            out["strength"].append(mutant("strength", i, {**m, "strength": strength, "statement": statement},
                                          f"strength {m['strength']} -> {strength}"))
        extra = outside_scope(sources[m["source"]]["applies_to"])
        if extra and len(out["plant_type"]) < PER_TYPE:
            out["plant_type"].append(mutant("plant_type", i, {**m, "plant_types": sorted(m["plant_types"] + [extra])},
                                            f"plant type {extra} added"))
        other = other_clause(m, clauses_of, rng, drafted) if len(out["wrong_clause"]) < PER_TYPE else None
        if other:
            ref, clause = other
            out["wrong_clause"].append(mutant("wrong_clause", i, {**m, "ref": ref, "clause_sha256": clause["sha256"]},
                                              f"cited {ref} instead of {m['ref']}"))
    return out


def mutant(kind, original, mapping, change):
    return {"type": kind, "original": original, "mapping": mapping, "change": change}


def text_requests(mappings, sources, clauses_of, rng=None):
    """Mutator requests: every mapping for a dropped condition, a seeded sample for the other two types."""
    rng = rng or random.Random(SEED)
    out = []
    for kind, label in TEXT_TYPES.items():
        n = TEXT_ASKED[kind]
        chosen = range(len(mappings)) if n is None else sorted(rng.sample(range(len(mappings)), min(n, len(mappings))))
        for i in chosen:
            m = mappings[i]
            clause = clauses_of(m["source"])[m["ref"]]
            scope = ", ".join(sorted(pilot.runner_scope(sources[m["source"]]["applies_to"])))
            user = (f"CHANGE: {label}\n\nITEM: {m['statement']}\nStrength: {m['strength']}\n"
                    f"Plant types: {', '.join(m['plant_types'])}\n\n"
                    f"{pilot.clause_block(sources[m['source']], clause, scope)}")
            out.append(runner.Request(f"mutate-{kind}-{i:03d}", pilot.prompt("mutate"), user, MUTATOR_SCHEMA,
                                      max_tokens=2000, meta={"type": kind, "mapping": i, "source": m["source"],
                                                             "ref": m["ref"]}))
    return out


def text_mutants(mappings, results, requests):
    """{type: [mutant]} from the mutator answers: possible, non-empty and really different from the item."""
    by_id = {r.custom_id: r for r in results}
    candidates = {t: [] for t in TEXT_TYPES}
    for req in requests:
        res = by_id.get(req.custom_id)
        if not res or not res.ok or not res.answer["possible"]:
            continue
        i, kind = req.meta["mapping"], req.meta["type"]
        statement = res.answer["statement"].strip()
        if not statement or pilot.normalise(statement) == pilot.normalise(mappings[i]["statement"]):
            continue
        candidates[kind].append(mutant(kind, i, {**mappings[i], "statement": statement}, res.answer["change"]))
    out = {}
    for kind, found in candidates.items():
        forced = [c for c in found if (c["mapping"]["source"], c["mapping"]["ref"]) in FORCED.get(kind, [])]
        rest = [c for c in found if c not in forced]
        random.Random(f"{SEED}-{kind}").shuffle(rest)
        out[kind] = (forced + rest)[:max(PER_TYPE, len(forced))]
    return out


def layer1_findings(m, sources):
    """Layer 1 checks of one mapping, as a one-mapping requirement: [(check, message)]."""
    import layer1
    req = {"id": "MUT-001", "item_text": m["statement"], "strength": m["strength"], "plant_types": m["plant_types"],
           "parameters": {}, "general": False,
           "mappings": [{"source": m["source"], "clause_ref": m["ref"], "clause_sha256": m["clause_sha256"],
                         "quote": m["quote"], "strength": m["strength"], "relation": "same",
                         "plant_types": m["plant_types"], "addendum": ""}]}
    return [[check, msg] for _, _, check, msg in layer1.check_requirement(req, sources)]


def build(mappings, code, text, sources, rng):
    """Mutants and controls, shuffled, each with its Layer 1 findings: the key rows."""
    items = [{"type": "control", "original": i, "mapping": m, "change": ""} for i, m in enumerate(mappings)]
    for group in list(code.values()) + list(text.values()):
        items += group
    rng.shuffle(items)
    counts = {}
    for n, it in enumerate(items):
        counts[it["type"]] = counts.get(it["type"], 0) + 1
        it["id"] = f"{it['type']}-{counts[it['type']]:03d}"
        it["position"] = n
        it["layer1"] = layer1_findings(it["mapping"], sources)
    return items


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare_text(draft_dir, sources=None, clauses_of=None):
    import layer1
    mappings = runner.read_jsonl(Path(draft_dir) / "mappings.jsonl")
    reqs = text_requests(mappings, sources or layer1.catalog(), clauses_of or layer1.clauses_of)
    return sessions.prepare(reqs, "mutator")


def prepare_verify(draft_dir, mutator_dir, sources=None, clauses_of=None):
    """Ingest the mutator answers, build mutants and controls, and write the verifier batches."""
    import layer1
    sources, clauses_of = sources or layer1.catalog(), clauses_of or layer1.clauses_of
    draft_dir, mutator_dir = Path(draft_dir), Path(mutator_dir)
    mappings = runner.read_jsonl(draft_dir / "mappings.jsonl")
    results, _ = sessions.ingest(mutator_dir, "mutator")
    rng = random.Random(SEED)
    code = code_mutants(mappings, sources, clauses_of, rng)
    text = text_mutants(mappings, results, sessions.load_requests(mutator_dir))
    items = build(mappings, code, text, sources, rng)
    verify_dir = sessions.prepare(pilot.verify_requests([it["mapping"] for it in items], sources, clauses_of),
                                  "mutation-verify")
    runner.write_jsonl(verify_dir / "mutation-key.jsonl", items)
    (verify_dir / "mutation-link.json").write_text(json.dumps(
        {"draft_run": draft_dir.name, "mappings_sha256": _sha256(draft_dir / "mappings.jsonl"),
         "mutator_run": mutator_dir.name, "seed": SEED}) + "\n", encoding="utf-8")
    return verify_dir


def record_agents(run_dir, model):
    """agents.json: the model that answered each batch file of a session run."""
    run_dir = Path(run_dir)
    rows = {b.name: model for b in sorted((run_dir / "batches").glob("batch_*.json"))}
    (run_dir / "agents.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return rows


def wilson_lower(k, n, z=1.96):
    """95 % Wilson lower bound of a proportion k/n."""
    if n == 0:
        return None
    p = k / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round((centre - spread) / (1 + z * z / n), 3)


def summarise(items, verdicts):
    """Per type: n, caught by Layer 1 / A / B / any, missed rows; controls: false alarms. verdicts:
    {position: {"a": answer, "b": answer}} (an answer may be missing when its call failed)."""
    rows, missed = {}, {}
    for it in items:
        v = verdicts.get(it["position"], {})
        flags = {"layer1": bool(it["layer1"]),
                 "a": v.get("a", {}).get("verdict") == "incorrect",
                 "b": v.get("b", {}).get("verdict") == "incorrect"}
        flags["any"] = any(flags.values())
        flags["verifiers"] = flags["a"] or flags["b"]
        complete = "a" in v and "b" in v
        row = rows.setdefault(it["type"], {"n": 0, "verified": 0, "layer1": 0, "a": 0, "b": 0, "verifiers": 0,
                                           "any": 0})
        row["n"] += 1
        row["verified"] += complete
        for k in ("layer1", "a", "b", "verifiers", "any"):
            row[k] += flags[k]
        if it["type"] != "control" and not flags["any"]:
            missed.setdefault(it["type"], []).append({
                "id": it["id"], "source": it["mapping"]["source"], "ref": it["mapping"]["ref"],
                "change": it["change"], "statement": it["mapping"]["statement"],
                "reason_a": v.get("a", {}).get("reason", ""), "reason_b": v.get("b", {}).get("reason", "")})
    for kind, row in rows.items():
        k = row["n"] - row["any"] if kind == "control" else row["any"]
        row["any_rate" if kind != "control" else "clean_rate"] = round(k / row["n"], 3)
        if kind != "control":
            row["any_lower95"] = wilson_lower(row["any"], row["n"])
            row["verifiers_rate"] = round(row["verifiers"] / row["n"], 3)
    return rows, missed


def report(verify_dir):
    verify_dir = Path(verify_dir)
    results, summary = sessions.ingest(verify_dir, "mutation-verify")
    items = runner.read_jsonl(verify_dir / "mutation-key.jsonl")
    verdicts = {}
    for r in results:
        if r.ok:
            role, n = r.custom_id.split("-")[1], int(r.custom_id.rsplit("-", 1)[1])
            verdicts.setdefault(n, {})[role] = r.answer
    rows, missed = summarise(items, verdicts)
    control = rows.get("control", {"n": 0, "a": 0, "b": 0, "verifiers": 0, "layer1": 0})
    rep = {"by_type": {t: rows[t] for t in TYPES + ("control",) if t in rows}, "missed": missed,
           "false_alarms": {k: round(control[k] / control["n"], 3) if control["n"] else None
                            for k in ("layer1", "a", "b", "verifiers")},
           "failed_calls": summary["failed"], "items": len(items)}
    (verify_dir / "mutation-report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["prepare-text", "prepare-verify", "agents", "report"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    need = {"prepare-text": 1, "prepare-verify": 2, "agents": 2, "report": 1}[a.command]
    if len(a.args) != need:
        ap.error(f"{a.command} takes {need} argument(s)")
    if a.command == "prepare-text":
        print(prepare_text(a.args[0]))
    elif a.command == "prepare-verify":
        print(prepare_verify(*a.args))
    elif a.command == "agents":
        print(json.dumps(record_agents(*a.args), indent=1))
    else:
        rep = report(a.args[0])
        print(json.dumps({k: rep[k] for k in ("by_type", "false_alarms", "failed_calls", "items")}, indent=1))


if __name__ == "__main__":
    main()
