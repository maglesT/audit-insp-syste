import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "ai"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import layer1  # noqa: E402
import pilot  # noqa: E402
import runner  # noqa: E402

PILOT = {"eu-cap9_en.pdf": ["Chapter 9 9.1", "Chapter 9 9.3"]}


def answer(req):
    """A stand-in model: one good quote and one invented quote per clause; verifier A agrees, B does not."""
    if req.custom_id.startswith("draft"):
        clause = layer1.clauses_of(req.meta["source"])[req.meta["ref"]]
        real = " ".join(clause["text"].split()[2:12])
        ob = {"statement": "x", "strength": "recommended", "plant_types": ["OSD"], "numbers": []}
        return {"no_obligation_reason": "", "obligations": [{**ob, "quote": real},
                                                            {**ob, "quote": "words that are not in the clause"}]}
    verdict = "correct" if req.meta["verifier"] == "a" else "incorrect"
    return {"required_by_clause": True, "item_adds": "", "item_omits": "", "strictness": "same",
            "plant_types_ok": True, "strength_ok": True, "verdict": verdict, "reason": "r"}


class Pilot(unittest.TestCase):
    def setUp(self):
        self.runs = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.runs)
        self.original, runner.RUNS = runner.RUNS, self.runs
        self.addCleanup(setattr, runner, "RUNS", self.original)

    def test_mock_run_end_to_end(self):
        rep = pilot.run(runner.MockRunner(answer), budget=15, pilot=PILOT)
        self.assertEqual((rep["clauses"], rep["mappings"], rep["quotes_rejected"]), (2, 2, 2))
        self.assertEqual((rep["verified_by_both"], rep["disagree"], rep["both_correct"]), (2, 2, 0))
        self.assertEqual(rep["failed_calls"], [])
        draft_dir, verify_dir = (self.runs / r for r in rep["runs"])
        for f in ("requests.jsonl", "results.jsonl", "summary.json", "mappings.jsonl", "rejected-quotes.jsonl"):
            self.assertTrue((draft_dir / f).exists(), f)
        self.assertTrue((verify_dir / "pilot-report.json").exists())
        sent = json.loads((verify_dir / "requests.jsonl").read_text().splitlines()[0])
        self.assertEqual(sent["params"]["model"], "mock")
        self.assertEqual(sent["params"]["system"][0]["cache_control"], {"type": "ephemeral"})

    def test_verifiers_are_blind_and_differently_framed(self):
        rep = pilot.run(runner.MockRunner(answer), budget=15, pilot=PILOT)
        rows = [json.loads(x) for x in (self.runs / rep["runs"][1] / "requests.jsonl").read_text().splitlines()]
        a, b = rows[0]["params"], rows[1]["params"]
        self.assertNotEqual(a["system"][0]["text"], b["system"][0]["text"])
        self.assertTrue(a["messages"][0]["content"].startswith("ITEM:"))
        self.assertTrue(b["messages"][0]["content"].startswith("Source:"))
        self.assertNotIn("verdict", a["messages"][0]["content"] + b["messages"][0]["content"])

    def test_budget_stops_before_anything_is_sent(self):
        calls = []
        with self.assertRaises(SystemExit):
            pilot.run(runner.MockRunner(lambda r: calls.append(r)), budget=0.01, pilot=PILOT)
        self.assertEqual(calls, [])
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_failed_calls_are_recorded_not_dropped(self):
        def flaky(req):
            if req.custom_id == "draft-001":
                raise RuntimeError("overloaded")
            return answer(req)
        rep = pilot.run(runner.MockRunner(flaky), budget=15, pilot=PILOT)
        self.assertEqual(rep["failed_calls"], ["draft-001"])
        self.assertEqual(rep["mappings"], 1)

    def test_short_or_empty_quotes_are_rejected(self):
        def short(req):
            a = answer(req)
            if req.custom_id.startswith("draft"):
                for ob, q in zip(a["obligations"], ("", "the")):
                    ob["quote"] = q
            return a
        rep = pilot.run(runner.MockRunner(short), budget=15, pilot=PILOT)
        self.assertEqual((rep["mappings"], rep["quotes_rejected"]), (0, 4))

    def test_verify_calls_carry_their_trace(self):
        rep = pilot.run(runner.MockRunner(answer), budget=15, pilot=PILOT)
        row = json.loads((self.runs / rep["runs"][1] / "requests.jsonl").read_text().splitlines()[0])
        self.assertEqual({"source", "ref", "clause_sha256", "draft"} - set(row["meta"]), set())

    def test_many_obligations_verify_what_the_budget_allows(self):
        def many(req):
            a = answer(req)
            if req.custom_id.startswith("draft"):
                a["obligations"] = [a["obligations"][0]] * 40
            return a
        rep = pilot.run(runner.MockRunner(many), budget=2.0, pilot=PILOT)
        self.assertEqual(rep["mappings"], 80)
        self.assertGreater(rep["not_verified_budget"], 0)
        self.assertEqual(rep["verified_by_both"] + rep["not_verified_budget"], 80)

    def test_full_pilot_fits_the_budget(self):
        drafts = pilot.draft_requests(pilot.PILOT, layer1.catalog(), layer1.clauses_of)
        self.assertGreaterEqual(len(drafts), 20)
        bound = runner.worst_case(drafts) + len(drafts) * 6 * runner.cost(
            {"input_tokens": 2000, "output_tokens": pilot.VERIFY_TOKENS})
        self.assertLess(bound, 15)


