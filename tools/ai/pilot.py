"""Paid pilot: measure the real cost per mapping before the full run (D29).

  python3 tools/ai/pilot.py check                 # one tiny call: is the API key accepted?
  python3 tools/ai/pilot.py run [--budget 15]     # draft + two blind verifiers on the self-inspection clauses

In Claude Code sessions (D30; the API commands above stay, unused), agents answer the batch files in between:
  python3 tools/ai/pilot.py prepare-draft [--topic self-inspection]   # S3: units of topic.py; twins by D36
  python3 tools/ai/pilot.py ingest-draft <draft dir>
  python3 tools/ai/pilot.py prepare-verify <draft dir>
  python3 tools/ai/pilot.py ingest-verify <verify dir> <draft dir>

Stage 1 (plan 2.2): Opus reads ONE clause and returns its obligations (statement, exact quote, strength, plant
types, numbers). Each quote is checked word for word against the clause (Layer 1 rule 1) before verification.
Stage 4 (plan 2.5): two blind verifiers with differently framed prompts (A: item -> clause, B: clause -> item)
judge every drafted mapping. The run stops before sending anything if the worst-case cost exceeds the budget.
Coverage (D30): every obligation sentence of a drafted clause must be covered by that clause's mapping quotes;
a sentence with less than COVERED_SHARE of its words inside a quote is reported as uncovered.
Output: library/ai-runs/<run>/ (audit trail, D29) and pilot-report.json with cost per mapping and agreement.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import obligations  # noqa: E402
import runner  # noqa: E402
import sessions  # noqa: E402
from common import normalise  # noqa: E402

PROMPTS = HERE / "prompts"
PLANT_TYPES = ["OSD", "LIQ", "SEMI", "INJ", "API"]
MIN_QUOTE_WORDS = 3                                 # an empty or one-word "quote" is always found; it proves nothing
COVERED_SHARE = 0.8                                 # share of a sentence's words that must lie inside a quote
DRAFT_TOKENS, VERIFY_TOKENS = 8000, 6000           # output caps, thinking included; a cut-off answer is a failure
# the self-inspection clauses of the pilot regulators: about 25 clauses, about 50 mappings
PILOT = {
    "eu-cap9_en.pdf": ["Chapter 9 Principle", "Chapter 9 9.1", "Chapter 9 9.2", "Chapter 9 9.3"],
    "who-trs986-a2-gmp-main.pdf": [f"8.{n}" for n in range(1, 10)],
    "india-schedule-m-2023-GSR922E.pdf": [f"Part I 10.{n}" for n in range(1, 8)] + ["Part I 10.8.1",
                                                                                  "Part I 10.8.2"],
    "ich-q7.pdf": ["2.40", "2.41"],
}

def sub_topics():
    """[(sub-topic id, area name)] from library/topics.json, for the drafter's topic field (D37)."""
    tree = json.loads((HERE.parents[1] / "library" / "topics.json").read_text(encoding="utf-8"))
    return [(sub, t["name"]) for t in tree["topics"] for sub in t["sub"]]


DRAFT_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["obligations", "no_obligation_reason"],
    "properties": {
        "no_obligation_reason": {"type": "string"},
        "obligations": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["statement", "quote", "strength", "plant_types", "numbers", "topic"],
            "properties": {
                "statement": {"type": "string"},
                "quote": {"type": "string"},
                "strength": {"type": "string", "enum": ["mandatory", "recommended", "optional"]},
                "plant_types": {"type": "array", "items": {"type": "string", "enum": PLANT_TYPES}},
                "numbers": {"type": "array", "items": {"type": "string"}},
                "topic": {"type": "string", "enum": [sub for sub, _ in sub_topics()]}}}}}}

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


def draft_prompt():
    """The drafter's instructions with the topic list its topic field takes (D37)."""
    return prompt("draft") + "\n\nTOPICS (sub-topic id: area):\n" + "\n".join(f"{sub}: {name}"
                                                                          for sub, name in sub_topics()) + "\n"


