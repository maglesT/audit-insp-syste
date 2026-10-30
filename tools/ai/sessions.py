"""Session runner: the model calls are answered by Claude Code agents inside a session (D30), not the API.

  prepare(requests, stage)  run dir with requests.jsonl (same audit trail as runner.py) and batches/batch_NNN.json
  ingest(run_dir)           answers/batch_NNN.json -> validated Results -> results.jsonl and summary.json

A batch holds at most BATCH_SIZE requests that share one system prompt, so verifier A and verifier B never meet
in one batch. A batch file is {"instructions", "schema", "items": [{custom_id, input}]}. The agent that answers
it writes answers/<same name> as {"answers": [{custom_id, answer}]}. An answer that is missing, comes from another
batch's file or does not fit the schema is a failed call with the reason recorded. Sessions have no token bill:
cost is 0 and usage stays empty. Ingesting again (after answers were corrected) keeps the earlier results as
results-<time>.jsonl and summary-<time>.json, so no outcome is lost.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import runner

MODEL = "claude-code-session"
BATCH_SIZE = 40


def prepare(requests, stage, size=BATCH_SIZE):
    """Record the requests and split them into batch files. Returns the run dir. Checks come first, so a bad
    request list leaves no run dir behind. A request whose meta has a "batch" key goes into a batch with only
    the requests of the same key (and system prompt), so a caller can keep chosen requests apart."""
    ids = [r.custom_id for r in requests]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate custom_id in requests")
    groups = {}
    for r in requests:
        groups.setdefault((r.system, r.meta.get("batch")), []).append(r)
    for group in groups.values():
        if len({json.dumps(r.schema, sort_keys=True) for r in group}) != 1:
            raise ValueError("requests with one system prompt must share one schema")
    run_dir = runner.new_run(stage)
    runner.record_requests(run_dir, requests, MODEL)
    (run_dir / "batches").mkdir()
    (run_dir / "answers").mkdir()
    n = 0
    for group in groups.values():
        for i in range(0, len(group), size):
            chunk = group[i:i + size]
            batch = {"instructions": chunk[0].system, "schema": chunk[0].schema,
                     "items": [{"custom_id": r.custom_id, "input": r.user} for r in chunk]}
            (run_dir / "batches" / f"batch_{n:03d}.json").write_text(
                json.dumps(batch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            n += 1
    return run_dir


def load_requests(run_dir):
    """The recorded requests as runner.Request objects (custom_id, prompts, schema, meta)."""
    out = []
    for row in runner.read_jsonl(Path(run_dir) / "requests.jsonl"):
        p = row["params"]
        out.append(runner.Request(row["custom_id"], p["system"][0]["text"], p["messages"][0]["content"],
                                  p["output_config"]["format"]["schema"], max_tokens=p["max_tokens"],
                                  meta=row["meta"]))
    return out


def validate(value, schema, path="answer"):
    """Errors of value against a JSON schema (the subset the pilot uses): type, enum, required, properties,
    additionalProperties false, items. Empty list when valid."""
    kinds = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
    t = schema.get("type")
    if t is not None and not isinstance(t, str):
        raise ValueError(f"{path}: schema type lists are not supported")
    if t in ("integer", "number"):
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        if t == "integer" and isinstance(value, float):
            ok = value.is_integer()                     # JSON Schema: 2.0 is an integer
    elif t:
        ok = isinstance(value, kinds[t])
    else:
        ok = True
    if not ok:
        return [f"{path}: expected {t}, got {type(value).__name__}"]
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if t == "object":
        props = schema.get("properties", {})
        errors += [f"{path}: missing {k}" for k in schema.get("required", []) if k not in value]
        if schema.get("additionalProperties") is False:
            errors += [f"{path}: unexpected {k}" for k in value if k not in props]
        for k, sub in props.items():
            if k in value:
                errors += validate(value[k], sub, f"{path}.{k}")
    if t == "array" and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    return errors


def _answers(path):
    """{custom_id: answer} of one answer file, or an error string for the whole file. A custom_id answered twice
    maps to DUPLICATE: neither answer is taken."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["answers"]
        out = {}
        for row in rows:
            cid = row["custom_id"]
            out[cid] = DUPLICATE if cid in out else row["answer"]
        return out
    except (OSError, ValueError, KeyError, TypeError) as e:
        return f"unreadable answer file {path.name}: {e}"


DUPLICATE = object()


def ingest(run_dir, stage=None):
    """Validate the answers and record them: (results, summary). stage, if given, must end the run id, so a
    swapped argument cannot rewrite another run's results."""
    run_dir = Path(run_dir)
    if stage and not run_dir.name.endswith("-" + stage):
        raise SystemExit(f"{run_dir} is not a {stage} run")
    if not (run_dir / "batches").is_dir():
        raise SystemExit(f"{run_dir} is not a session run (no batches/)")
    requests = load_requests(run_dir)
    schema_of = {r.custom_id: r.schema for r in requests}
    results = {}
    for batch_file in sorted((run_dir / "batches").glob("batch_*.json")):
        ids = [i["custom_id"] for i in json.loads(batch_file.read_text(encoding="utf-8"))["items"]]
        answer_file = run_dir / "answers" / batch_file.name
        answers = _answers(answer_file) if answer_file.exists() else f"no answer file {answer_file.name}"
        for cid in ids:
            if isinstance(answers, str):
                results[cid] = runner.Result(cid, False, None, "missing", {}, error=answers)
            elif cid not in answers:
                results[cid] = runner.Result(cid, False, None, "missing", {}, error="no answer")
            elif answers[cid] is DUPLICATE:
                results[cid] = runner.Result(cid, False, None, "invalid", {}, error="duplicate answer")
            else:
                errors = validate(answers[cid], schema_of[cid])
                results[cid] = (runner.Result(cid, True, answers[cid], "end_turn", {}) if not errors else
                                runner.Result(cid, False, None, "invalid", {}, error="; ".join(errors[:5])))
    ordered = [results.get(r.custom_id) or runner.Result(r.custom_id, False, None, "missing", {},
                                                         error="in no batch file") for r in requests]
    if (run_dir / "results.jsonl").exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        for name in ("results.jsonl", "summary.json"):
            old = run_dir / name
            if old.exists():
                old.rename(run_dir / f"{old.stem}-{stamp}{old.suffix}")
    summary = runner.record_results(run_dir, ordered, MODEL, batch=False)
    return ordered, summary
