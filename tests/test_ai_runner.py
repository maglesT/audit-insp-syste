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

    def test_full_pilot_fits_the_budget(self):
        drafts = pilot.draft_requests(pilot.PILOT, layer1.catalog(), layer1.clauses_of)
        self.assertGreaterEqual(len(drafts), 20)
        bound = runner.worst_case(drafts) + len(drafts) * 6 * runner.cost(
            {"input_tokens": 2000, "output_tokens": pilot.VERIFY_TOKENS})
        self.assertLess(bound, 15)


class Batch(unittest.TestCase):
    """BatchRunner against a fake client: no network."""

    def test_results_by_custom_id_and_failures(self):
        def msg(text, stop="end_turn"):
            usage = NS(input_tokens=100, cache_creation_input_tokens=0, cache_read_input_tokens=900, output_tokens=50)
            return NS(id="msg_1", stop_reason=stop, usage=usage, content=[NS(type="thinking"), NS(type="text", text=text)])
        results = [  # any order
            NS(custom_id="c", result=NS(type="succeeded", message=msg("{not json"))),
            NS(custom_id="a", result=NS(type="succeeded", message=msg('{"v": 1}'))),
            NS(custom_id="d", result=NS(type="succeeded", message=msg('{"v"', stop="max_tokens"))),
            NS(custom_id="b", result=NS(type="errored", error=NS(type="overloaded_error"))),
        ]
        state = {"polls": 0}

        def retrieve(batch_id):
            state["polls"] += 1
            return NS(id=batch_id, processing_status="ended", request_counts=NS(processing=0))
        fake = NS(messages=NS(batches=NS(
            create=lambda requests: NS(id="b1", processing_status="in_progress", request_counts=NS(processing=4)),
            retrieve=retrieve, results=lambda batch_id: iter(results))))
        reqs = [runner.Request(i, "s", "u", {"type": "object"}) for i in "abcde"]
        out = runner.BatchRunner(poll_seconds=0, api=fake).run(reqs)
        self.assertEqual([r.custom_id for r in out], list("abcde"))
        self.assertEqual(out[0].answer, {"v": 1})
        self.assertEqual([r.ok for r in out], [True, False, False, False, False])
        self.assertEqual(out[1].error, "overloaded_error")
        self.assertEqual(out[3].stop_reason, "max_tokens")
        self.assertEqual(out[4].error, "no result")
        self.assertEqual(state["polls"], 1)

    def test_cost(self):
        u = {"input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000, "output_tokens": 1_000_000}
        self.assertAlmostEqual(runner.cost(u, batch=False), 24.20)
        self.assertAlmostEqual(runner.cost(u), 12.10)


if __name__ == "__main__":
    unittest.main()
