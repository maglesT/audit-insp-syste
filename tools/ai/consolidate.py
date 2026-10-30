"""Stage 2 (plan 2.3): consolidate drafted obligations into requirements, cores first, in session rounds (D36).

  python3 tools/ai/consolidate.py start <draft dir>              # new consolidation dir with state.json
  python3 tools/ai/consolidate.py prepare <consolidation dir>    # next round: a session run of one request
  python3 tools/ai/consolidate.py ingest <consolidation dir> <round run dir>
  python3 tools/ai/consolidate.py status <consolidation dir>
  python3 tools/ai/consolidate.py write <consolidation dir>      # library/requirements/, library/coverage/

The obligations are the draft run's mappings (pilot.py ingest-draft). They are consolidated in STEPS: the EU
GMP/PIC/S core first, then the FDA and WHO cores, then the rest (plan 2.3). A round sends at most GROUP
obligations of the earliest step that still has some, never splitting one clause's obligations, together with
every requirement made so far; the answer gives each obligation a requirement (existing, or a new key defined on
first use), a relation and, for "stricter" and "adds", an addendum. Rounds run one after another, because each
round sees the requirements of the rounds before it.

Ingest checks every decision; a bad decision leaves its obligation pending for a later round, with the reason
in state.json, and never changes the library:
  - the obligation was asked in this round and is decided once; the requirement exists or its new key is
    defined once, with a known sub-topic and an item text; a new key's first use is "same";
  - "stricter" and "adds" have an addendum, the other relations have none;
  - item text and addendum pass the option-A text check (tools/library/export.py: no 12-word run of the source,
    no clause or document reference).
Twins (D36) take their lead obligation's decision. New requirements get ids by top topic ("SI-001"), after the
highest id the library and the state already use. Write builds each requirement from its decisions: strength
is the strictest mapping's, plant types the union of the mappings', status "draft" until Layer 2 verifies it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import runner  # noqa: E402
import sessions  # noqa: E402

STEPS = (("EU", "PICS"), ("FDA", "WHO"), ("EMA", "ICH", "INDIA"))
GROUP = 50
RELATIONS = ("same", "stricter", "adds", "looser", "narrower")
RANK = {"optional": 0, "recommended": 1, "mandatory": 2}
NEW_KEY = re.compile(r"^NEW-\d+$")
TOKENS = 32000

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["decisions"],
    "properties": {"decisions": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["obligation", "requirement", "relation", "addendum", "topic", "item_text", "reason"],
        "properties": {
            "obligation": {"type": "string"},
            "requirement": {"type": "string"},
            "relation": {"type": "string", "enum": list(RELATIONS)},
            "addendum": {"type": "string"},
            "topic": {"type": "string"},
            "item_text": {"type": "string"},
            "reason": {"type": "string"}}}}}}


def step_of(regulator):
    return next((i for i, regs in enumerate(STEPS) if regulator in regs), len(STEPS))


def start(draft_dir, sources, root=None):
    """A new consolidation dir (an ai-runs run) whose state.json lists the draft's obligations and twins."""
    draft_dir = Path(draft_dir)
    mappings = runner.read_jsonl(draft_dir / "mappings.jsonl")
    twins_file = draft_dir / "twin-mappings.jsonl"
    twins = runner.read_jsonl(twins_file) if twins_file.exists() else []
    obligations = [{"id": f"O{n:03d}", "regulator": sources[m["source"]]["regulator"], **m}
                   for n, m in enumerate(mappings)]
    order = {(o["source"], o["ref"]): i for i, o in enumerate(obligations)}
    obligations.sort(key=lambda o: (step_of(o["regulator"]), order[(o["source"], o["ref"])], o["id"]))
    state = {"draft": draft_dir.name, "obligations": obligations,
             "twins": [{**t, "lead": f"O{t['twin_of']:03d}"} for t in twins],
             "requirements": [], "decisions": {}, "errors": {}, "rounds": []}
    run_dir = runner.new_run("consolidation")
    save(run_dir, state)
    return run_dir


def load(cons_dir):
    return json.loads((Path(cons_dir) / "state.json").read_text(encoding="utf-8"))


def save(cons_dir, state):
    (Path(cons_dir) / "state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")


def pending(state):
    return [o for o in state["obligations"] if o["id"] not in state["decisions"]]


