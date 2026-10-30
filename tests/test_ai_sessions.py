import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "ai"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import layer1  # noqa: E402
import pilot  # noqa: E402
import runner  # noqa: E402
import sessions  # noqa: E402

PILOT = {"eu-cap9_en.pdf": ["Chapter 9 9.1", "Chapter 9 9.3"]}
VERDICT = {"required_by_clause": True, "item_adds": "", "item_omits": "", "strictness": "same",
           "plant_types_ok": True, "strength_ok": True, "verdict": "correct", "reason": "r"}


def draft_answer(clause_text):
    """One obligation whose quote is the clause's first ten words."""
    quote = " ".join(clause_text.split()[:10])
    return {"no_obligation_reason": "", "obligations": [
        {"statement": "x", "quote": quote, "strength": "recommended", "plant_types": ["OSD"], "numbers": []}]}


def answer_all(run_dir, make):
    """Play the agents: answer every batch file with make(custom_id, input)."""
    for batch in sorted((run_dir / "batches").glob("batch_*.json")):
        items = json.loads(batch.read_text())["items"]
        (run_dir / "answers" / batch.name).write_text(json.dumps(
            {"answers": [{"custom_id": i["custom_id"], "answer": make(i["custom_id"], i["input"])} for i in items]}))


class Sessions(unittest.TestCase):
    def setUp(self):
        self.runs = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.runs)
        self.original, runner.RUNS = runner.RUNS, self.runs
        self.addCleanup(setattr, runner, "RUNS", self.original)

    def requests(self, n, system="s"):
        schema = {"type": "object", "additionalProperties": False, "required": ["v"],
                  "properties": {"v": {"type": "string", "enum": ["yes", "no"]}}}
        return [runner.Request(f"{system}-{i:03d}", system, f"input {i}", schema, meta={"n": i}) for i in range(n)]

    def test_prepare_and_ingest(self):
        run_dir = sessions.prepare(self.requests(45), "t")
        batches = sorted((run_dir / "batches").glob("*.json"))
        self.assertEqual([len(json.loads(b.read_text())["items"]) for b in batches], [40, 5])
        first = json.loads(batches[0].read_text())
        self.assertEqual(set(first), {"instructions", "schema", "items"})
        self.assertEqual(first["items"][0], {"custom_id": "s-000", "input": "input 0"})
        sent = runner.read_jsonl(run_dir / "requests.jsonl")[0]
        self.assertEqual((sent["params"]["model"], sent["meta"]), ("claude-code-session", {"n": 0}))
        answer_all(run_dir, lambda cid, inp: {"v": "yes"})
        results, summary = sessions.ingest(run_dir)
        self.assertEqual((summary["ok"], summary["failed"], summary["cost_usd"]), (45, [], 0))
        self.assertEqual(summary["model"], "claude-code-session")
        self.assertFalse(summary["batch"])
        self.assertEqual(results[0].answer, {"v": "yes"})
        self.assertTrue((run_dir / "results.jsonl").exists())

    def test_invalid_or_missing_answers_are_failed_calls(self):
        run_dir = sessions.prepare(self.requests(5), "t")
        bad = {"s-000": {"v": "maybe"}, "s-001": {"v": "yes", "extra": 1}, "s-002": {}, "s-003": "yes"}
        items = [{"custom_id": c, "answer": a} for c, a in bad.items()]       # s-004 has no answer
        (run_dir / "answers" / "batch_000.json").write_text(json.dumps({"answers": items}))
        results, summary = sessions.ingest(run_dir)
        self.assertEqual(summary["ok"], 0)
        errors = {r.custom_id: r.error for r in results}
        self.assertIn("not in", errors["s-000"])
        self.assertIn("unexpected extra", errors["s-001"])
        self.assertIn("missing v", errors["s-002"])
        self.assertIn("expected object", errors["s-003"])
        self.assertEqual(errors["s-004"], "no answer")
        self.assertTrue(all(r.answer is None for r in results))

    def test_no_answer_file_or_unreadable_file(self):
        run_dir = sessions.prepare(self.requests(41), "t")
        (run_dir / "answers" / "batch_001.json").write_text("{not json")
        results, summary = sessions.ingest(run_dir)
        self.assertEqual(len(summary["failed"]), 41)
        self.assertIn("no answer file", results[0].error)
        self.assertIn("unreadable", results[40].error)

    def test_answer_from_another_batch_does_not_count(self):
        run_dir = sessions.prepare(self.requests(2, "a") + self.requests(1, "b"), "t")
        (run_dir / "answers" / "batch_000.json").write_text(json.dumps(
            {"answers": [{"custom_id": c, "answer": {"v": "no"}} for c in ("a-000", "a-001", "b-000")]}))
        results, _ = sessions.ingest(run_dir)
        self.assertEqual([r.ok for r in results], [True, True, False])

    def test_validator(self):
        schema = {"type": "object", "required": ["a"], "properties": {
            "a": {"type": "array", "items": {"type": "integer"}}, "b": {"type": "boolean"}}}
        self.assertEqual(sessions.validate({"a": [1, 2], "b": False, "c": 0}, schema), [])
        self.assertEqual(len(sessions.validate({"a": [1, True, 2.5], "b": 1}, schema)), 3)

    def test_verifier_a_and_b_never_share_a_batch(self):
        mappings = [{"source": "eu-cap9_en.pdf", "ref": "Chapter 9 9.3", "statement": f"s{i}",
                     "quote": "All self inspections should be recorded", "strength": "recommended",
                     "plant_types": ["OSD"], "clause_sha256": "x", "draft": "draft-000"} for i in range(50)]
        verifies = pilot.verify_requests(mappings, layer1.catalog(), layer1.clauses_of)
        run_dir = sessions.prepare(verifies, "t")
        batches = sorted((run_dir / "batches").glob("*.json"))
        self.assertEqual(len(batches), 4)                   # 50 A + 50 B, at most 40 per batch
        for b in batches:
            roles = {i["custom_id"].split("-")[1] for i in json.loads(b.read_text())["items"]}
            self.assertEqual(len(roles), 1, b.name)
        self.assertEqual(sorted(len(json.loads(b.read_text())["items"]) for b in batches), [10, 10, 40, 40])

    def test_covers_line_in_both_verifier_inputs(self):
        m = {"source": "eu-cap9_en.pdf", "ref": "Chapter 9 9.3", "statement": "s", "strength": "recommended",
             "quote": "All self inspections should be recorded", "plant_types": ["OSD"], "clause_sha256": "x",
             "draft": "draft-000"}
        a, b = pilot.verify_requests([m], layer1.catalog(), layer1.clauses_of)
        for r in (a, b):
            self.assertIn("\nCOVERS: All self inspections should be recorded", r.user)
        self.assertTrue(a.user.startswith("ITEM:"))
        self.assertTrue(b.user.startswith("Source:"))

    def test_verifiers_read_the_item_literally(self):
        """D31: a condition or trigger missing from the item is an omission, even if the clause implies it."""
        a, b = pilot.prompt("verify_a"), pilot.prompt("verify_b")
        self.assertIn("Do not read the clause back into the item", a)
        self.assertIn("with nothing filled in from the clause", b)
        for text in (a, b):
            for trigger in ('"if"', '"when"', '"before"'):
                self.assertIn(trigger, text)
        self.assertNotEqual(a, b)                           # still framed differently

    def test_coverage_check(self):
        drafts = pilot.draft_requests(PILOT, layer1.catalog(), layer1.clauses_of)
        text = layer1.clauses_of("eu-cap9_en.pdf")["Chapter 9 9.3"]["text"]
        base = {"source": "eu-cap9_en.pdf", "ref": "Chapter 9 9.3"}
        whole = pilot.coverage(drafts, [{**base, "quote": text}], layer1.clauses_of)
        self.assertEqual([u["ref"] for u in whole], ["Chapter 9 9.1"])      # 9.3 fully quoted, 9.1 not at all
        self.assertTrue(all(u["covered_share"] == 0 for u in whole))
        sentences = [s for s in pilot.obligations.sentences(pilot.normalise(text))
                     if pilot.obligations.strength(s)]
        self.assertGreater(len(sentences), 1)
        part = pilot.coverage(drafts, [{**base, "quote": sentences[0]}], layer1.clauses_of)
        flagged = [u["text"] for u in part if u["ref"] == "Chapter 9 9.3"]
        self.assertEqual(flagged, [pilot.normalise(s) for s in sentences[1:]])

    def test_session_pilot_end_to_end(self):
        draft_dir = pilot.prepare_draft(PILOT)
        clauses = {r.custom_id: layer1.clauses_of(r.meta["source"])[r.meta["ref"]]["text"]
                   for r in sessions.load_requests(draft_dir)}
        answer_all(draft_dir, lambda cid, inp: draft_answer(clauses[cid]))
        d = pilot.ingest_draft(draft_dir)
        self.assertEqual((d["requests"], d["mappings"], d["quotes_rejected"], d["failed"]), (2, 2, 0, []))
        verify_dir = pilot.prepare_verify(draft_dir)
        answer_all(verify_dir, lambda cid, inp: {**VERDICT, "verdict": "correct" if "-a-" in cid else "incorrect"})
        rep = pilot.ingest_verify(verify_dir, draft_dir)
        self.assertEqual((rep["mappings"], rep["verified_by_both"], rep["disagree"]), (2, 2, 2))
        self.assertEqual((rep["cost_usd"], rep["failed_calls"]), (0, []))
        self.assertTrue(rep["uncovered_sentences"])         # ten-word quotes leave most sentences uncovered
        self.assertEqual(rep["runs"], [draft_dir.name, verify_dir.name])
        self.assertTrue((verify_dir / "pilot-report.json").exists())


    def test_duplicates_are_refused_or_failed(self):
        reqs = self.requests(2)
        with self.assertRaises(ValueError):
            sessions.prepare(reqs + reqs[:1], "t")
        mixed = self.requests(1) + [runner.Request("s-009", "s", "i", {"type": "object"})]
        with self.assertRaises(ValueError):
            sessions.prepare(mixed, "t")
        self.assertEqual(list(self.runs.iterdir()), [])     # checks run before any run dir exists
        run_dir = sessions.prepare(reqs, "t")
        (run_dir / "answers" / "batch_000.json").write_text(json.dumps({"answers": [
            {"custom_id": "s-000", "answer": {}}, {"custom_id": "s-000", "answer": {"v": "yes"}},
            {"custom_id": "s-001", "answer": {"v": "no"}}]}))
        results, _ = sessions.ingest(run_dir)
        self.assertEqual([(r.ok, r.error) for r in results], [(False, "duplicate answer"), (True, "")])

    def test_ingest_again_keeps_earlier_results(self):
        run_dir = sessions.prepare(self.requests(1), "t")
        sessions.ingest(run_dir)                             # no answers yet: one failed call
        answer_all(run_dir, lambda cid, inp: {"v": "no"})
        _, summary = sessions.ingest(run_dir)
        self.assertEqual(summary["ok"], 1)
        kept = sorted(f.name for f in run_dir.glob("results-*.jsonl"))
        self.assertEqual(len(kept), 1)
        self.assertFalse(runner.read_jsonl(run_dir / kept[0])[0]["ok"])
        self.assertEqual(len(list(run_dir.glob("summary-*.json"))), 1)

    def test_ingest_checks_the_stage(self):
        run_dir = sessions.prepare(self.requests(1), "session-draft")
        with self.assertRaises(SystemExit):
            sessions.ingest(run_dir, "session-verify")
        self.assertFalse((run_dir / "results.jsonl").exists())

    def test_integer_and_type_lists(self):
        self.assertEqual(sessions.validate(2.0, {"type": "integer"}), [])
        self.assertTrue(sessions.validate(2.5, {"type": "integer"}))
        self.assertTrue(sessions.validate(True, {"type": "number"}))
        with self.assertRaises(ValueError):
            sessions.validate(1, {"type": ["integer", "null"]})

    def test_coverage_ignores_punctuation_and_handles_overlaps(self):
        text = ("(a) Records must be kept. Audits should be done yearly, by staff. "
                "Audits should be done yearly, by staff.")
        clauses = {"x": {"r": {"text": text}}}
        drafts = [runner.Request("draft-000", "s", "u", {}, meta={"source": "x", "ref": "r"})]

        def uncovered(*quotes):
            maps = [{"source": "x", "ref": "r", "quote": q} for q in quotes]
            return [(u["sentence_index"], u["covered_share"]) for u in pilot.coverage(drafts, maps, clauses.get)]
        # full stops outside the quotes and an unquoted "(a)" (4 of 5 words) pass; overlapping quotes; a quote
        # matching both copies covers both
        self.assertEqual(uncovered("Records must be kept", "Audits should be done", "done yearly, by staff"), [])
        # a quote across a sentence boundary covers the first copy only; the repeated sentence is found in place
        self.assertEqual(uncovered("Records must be kept. Audits should be done yearly, by staff"), [(2, 0.0)])
        self.assertEqual(uncovered("Records must"), [(0, 0.4), (1, 0.0), (2, 0.0)])   # "(a)" is a word

    def test_verify_run_is_tied_to_its_draft_run(self):
        draft_dir = pilot.prepare_draft(PILOT)
        clauses = {r.custom_id: layer1.clauses_of(r.meta["source"])[r.meta["ref"]]["text"]
                   for r in sessions.load_requests(draft_dir)}
        answer_all(draft_dir, lambda cid, inp: draft_answer(clauses[cid]))
        pilot.ingest_draft(draft_dir)
        verify_dir = pilot.prepare_verify(draft_dir)
        with self.assertRaises(SystemExit):                 # swapped arguments touch nothing
            pilot.ingest_verify(draft_dir, verify_dir)
        with self.assertRaises(SystemExit):
            pilot.prepare_verify(verify_dir)
        with open(draft_dir / "mappings.jsonl", "a") as f:  # mappings changed after prepare-verify
            f.write("{}\n")
        answer_all(verify_dir, lambda cid, inp: VERDICT)
        with self.assertRaises(SystemExit):
            pilot.ingest_verify(verify_dir, draft_dir)
        self.assertFalse((verify_dir / "results.jsonl").exists())

    def test_draft_ingest_refuses_changed_clause_text(self):
        draft_dir = pilot.prepare_draft(PILOT)
        rows = runner.read_jsonl(draft_dir / "requests.jsonl")
        rows[0]["meta"]["clause_sha256"] = "0" * 64
        runner.write_jsonl(draft_dir / "requests.jsonl", rows)
        with self.assertRaises(SystemExit):
            pilot.ingest_draft(draft_dir)

    def test_failed_verifier_answers_in_the_report(self):
        draft_dir = pilot.prepare_draft(PILOT)
        clauses = {r.custom_id: layer1.clauses_of(r.meta["source"])[r.meta["ref"]]["text"]
                   for r in sessions.load_requests(draft_dir)}
        answer_all(draft_dir, lambda cid, inp: draft_answer(clauses[cid]))
        pilot.ingest_draft(draft_dir)
        verify_dir = pilot.prepare_verify(draft_dir)
        answer_all(verify_dir, lambda cid, inp: {"verdict": "correct"} if cid == "verify-b-000" else VERDICT)
        rep = pilot.ingest_verify(verify_dir, draft_dir)
        self.assertEqual(rep["failed_calls"], ["verify-b-000"])
        self.assertEqual((rep["verified_by_both"], rep["both_correct"], rep["not_verified_budget"]), (1, 1, 0))

    def test_cli_checks_the_number_of_run_dirs(self):
        for argv in (["pilot.py", "ingest-draft"], ["pilot.py", "ingest-verify", "x"], ["pilot.py", "run", "x"]):
            with self.assertRaises(SystemExit), unittest.mock.patch.object(sys, "argv", argv), \
                    unittest.mock.patch("sys.stderr"):
                pilot.main()

if __name__ == "__main__":
    unittest.main()
