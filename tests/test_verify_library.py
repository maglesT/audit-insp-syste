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


def mapping(source, strength="recommended"):
    return {"source": source, "clause_ref": "9.1", "clause_sha256": SHA, "quote": QUOTE, "strength": strength,
            "plant_types": ["OSD"]}


def item(rid, text, m):
    return {"id": rid, "item_text": text, "status": "draft", "mappings": [m]}


REQS = [item("SI-001", "Run regular self-inspections.", mapping("eu.pdf")),
        item("SI-002", "Run regular self-inspections.", mapping("pics.pdf")),
        item("SI-003", "Run regular self-inspections at least once a year.", mapping("who.pdf")),
        item("SI-004", "Record them.", mapping("eu.pdf", "optional"))]


def answer(verdict="correct", strictness="same", omits=""):
    return {"required_by_clause": True, "item_adds": "", "item_omits": omits, "strictness": strictness,
            "plant_types_ok": True, "strength_ok": True, "verdict": verdict, "reason": "r"}


class Library(unittest.TestCase):
    def test_twins_share_a_judgement(self):
        u = verify.units(REQS)
        self.assertEqual(len(u), 4)
        self.assertEqual(len({k for k, *_ in u}), 3)          # EU and PIC/S twins share one judgement

    def test_passes(self):
        self.assertTrue(verify.passes(answer()))
        self.assertFalse(verify.passes(answer("incorrect", "stricter")))

    def test_findings_block_verification(self):
        import export
        import layer1
        with unittest.mock.patch.object(layer1, "check_requirement",
                                        lambda r, s: [("SI-003", 1, "numbers", "x")] if r["id"] == "SI-003" else []), \
                unittest.mock.patch.object(layer1, "catalog", lambda: {}), \
                unittest.mock.patch.object(export, "check_library", lambda root, drafts: ["SI-004: copies source"]):
            self.assertEqual(verify.blocked(REQS, "root"), {"SI-003": ["layer 1 numbers: x"],
                                                            "SI-004": ["option A: copies source"]})

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
                    ans = answer()
                    if n == 1 and it["custom_id"].startswith("verify-b"):
                        ans = answer("incorrect", omits="the year")
                    answers.append({"custom_id": it["custom_id"], "answer": ans})
                (run / "answers" / batch.name).write_text(json.dumps({"answers": answers}))
            rep = verify.ingest(run)
            self.assertEqual((rep["judged"], rep["both_pass"], rep["disagree"]), (3, 2, 1))
            self.assertEqual(verify.statuses(REQS, run), {"SI-001": "verified", "SI-002": "verified",
                                                          "SI-003": "unverified", "SI-004": "verified"})


if __name__ == "__main__":
    unittest.main()
