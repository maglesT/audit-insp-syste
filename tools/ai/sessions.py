"""Session runner: the model calls are answered by Claude Code agents inside a session (D30), not the API.

  prepare(requests, stage)  run dir with requests.jsonl (same audit trail as runner.py) and batches/batch_NNN.json
  ingest(run_dir)           answers/batch_NNN.json -> validated Results -> results.jsonl and summary.json

A batch holds at most BATCH_SIZE requests that share one system prompt, so verifier A and verifier B never meet
in one batch. A batch file is {"instructions", "schema", "items": [{custom_id, input}]}. The agent that answers
it writes answers/<same name> as {"answers": [{custom_id, answer}]}. An answer that is missing, comes from another
batch's file or does not fit the schema is a failed call with the reason recorded. Sessions have no token bill:
cost is 0 and usage stays empty.
"""
import json
from pathlib import Path

import runner

MODEL = "claude-code-session"
BATCH_SIZE = 40


def prepare(requests, stage, size=BATCH_SIZE):
    """Record the requests and split them into batch files. Returns the run dir."""
    run_dir = runner.new_run(stage)
    runner.record_requests(run_dir, requests, MODEL)
    groups = {}
    for r in requests:
        groups.setdefault(r.system, []).append(r)
    (run_dir / "batches").mkdir()
    (run_dir / "answers").mkdir()
    n = 0
    for group in groups.values():
        for i in range(0, len(group), size):
            chunk = group[i:i + size]
            if len({json.dumps(r.schema, sort_keys=True) for r in chunk}) != 1:
                raise ValueError("requests with one system prompt must share one schema")
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
    if t in ("integer", "number"):
        ok = isinstance(value, (int, float) if t == "number" else int) and not isinstance(value, bool)
        if t == "integer" and isinstance(value, float):
            ok = False
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
    """{custom_id: answer} of one answer file, or an error string for the whole file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["answers"]
        out = {}
        for row in rows:
            out.setdefault(row["custom_id"], row["answer"])
        return out
    except (OSError, ValueError, KeyError, TypeError) as e:
        return f"unreadable answer file {path.name}: {e}"


def ingest(run_dir):
    """Validate the answers and record them: (results, summary)."""
    run_dir = Path(run_dir)
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
            else:
                errors = validate(answers[cid], schema_of[cid])
                results[cid] = (runner.Result(cid, True, answers[cid], "end_turn", {}) if not errors else
                                runner.Result(cid, False, None, "invalid", {}, error="; ".join(errors[:5])))
    ordered = [results.get(r.custom_id) or runner.Result(r.custom_id, False, None, "missing", {},
                                                         error="in no batch file") for r in requests]
    summary = runner.record_results(run_dir, ordered, MODEL, batch=False)
    return ordered, summary
