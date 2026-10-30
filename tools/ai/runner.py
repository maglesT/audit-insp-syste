"""Model runners: one interface, two implementations (D14: the runner is swappable).

  BatchRunner  the Claude Message Batches API (50 % price), structured JSON output, cached instructions.
  MockRunner   a function from request to answer, for tests (CI never calls the API).

Every run writes an audit trail to library/ai-runs/<run id>/: requests.jsonl (the exact parameters sent),
results.jsonl (raw answer, stop reason, usage, request id) and summary.json (model, counts, tokens, cost).
"""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "library" / "ai-runs"
MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000
# US$ per million tokens, Claude Opus 5.5 list prices (cached 2026-10-06); the Batch API halves all of them
PRICE = {"input": 4.00, "cache_write": 5.00, "cache_read": 0.20, "output": 20.00}
BATCH_DISCOUNT = 0.5


@dataclass
class Request:
    custom_id: str
    system: str               # fixed instructions: identical across a stage, so they are cached
    user: str                 # the varying part: one clause, or one item with its clause
    schema: dict              # JSON schema of the answer (structured output)
    effort: str = "high"
    max_tokens: int = MAX_TOKENS
    meta: dict = field(default_factory=dict)

    def params(self, model=MODEL):
        return {"model": model, "max_tokens": self.max_tokens,
                "system": [{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": self.user}],
                "output_config": {"effort": self.effort, "format": {"type": "json_schema", "schema": self.schema}}}


@dataclass
class Result:
    custom_id: str
    ok: bool
    answer: dict | None
    stop_reason: str
    usage: dict
    message_id: str = ""      # msg_... of a succeeded call
    request_id: str = ""      # req_... where the API reports one (errored calls)
    error: str = ""


def cost(usage, batch=True):
    """US$ for one usage dict (input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens)."""
    usd = (usage.get("input_tokens", 0) * PRICE["input"] + usage.get("cache_creation_input_tokens", 0)
           * PRICE["cache_write"] + usage.get("cache_read_input_tokens", 0) * PRICE["cache_read"]
           + usage.get("output_tokens", 0) * PRICE["output"]) / 1e6
    return usd * (BATCH_DISCOUNT if batch else 1)


def worst_case(requests):
    """Upper bound in US$ before sending: 3 characters per token (generous), all input priced as a cache write
    (the dearest input rate), every answer at its max_tokens."""
    tokens_in = sum(len(r.system) + len(r.user) + len(json.dumps(r.schema)) for r in requests) / 3
    return cost({"cache_creation_input_tokens": tokens_in, "output_tokens": sum(r.max_tokens for r in requests)})


def new_run(stage):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "-" + stage
    path = RUNS / run_id
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def record_requests(run_dir, requests, model):
    """Written before anything is sent, so a paid batch is always traceable."""
    write_jsonl(run_dir / "requests.jsonl", [{"custom_id": r.custom_id, "meta": r.meta, "params": r.params(model)}
                                             for r in requests])


def record_results(run_dir, results, model, batch):
    """Results and summary of one run."""
    write_jsonl(run_dir / "results.jsonl", [r.__dict__ for r in results])
    total = {k: sum(r.usage.get(k, 0) for r in results) for k in
             ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}
    summary = {"model": model, "batch": batch, "requests": len(results), "ok": sum(r.ok for r in results),
               "failed": [r.custom_id for r in results if not r.ok], "usage": total,
               "cost_usd": round(cost(total, batch), 4), "prices_per_mtok": PRICE,
               "finished": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return summary


def execute(run_with, requests, stage):
    """Record the requests, run them, record the results: (run dir, results, summary)."""
    model = getattr(run_with, "model", MODEL)
    run_dir = new_run(stage)
    record_requests(run_dir, requests, model)
    results = run_with.run(requests, run_dir)
    return run_dir, results, record_results(run_dir, results, model, run_with.batch)


def parse_answer(text):
    try:
        return json.loads(text), ""
    except (json.JSONDecodeError, TypeError) as e:
        return None, f"answer is not JSON: {e}"


class MockRunner:
    """answer(request) -> dict, or raises to simulate a failed call. Usage is a fixed small amount per call."""
    model = "mock"
    batch = False

    def __init__(self, answer):
        self.answer = answer

    def run(self, requests, run_dir=None):
        out = []
        for r in requests:
            usage = {"input_tokens": 1000, "output_tokens": 500}
            try:
                out.append(Result(r.custom_id, True, self.answer(r), "end_turn", usage))
            except Exception as e:                          # noqa: BLE001 - recorded as a failed call
                out.append(Result(r.custom_id, False, None, "error", usage, error=str(e)))
        return out


def client():
    """An API client. The key is never in the repo: either ANTHROPIC_API_KEY is set in the environment, or the
    environment's network secret adds the x-api-key header on the way to api.anthropic.com (the SDK then sends
    a placeholder that the proxy replaces)."""
    import os
    import anthropic
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or "set-by-network-secret")


def check_access(model=MODEL):
    """One tiny call, so a missing or wrong key fails before any batch is sent."""
    msg = client().messages.create(model=model, max_tokens=16, messages=[{"role": "user", "content": "Reply OK."}],
                                   output_config={"effort": "low"})
    return msg.model


def to_result(item):
    """One batch result -> Result."""
    res = item.result
    if res.type != "succeeded":
        err = getattr(res, "error", None)                   # ErrorResponse: .error.type/.message, .request_id
        inner = getattr(err, "error", None)
        detail = f"{getattr(inner, 'type', '') or res.type}: {getattr(inner, 'message', '')}".rstrip(": ")
        return Result(item.custom_id, False, None, res.type, {}, request_id=getattr(err, "request_id", "") or "",
                      error=detail)
    msg = res.message
    usage = {k: getattr(msg.usage, k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                         "cache_read_input_tokens", "output_tokens")}
    if msg.stop_reason != "end_turn":
        return Result(item.custom_id, False, None, msg.stop_reason, usage, msg.id, error=f"stopped: {msg.stop_reason}")
    text = next((b.text for b in msg.content if b.type == "text"), None)
    answer, error = parse_answer(text)
    return Result(item.custom_id, answer is not None, answer, msg.stop_reason, usage, msg.id, error=error)


class BatchRunner:
    """The Message Batches API. The batch id is written to <run dir>/batch.json as soon as it exists, so an
    interrupted run can be collected later: python3 tools/ai/runner.py collect <run dir>."""
    batch = True

    def __init__(self, model=MODEL, poll_seconds=60, api=None):
        self.model, self.poll = model, poll_seconds
        self.client = api or client()

    def run(self, requests, run_dir=None):
        from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
        from anthropic.types.messages.batch_create_params import Request as BatchRequest
        batch = self.client.messages.batches.create(requests=[
            BatchRequest(custom_id=r.custom_id, params=MessageCreateParamsNonStreaming(**r.params(self.model)))
            for r in requests])
        if run_dir:
            (run_dir / "batch.json").write_text(json.dumps({"batch_id": batch.id, "model": self.model}) + "\n",
                                                encoding="utf-8")
        print(f"batch {batch.id}: {len(requests)} requests submitted", flush=True)
        return self.collect(batch.id, [r.custom_id for r in requests])

    def collect(self, batch_id, custom_ids):
        batch = self.client.messages.batches.retrieve(batch_id)
        while batch.processing_status != "ended":
            time.sleep(self.poll)
            batch = self.client.messages.batches.retrieve(batch_id)
            print(f"batch {batch_id}: {batch.request_counts.processing} still processing", flush=True)
        by_id = {item.custom_id: to_result(item) for item in self.client.messages.batches.results(batch_id)}
        return [by_id.get(c) or Result(c, False, None, "missing", {}, error="no result") for c in custom_ids]


def collect(run_dir, api=None):
    """Finish an interrupted run from its batch.json and requests.jsonl."""
    run_dir = Path(run_dir)
    info = json.loads((run_dir / "batch.json").read_text(encoding="utf-8"))
    ids = [r["custom_id"] for r in read_jsonl(run_dir / "requests.jsonl")]
    results = BatchRunner(info["model"], api=api).collect(info["batch_id"], ids)
    return record_results(run_dir, results, info["model"], True)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "collect":
        print(json.dumps(collect(sys.argv[2]), indent=1))
    else:
        sys.exit("usage: python3 tools/ai/runner.py collect <run dir>")