def sdk_result(custom_id, text=None, stop="end_turn", error=None):
    """A real SDK batch result object, built from the API's JSON shape."""
    from anthropic.types.messages import MessageBatchIndividualResponse
    if error:
        result = {"type": "errored", "error": {"type": "error", "error": {"type": error, "message": "Overloaded"},
                                               "request_id": "req_1"}}
    else:
        result = {"type": "succeeded", "message": {
            "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5", "stop_sequence": None,
            "content": [{"type": "text", "text": text}], "stop_reason": stop,
            "usage": {"input_tokens": 100, "cache_read_input_tokens": 900, "output_tokens": 50}}}
    return MessageBatchIndividualResponse.model_validate({"custom_id": custom_id, "result": result})


def fake_api(results, fail_retrieve=False):
    state = {"polls": 0, "created": 0}

    def create(requests):
        state["created"] += 1
        return NS(id="b1", processing_status="in_progress", request_counts=NS(processing=len(requests)))

    def retrieve(batch_id):
        state["polls"] += 1
        if fail_retrieve:
            raise ConnectionError("network down")
        return NS(id=batch_id, processing_status="ended", request_counts=NS(processing=0))
    api = NS(messages=NS(batches=NS(create=create, retrieve=retrieve, results=lambda batch_id: iter(results))))
    return api, state


class Batch(unittest.TestCase):
    """BatchRunner against a fake client with real SDK result objects: no network."""

    def setUp(self):
        self.runs = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.runs)
        self.original, runner.RUNS = runner.RUNS, self.runs
        self.addCleanup(setattr, runner, "RUNS", self.original)

    def test_results_by_custom_id_and_failures(self):
        results = [sdk_result("c", "{not json"), sdk_result("a", '{"v": 1}'),     # any order
                   sdk_result("d", '{"v"', stop="max_tokens"), sdk_result("b", error="overloaded_error")]
        api, state = fake_api(results)
        reqs = [runner.Request(i, "s", "u", {"type": "object"}) for i in "abcde"]
        out = runner.BatchRunner(poll_seconds=0, api=api).run(reqs)
        self.assertEqual([r.custom_id for r in out], list("abcde"))
        self.assertEqual((out[0].answer, out[0].message_id), ({"v": 1}, "msg_1"))
        self.assertEqual(out[0].usage["cache_read_input_tokens"], 900)
        self.assertEqual([r.ok for r in out], [True, False, False, False, False])
        self.assertEqual((out[1].error, out[1].request_id), ("overloaded_error: Overloaded", "req_1"))
        self.assertTrue(out[2].error.startswith("answer is not JSON"))
        self.assertEqual(out[3].stop_reason, "max_tokens")
        self.assertEqual(out[4].error, "no result")

    def test_interrupted_run_keeps_its_trail_and_can_be_collected(self):
        api, state = fake_api([sdk_result("a", '{"v": 1}')], fail_retrieve=True)
        reqs = [runner.Request("a", "s", "u", {"type": "object"})]
        with self.assertRaises(ConnectionError):
            runner.execute(runner.BatchRunner(poll_seconds=0, api=api), reqs, "x")
        run_dir = next(self.runs.iterdir())
        self.assertTrue((run_dir / "requests.jsonl").exists())
        self.assertEqual(json.loads((run_dir / "batch.json").read_text())["batch_id"], "b1")
        api, state = fake_api([sdk_result("a", '{"v": 1}')])
        summary = runner.collect(run_dir, api=api)
        self.assertEqual((summary["ok"], state["created"]), (1, 0))       # collected, not sent again
        self.assertTrue((run_dir / "results.jsonl").exists())

    def test_api_key_variable(self):
        self.assertEqual(runner.api_key({"AUDIT_ANTHROPIC_KEY": " k1\n", "ANTHROPIC_API_KEY": "k2"}), "k1")
        self.assertEqual(runner.api_key({"ANTHROPIC_API_KEY": "k2"}), "k2")
        with self.assertRaises(SystemExit) as e:
            runner.api_key({"AUDIT_ANTHROPIC_KEY": "  "})
        self.assertIn("AUDIT_ANTHROPIC_KEY", str(e.exception))

    def test_cost(self):
        u = {"input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000, "output_tokens": 1_000_000}
        self.assertAlmostEqual(runner.cost(u, batch=False), 24.20)
        self.assertAlmostEqual(runner.cost(u), 12.10)


if __name__ == "__main__":
    unittest.main()