def next_group(state, size=GROUP):
    """The next round's obligations: the earliest step's pending ones, whole clauses only, at most size (one clause
    with more than size obligations goes alone)."""
    left = pending(state)
    if not left:
        return []
    step = min(step_of(o["regulator"]) for o in left)
    left = [o for o in left if step_of(o["regulator"]) == step]
    group, clause = [], None
    for o in left:
        key = (o["source"], o["ref"])
        if key != clause and len(group) + sum(1 for x in left if (x["source"], x["ref"]) == key) > size and group:
            break
        group.append(o)
        clause = key
    return group


def topic_lines(topic_tree):
    return [f"{sub} ({t['name']})" for t in topic_tree["topics"] for sub in t["sub"]]


def round_input(state, group, sources, topic_tree):
    reqs = [f"{r['id']} [{r['topic']}] ({r['strength']}; {', '.join(r['plant_types'])}) {r['item_text']}"
            for r in state["requirements"]]
    obs = [f"{o['id']} | {o['regulator']}: {sources[o['source']]['title']} | strength {o['strength']} | plant types "
           f"{', '.join(o['plant_types'])}\n  statement: {o['statement']}\n  quote: {o['quote']}" for o in group]
    return ("TOPICS:\n" + "\n".join(topic_lines(topic_tree)) + "\n\nREQUIREMENTS SO FAR:\n"
            + ("\n".join(reqs) if reqs else "(none yet)") + "\n\nOBLIGATIONS TO DECIDE:\n" + "\n".join(obs))


def prompt():
    return (HERE / "prompts" / "consolidate.md").read_text(encoding="utf-8")


def prepare(cons_dir, sources, topic_tree):
    """The next round as a session run (one request); None when every obligation is decided."""
    state = load(cons_dir)
    group = next_group(state)
    if not group:
        return None
    req = runner.Request(f"consolidate-{len(state['rounds']):03d}", prompt(),
                         round_input(state, group, sources, topic_tree), SCHEMA, max_tokens=TOKENS,
                         meta={"consolidation": Path(cons_dir).name, "obligations": [o["id"] for o in group]})
    run_dir = sessions.prepare([req], "consolidate")
    state["rounds"].append({"run": run_dir.name, "obligations": [o["id"] for o in group], "ingested": False})
    save(cons_dir, state)
    return run_dir


def next_ids(state, existing_ids):
    used = {}
    for rid in list(existing_ids) + [r["id"] for r in state["requirements"]]:
        prefix, _, number = rid.partition("-")
        used[prefix] = max(used.get(prefix, 0), int(number))
    return used


def text_findings(text, corpus):
    import export
    return export.check_text(text, corpus) if text.strip() else []


