"""Layer 2 on library requirements (tools/ai/verify.py)."""
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ai"))
import runner  # noqa: E402
import sessions  # noqa: E402
import verify  # noqa: E402

SHA = "0" * 64
QUOTE = "Self inspections should be conducted regularly."
SOURCES = {s: {"regulator": r, "title": s, "applies_to": "ALL"} for s, r in
           (("eu.pdf", "EU"), ("pics.pdf", "PICS"), ("who.pdf", "WHO"))}
TREES = {s: {"9.1": {"ref": "9.1", "text": "9.1 " + QUOTE, "sha256": SHA}} for s in SOURCES}


def mapping(source, relation="same", addendum="", strength="recommended"):
    return {"source": source, "clause_ref": "9.1", "clause_sha256": SHA, "quote": QUOTE, "strength": strength,
            "relation": relation, "plant_types": ["OSD"], "addendum": addendum}


REQS = [{"id": "SI-001", "item_text": "Run regular self-inspections.", "status": "draft", "mappings": [
    mapping("eu.pdf"), mapping("pics.pdf"), mapping("who.pdf", "stricter", "At least once a year.")]},
        {"id": "SI-002", "item_text": "Record them.", "status": "draft", "mappings": [
            mapping("eu.pdf", "looser", strength="optional")]}]


def answer(verdict="correct", strictness="same", omits=""):
    return {"required_by_clause": True, "item_adds": "", "item_omits": omits, "strictness": strictness,
            "plant_types_ok": True, "strength_ok": True, "verdict": verdict, "reason": "r"}


class Library(unittest.TestCase):
    def test_judged_text_and_twins(self):
        u = verify.units(REQS)
        self.assertEqual(len(u), 4)
        self.assertEqual(len({k for k, *_ in u}), 3)          # EU and PIC/S twins share one judgement
        self.assertEqual(u[2][3]["statement"], "Run regular self-inspections. At least once a year.")

    def test_passes(self):
        self.assertTrue(verify.passes(answer(), "same"))
        self.assertFalse(verify.passes(answer("incorrect", "stricter"), "adds"))
        self.assertTrue(verify.passes(answer("incorrect", "stricter"), "looser"))
        self.assertFalse(verify.passes(answer("incorrect", "stricter", omits="the frequency"), "looser"))
        self.assertFalse(verify.passes(answer(), "narrower"))

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp, unittest.mock.patch.object(runner, "RUNS", Path(tmp)):
            run = verify.prepare(REQS, SOURCES, TREES.get)
            judged = runner.read_jsonl(run / "judged.jsonl")
            self.assertEqual(len(judged), 3)
            for batch in sorted((run / "batches").glob("*.json")):
                items = json.loads(batch.read_text())["items"]
                answers = []
                for it in items:
                    n = int(it["custom_id"].rsplit("-", 1)[1])
                    ans = answer("incorrect", "stricter") if judged[n]["relation"] == "looser" else answer()
                    if n == 1 and it["custom_id"].startswith("verify-b"):
                        ans = answer("incorrect", omits="the year")
                    answers.append({"custom_id": it["custom_id"], "answer": ans})
                (run / "answers" / batch.name).write_text(json.dumps({"answers": answers}))
            rep = verify.ingest(run)
            self.assertEqual((rep["judged"], rep["both_pass"], rep["disagree"]), (3, 2, 1))
            self.assertEqual(verify.statuses(REQS, run), {"SI-001": "unverified", "SI-002": "verified"})


if __name__ == "__main__":
    unittest.main()