def clause_block(source, clause, scope):
    heading = f"Section: {clause['section']}\n" if clause.get("section") else ""
    return (f"Source: {source['regulator']} - {source['title']}\nApplies to plant types: {scope}\n{heading}"
            f"Clause {clause['ref']}:\n{clause['text']}")


def with_context(text, source, ref, context_of):
    """The model input with the clause graph's context block appended (D34), when one is asked for."""
    block = context_of(source, ref) if context_of else ""
    return f"{text}\n\n{block}" if block else text


def graph_context(files):
    """context_of(source, ref) from the full clause graph (tools/library/graph.py), so definitions come from
    every glossary of the source's family, not only from the files being drafted; files is kept for callers."""
    import graph
    import layer1
    rows = graph.links(reqs=[])
    sources = layer1.catalog()
    return lambda source, ref: graph.context_block(graph.context(source, ref, rows, layer1.segments_of, sources))


def draft_requests(pilot, sources, clauses_of, context_of=None):
    """One drafting request per clause; context_of(source, ref) adds the clause graph's context (D34)."""
    out = []
    for file, refs in pilot.items():
        tree = clauses_of(file)
        scope = ", ".join(sorted(runner_scope(sources[file]["applies_to"])))
        for ref in refs:
            clause = tree[ref]
            out.append(runner.Request(f"draft-{len(out):03d}", draft_prompt(),
                                      with_context(clause_block(sources[file], clause, scope), file, ref,
                                                   context_of), DRAFT_SCHEMA,
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
            quote = normalise(ob["quote"])
            found = len(quote.split()) >= MIN_QUOTE_WORDS and quote in normalise(clause["text"])
            (mappings if found else rejected).append(m)
    return mappings, rejected


def verify_requests(mappings, sources, clauses_of, context_of=None):
    """Two blind verifier requests per mapping; context_of(source, ref) adds the same context the drafter had."""
    out = []
    for n, m in enumerate(mappings):
        clause = clauses_of(m["source"])[m["ref"]]
        scope = ", ".join(sorted(runner_scope(sources[m["source"]]["applies_to"])))
        item = (f"ITEM: {m['statement']}\nStrength: {m['strength']}\n"
                f"Plant types: {', '.join(m['plant_types'])}\nCOVERS: {normalise(m['quote'])}")
        clause_text = with_context(clause_block(sources[m["source"]], clause, scope), m["source"], m["ref"],
                                   context_of)
        for role, first, second in (("a", item, clause_text), ("b", clause_text, item)):
            out.append(runner.Request(f"verify-{role}-{n:03d}", prompt(f"verify_{role}"), f"{first}\n\n{second}",
                                      VERIFY_SCHEMA, max_tokens=VERIFY_TOKENS,
                                      meta={"mapping": n, "verifier": role, "source": m["source"], "ref": m["ref"],
                                            "clause_sha256": m["clause_sha256"], "draft": m["draft"]}))
    return out


def _spans(text, part):
    """Start offsets of every occurrence of part in text."""
    out, i = [], text.find(part)
    while part and i >= 0:
        out.append(i)
        i = text.find(part, i + 1)
    return out


def coverage(drafts, mappings, clauses_of):
    """Obligation sentences of the drafted clauses that the clause's mapping quotes do not cover: a sentence is
    uncovered when less than COVERED_SHARE of its words lie inside some quote's span in the clause text. Words are
    runs of letters and digits, so punctuation or a list marker outside a quote does not count against it."""
    quotes = {}
    for m in mappings:
        quotes.setdefault((m["source"], m["ref"]), []).append(normalise(m["quote"]))
    out = []
    for req in drafts:
        key = (req.meta["source"], req.meta["ref"])
        text = normalise(clauses_of(key[0])[key[1]]["text"])
        covered = [False] * len(text)
        number = LEADING_NUMBER.match(text)                 # "9.3 All self inspections ...": not a word to quote
        covered[:number.end()] = [True] * number.end()
        for q in quotes.get(key, []):
            for start in _spans(text, q):
                covered[start:start + len(q)] = [True] * len(q)
        cursor = 0
        for i, sentence in enumerate(obligations.sentences(text)):
            if not obligations.strength(sentence):
                continue
            sentence = normalise(sentence)
            start = text.find(sentence, cursor)
            if start < 0:
                start = text.find(sentence)
            cursor = max(cursor, start + len(sentence)) if start >= 0 else cursor
            words = [(start + w.start(), start + w.end()) for w in WORD.finditer(sentence)] if start >= 0 else []
            share = (sum(all(covered[a:b]) for a, b in words) / len(words)) if words else 0.0
            if share < COVERED_SHARE:
                out.append({"source": key[0], "ref": key[1], "sentence_index": i, "covered_share": round(share, 2),
                            "text": sentence})
    return out


WORD = re.compile(r"\w+")
# a clause's own number ("9.3", "10.1.", "(b)", "(A)", "Principle"); not a year or count ("2024 annual review")
LEADING_NUMBER = re.compile(r"\s*(?:[A-Z]?\d{1,3}(?:\.\d+)*\.?(?!\d)|\([a-zA-Z0-9]+\)|principle\b)?\s*", re.I)


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
    drafts = draft_requests(pilot, sources, clauses_of)
    # verification is two calls per obligation; assume up to 3 obligations per clause for the bound
    per_verify = runner.cost({"input_tokens": 2000, "output_tokens": VERIFY_TOKENS})
    bound = runner.worst_case(drafts) + len(drafts) * 3 * 2 * per_verify
    if bound > budget:
        raise SystemExit(f"worst-case cost US${bound:.2f} is over the budget US${budget:.2f}; nothing was sent")
    d_dir, d_results, d_summary = runner.execute(run_with, drafts, "pilot-draft")
    mappings, rejected = mappings_from(drafts, d_results, clauses_of)
    runner.write_jsonl(d_dir / "mappings.jsonl", mappings)
    runner.write_jsonl(d_dir / "rejected-quotes.jsonl", rejected)
    verifies = verify_requests(mappings, sources, clauses_of)
    # if drafting found more obligations than the bound assumed, verify as many whole mappings as the budget allows
    left = budget - d_summary["cost_usd"]
    while verifies and runner.worst_case(verifies) > left:
        verifies = verifies[:-2]
    skipped = len(mappings) - len(verifies) // 2
    v_dir, v_results, v_summary = runner.execute(run_with, verifies, "pilot-verify")
    rep = report(mappings, rejected, d_summary, v_results, v_summary)
    rep["not_verified_budget"] = skipped
    rep["uncovered_sentences"] = coverage(drafts, mappings, clauses_of)
    rep["runs"] = [d_dir.name, v_dir.name]
    (v_dir / "pilot-report.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def topic_pilot(units):
    """{file: [refs]} for the units of a topic file (tools/ai/topic.py) that are drafted; twins are not."""
    out = {}
    for u in units:
        out.setdefault(u["source"], []).append(u["ref"])
    return out


def prepare_draft(pilot=PILOT, sources=None, clauses_of=None, context_of=None, topic=None):
    """Session stage 1: draft batch files. Returns the draft run dir. With topic (a topic.py file's content), the
    topic's units are drafted and the file is kept in the run dir, so ingest can give each twin its mappings."""
    import layer1
    if topic:
        pilot = topic_pilot(topic["units"])
    drafts = draft_requests(pilot, sources or layer1.catalog(), clauses_of or layer1.clauses_of, context_of)
    run_dir = sessions.prepare(drafts, "session-draft")
    if topic:
        (Path(run_dir) / "topic.json").write_text(json.dumps(topic, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
    return run_dir


def twin_quote(quote, text):
    """The twin clause's own span for a quote: the same words in the same order, where punctuation and spacing
    may differ (twins are found on words alone, common.twin_key): "self- inspection", "(b)arran" for "(b) arran",
    ";" for ".". The span runs from the first to the last word. None when the twin has no such span."""
    text = normalise(text)
    quote = normalise(quote)
    if quote in text:
        return quote
    words = re.findall(r"\w+", quote)
    if not words:
        return None
    hit = re.search(r"(?<!\w)" + r"\W*".join(re.escape(w) for w in words) + r"(?!\w)", text, re.I)
    return hit.group(0) if hit else None


def twin_mappings(mappings, units, sources, clauses_of):
    """D36: each drafted unit's mappings copied to its twins (same text in another source). The quote is checked
    word for word against the twin's own clause and the plant types are cut to the twin source's scope; a copy
    that fails either is rejected, never kept. The copy keeps the twin's own wording (twin_quote). Returns
    (copies, rejected)."""
    twins = {(u["source"], u["ref"]): u["twins"] for u in units if u["twins"]}
    copies, rejected = [], []
    for n, m in enumerate(mappings):
        for t in twins.get((m["source"], m["ref"]), []):
            clause = clauses_of(t["source"])[t["ref"]]
            scope = runner_scope(sources[t["source"]]["applies_to"])
            quote = twin_quote(m["quote"], clause["text"])
            copy = {**m, "source": t["source"], "ref": t["ref"], "clause_sha256": clause["sha256"],
                    "quote": quote or m["quote"], "plant_types": [p for p in m["plant_types"] if p in scope],
                    "twin_of": n}
            if quote is None:
                rejected.append({**copy, "reason": "quote not found in the twin clause"})
            elif not copy["plant_types"]:
                rejected.append({**copy, "reason": "no plant type inside the twin source's scope"})
            else:
                copies.append(copy)
    return copies, rejected


def ingest_draft(draft_dir, clauses_of=None, sources=None):
    """Session stage 2: validate the draft answers, write mappings.jsonl and rejected-quotes.jsonl; for a topic
    run also twin-mappings.jsonl and twin-rejected.jsonl (D36)."""
    import layer1
    clauses_of = clauses_of or layer1.clauses_of
    drafts = sessions.load_requests(draft_dir)
    changed = [r.meta["ref"] for r in drafts if clauses_of(r.meta["source"])[r.meta["ref"]]["sha256"]
               != r.meta["clause_sha256"]]
    if changed:
        raise SystemExit(f"clause text changed since prepare-draft: {', '.join(changed)}")
    results, summary = sessions.ingest(draft_dir, "session-draft")
    mappings, rejected = mappings_from(drafts, results, clauses_of)
    out = {}
    topic_file = Path(draft_dir) / "topic.json"
    if topic_file.exists():
        units = json.loads(topic_file.read_text(encoding="utf-8"))["units"]
        copies, twin_rejected = twin_mappings(mappings, units, sources or layer1.catalog(), clauses_of)
        runner.write_jsonl(Path(draft_dir) / "twin-mappings.jsonl", copies)
        runner.write_jsonl(Path(draft_dir) / "twin-rejected.jsonl", twin_rejected)
        out = {"twin_mappings": len(copies), "twin_rejected": len(twin_rejected)}
    runner.write_jsonl(Path(draft_dir) / "mappings.jsonl", mappings)
    runner.write_jsonl(Path(draft_dir) / "rejected-quotes.jsonl", rejected)
    flagged = condition_findings(mappings)
    runner.write_jsonl(Path(draft_dir) / "condition-findings.jsonl", flagged)
    return {"requests": summary["requests"], "failed": summary["failed"], "mappings": len(mappings),
            "quotes_rejected": len(rejected), "condition_findings": len(flagged), **out}


def condition_findings(mappings):
    """Layer 1 check 9 on drafted items (D35): condition or limit wording in the quote that the statement lacks."""
    import layer1
    out = []
    for n, m in enumerate(mappings):
        missing = layer1.conditions_missing(m["quote"], layer1.conditions_in(m["statement"]))
        if missing:
            out.append({"mapping": n, "source": m["source"], "ref": m["ref"], "missing": missing,
                        "statement": m["statement"]})
    return out


def prepare_verify(draft_dir, sources=None, clauses_of=None, context_of=None):
    """Session stage 3: verifier batch files for every mapping. Returns the verify run dir."""
    import layer1
    draft_dir = Path(draft_dir)
    if not draft_dir.name.endswith("-session-draft"):
        raise SystemExit(f"{draft_dir} is not a session-draft run")
    mappings = runner.read_jsonl(draft_dir / "mappings.jsonl")
    verifies = verify_requests(mappings, sources or layer1.catalog(), clauses_of or layer1.clauses_of, context_of)
    verify_dir = sessions.prepare(verifies, "session-verify")
    (verify_dir / "draft-link.json").write_text(json.dumps(
        {"draft_run": draft_dir.name, "mappings_sha256": _sha256(draft_dir / "mappings.jsonl")}) + "\n",
        encoding="utf-8")
    return verify_dir


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ingest_verify(verify_dir, draft_dir, clauses_of=None):
    """Session stage 4: validate the verifier answers and write pilot-report.json into the verify dir."""
    import layer1
    clauses_of = clauses_of or layer1.clauses_of
    verify_dir, draft_dir = Path(verify_dir), Path(draft_dir)
    if not (verify_dir / "draft-link.json").exists():
        raise SystemExit(f"{verify_dir} is not a session-verify run (no draft-link.json)")
    link = json.loads((verify_dir / "draft-link.json").read_text(encoding="utf-8"))
    if link != {"draft_run": draft_dir.name, "mappings_sha256": _sha256(draft_dir / "mappings.jsonl")}:
        raise SystemExit(f"{verify_dir.name} was not prepared from the current mappings of {draft_dir.name}")
    v_results, v_summary = sessions.ingest(verify_dir, "session-verify")
    d_summary = json.loads((draft_dir / "summary.json").read_text(encoding="utf-8"))
    mappings = runner.read_jsonl(draft_dir / "mappings.jsonl")
    rejected = runner.read_jsonl(draft_dir / "rejected-quotes.jsonl")
    rep = report(mappings, rejected, d_summary, v_results, v_summary)
    rep["not_verified_budget"] = 0
    rep["uncovered_sentences"] = coverage(sessions.load_requests(draft_dir), mappings, clauses_of)
    rep["runs"] = [draft_dir.name, verify_dir.name]
    (verify_dir / "pilot-report.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "run", "prepare-draft", "ingest-draft", "prepare-verify",
                                        "ingest-verify"])
    ap.add_argument("dirs", nargs="*", help="run dirs: ingest-draft/prepare-verify <draft dir>; "
                                            "ingest-verify <verify dir> <draft dir>")
    ap.add_argument("--budget", type=float, default=15.0, help="US$; nothing is sent above this worst case")
    ap.add_argument("--topic", help="prepare-draft: draft the units of library/topics/<topic>.json (topic.py write)")
    ap.add_argument("--context", action="store_true",
                    help="prepare-draft/prepare-verify: add the clause graph's context (D34; measure before use)")
    args = ap.parse_args()
    need = {"ingest-draft": 1, "prepare-verify": 1, "ingest-verify": 2}.get(args.command, 0)
    if len(args.dirs) != need:
        ap.error(f"{args.command} takes {need} run dir(s)")
    if args.command == "check":
        print("API key accepted; model:", runner.check_access())
    elif args.command == "run":
        print(json.dumps(run(runner.BatchRunner(), args.budget), indent=1))
    elif args.command == "prepare-draft":
        topic = (json.loads((HERE.parents[1] / "library" / "topics" / f"{args.topic}.json").read_text(encoding="utf-8"))
                 if args.topic else None)
        files = sorted(topic_pilot(topic["units"]) if topic else PILOT)
        print(prepare_draft(context_of=graph_context(files) if args.context else None, topic=topic))
    elif args.command == "ingest-draft":
        print(json.dumps(ingest_draft(args.dirs[0]), indent=1))
    elif args.command == "prepare-verify":
        print(prepare_verify(args.dirs[0], context_of=graph_context(sorted(PILOT)) if args.context else None))
    else:
        print(json.dumps(ingest_verify(*args.dirs), indent=1))


if __name__ == "__main__":
    main()