def apply(state, round_ids, answer, known_topics, corpus, existing_ids=()):
    """Apply one round's answer to state. Returns the list of errors (also kept in state["errors"])."""
    by_id = {o["id"]: o for o in state["obligations"]}
    reqs = {r["id"]: r for r in state["requirements"]}
    asked, seen, errors = set(round_ids), set(), {}
    defined = {}
    for d in answer["decisions"]:
        if d["requirement"].startswith("NEW-") and NEW_KEY.match(d["requirement"]) and d["item_text"].strip():
            defined.setdefault(d["requirement"], d)
    used = next_ids(state, existing_ids)
    new_ids, accepted = {}, []
    for d in answer["decisions"]:
        oid, key = d["obligation"], d["requirement"]
        problems = []
        if oid not in asked:
            problems.append("obligation was not asked in this round")
        elif oid in seen:
            problems.append("obligation decided twice")
        seen.add(oid)
        if NEW_KEY.match(key):
            first = defined.get(key)
            if first is None:
                problems.append(f"{key} is never defined with an item text")
            elif first is d:
                if d["relation"] != "same":
                    problems.append("the first use of a new key must be 'same'")
                if d["topic"] not in known_topics or "." not in d["topic"]:
                    problems.append(f"unknown sub-topic {d['topic']!r}")
                problems += [f"item text {f}" for f in text_findings(d["item_text"], corpus)]
            elif d["item_text"].strip() or d["topic"].strip():
                problems.append(f"{key} is defined twice")
        elif key not in reqs:
            problems.append(f"unknown requirement {key!r}")
        elif d["item_text"].strip() or d["topic"].strip():
            problems.append("item text or topic given for an existing requirement")
        if d["relation"] in ("stricter", "adds") and not d["addendum"].strip():
            problems.append(f"relation {d['relation']!r} needs an addendum")
        if d["relation"] not in ("stricter", "adds") and d["addendum"].strip():
            problems.append(f"relation {d['relation']!r} takes no addendum")
        problems += [f"addendum {f}" for f in text_findings(d["addendum"], corpus)]
        if problems and oid in asked:
            errors[oid] = problems
        elif not problems:
            accepted.append(d)
    bad_keys = {d["requirement"] for d in answer["decisions"] if d["obligation"] in errors
                and defined.get(d["requirement"]) is d}
    for d in accepted:
        key = d["requirement"]
        if d["obligation"] in errors:           # also decided another way, which was rejected: ambiguous
            continue
        if key in bad_keys:                     # its definition was rejected: every use waits for a later round
            errors[d["obligation"]] = [f"{key}'s definition was rejected"]
            continue
        if NEW_KEY.match(key) and key not in new_ids:
            first = defined[key]
            prefix = first["topic"].split(".")[0]
            used[prefix] = used.get(prefix, 0) + 1
            new_ids[key] = f"{prefix}-{used[prefix]:03d}"
            reqs[new_ids[key]] = {"id": new_ids[key], "topic": first["topic"], "item_text": first["item_text"],
                                  "strength": by_id[first["obligation"]]["strength"],
                                  "plant_types": list(by_id[first["obligation"]]["plant_types"])}
            state["requirements"].append(reqs[new_ids[key]])
        rid = new_ids.get(key, key)
        o = by_id[d["obligation"]]
        state["decisions"][o["id"]] = {"requirement": rid, "relation": d["relation"], "addendum": d["addendum"],
                                       "reason": d["reason"]}
        r = reqs[rid]
        if RANK[o["strength"]] > RANK[r["strength"]]:
            r["strength"] = o["strength"]
        r["plant_types"] = sorted(set(r["plant_types"]) | set(o["plant_types"]))
        state["errors"].pop(o["id"], None)
    for oid in asked - seen:
        errors[oid] = ["no decision"]
    state["errors"].update(errors)
    return errors


def ingest(cons_dir, run_dir, topic_ids, corpus_of, existing_ids=()):
    """Validate a round's session answer and apply it. Returns {"decided", "errors", "pending"}."""
    state = load(cons_dir)
    run_dir = Path(run_dir)
    rnd = next((r for r in state["rounds"] if r["run"] == run_dir.name), None)
    if rnd is None:
        raise SystemExit(f"{run_dir.name} is not a round of {Path(cons_dir).name}")
    if rnd["ingested"]:
        raise SystemExit(f"{run_dir.name} was ingested already")
    results, _ = sessions.ingest(run_dir, "consolidate")
    res = results[0]
    if not res.ok:
        errors = {oid: [f"round failed: {res.error}"] for oid in rnd["obligations"]}
        state["errors"].update(errors)
    else:
        by_id = {o["id"]: o for o in state["obligations"]}
        corpus = corpus_of(sorted({by_id[oid]["source"] for oid in rnd["obligations"]}),
                           [by_id[oid]["quote"] for oid in rnd["obligations"]])
        errors = apply(state, rnd["obligations"], res.answer, topic_ids, corpus, existing_ids)
    rnd["ingested"] = True
    save(cons_dir, state)
    decided = sum(1 for oid in rnd["obligations"] if oid in state["decisions"])
    return {"decided": decided, "errors": len(errors), "pending": len(pending(state))}


def library_files(state, sources, clauses_of, draft_dir):
    """({top topic: [requirement]}, {source stem: {ref: entry}}) built from the state's decisions."""
    by_id = {o["id"]: o for o in state["obligations"]}
    reqs = {r["id"]: {**r, "parameters": {}, "general": False, "status": "draft", "mappings": []}
            for r in state["requirements"]}
    rows = [(by_id[oid], d) for oid, d in state["decisions"].items()]
    rows += [(t, state["decisions"][t["lead"]]) for t in state["twins"] if t["lead"] in state["decisions"]]
    coverage = {}
    for o, d in rows:
        reqs[d["requirement"]]["mappings"].append({
            "source": o["source"], "clause_ref": o["ref"], "clause_sha256": o["clause_sha256"], "quote": o["quote"],
            "strength": o["strength"], "relation": d["relation"], "plant_types": list(o["plant_types"]),
            "addendum": d["addendum"]})
        entry = coverage.setdefault(Path(o["source"]).stem, {}).setdefault(o["ref"], {"requirements": []})
        if d["requirement"] not in entry["requirements"]:
            entry["requirements"].append(d["requirement"])
    for r in reqs.values():
        r["mappings"].sort(key=lambda m: (m["source"], m["clause_ref"]))
        r["strength"] = max((m["strength"] for m in r["mappings"]), key=RANK.get, default=r["strength"])
        r["plant_types"] = sorted(set().union(*(m["plant_types"] for m in r["mappings"])))
    # drafted clauses with no obligation: not applicable, with the drafter's reason (and their twins)
    requests = {r.custom_id: r for r in sessions.load_requests(draft_dir)}
    topic_file = Path(draft_dir) / "topic.json"
    twins_of = {}
    if topic_file.exists():
        for u in json.loads(topic_file.read_text(encoding="utf-8"))["units"]:
            twins_of[(u["source"], u["ref"])] = [(t["source"], t["ref"]) for t in u["twins"]]
    for res in runner.read_jsonl(Path(draft_dir) / "results.jsonl"):
        if res["ok"] and not res["answer"]["obligations"]:
            meta = requests[res["custom_id"]].meta
            reason = res["answer"]["no_obligation_reason"].strip() or "no obligation"
            for source, ref in [(meta["source"], meta["ref"])] + twins_of.get((meta["source"], meta["ref"]), []):
                coverage.setdefault(Path(source).stem, {}).setdefault(ref, {"na": reason})
    by_topic = {}
    for r in sorted(reqs.values(), key=lambda r: (r["id"].split("-")[0], int(r["id"].split("-")[1]))):
        if r["mappings"]:
            by_topic.setdefault(r["topic"].split(".")[0], []).append(r)
    return by_topic, coverage


def write(cons_dir, root):
    """Merge the consolidation into library/requirements/<TOP>.json and library/coverage/<stem>.json: entries of
    this state replace entries with the same id or clause; everything else in the files is kept."""
    import layer1
    state = load(cons_dir)
    draft_dir = runner.RUNS / state["draft"]
    by_topic, coverage = library_files(state, layer1.catalog(), layer1.clauses_of, draft_dir)
    root = Path(root)
    (root / "requirements").mkdir(parents=True, exist_ok=True)
    (root / "coverage").mkdir(parents=True, exist_ok=True)
    for top, reqs in by_topic.items():
        path = root / "requirements" / f"{top}.json"
        old = json.loads(path.read_text(encoding="utf-8"))["requirements"] if path.exists() else []
        ids = {r["id"] for r in reqs}
        merged = [r for r in old if r["id"] not in ids] + reqs
        path.write_text(json.dumps({"requirements": merged}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for stem, entries in coverage.items():
        path = root / "coverage" / f"{stem}.json"
        old = json.loads(path.read_text(encoding="utf-8"))["clauses"] if path.exists() else {}
        path.write_text(json.dumps({"clauses": {**old, **entries}}, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return {"requirements": sum(len(v) for v in by_topic.values()), "topics": sorted(by_topic),
            "coverage_files": len(coverage)}


def corpus_of(files, quotes):
    import export
    import layer1
    return export.Corpus({f: [s["text"] for s in layer1.segments_of(f) if s["kind"] != "toc"] for f in files}, quotes)


def main():
    import layer1
    import model
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["start", "prepare", "ingest", "status", "write"])
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    if a.command == "start":
        print(start(a.dirs[0], layer1.catalog()))
    elif a.command == "prepare":
        print(prepare(a.dirs[0], layer1.catalog(), model.load_json(model.LIBRARY / "topics.json")) or "all decided")
    elif a.command == "ingest":
        if len(a.dirs) != 2:
            ap.error("ingest takes <consolidation dir> <round run dir>")
        existing = [r["id"] for r in model.requirements()]
        print(json.dumps(ingest(a.dirs[0], a.dirs[1], set(model.topics()), corpus_of, existing)))
    elif a.command == "status":
        s = load(a.dirs[0])
        print(json.dumps({"obligations": len(s["obligations"]), "decided": len(s["decisions"]),
                          "requirements": len(s["requirements"]), "errors": s["errors"],
                          "rounds": len(s["rounds"])}, indent=1))
    else:
        print(json.dumps(write(a.dirs[0], model.LIBRARY)))


if __name__ == "__main__":
    main()
