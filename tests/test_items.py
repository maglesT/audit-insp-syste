"""Per-regulator items from a draft run (tools/ai/items.py, D37)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ai"))
import items  # noqa: E402
import runner  # noqa: E402

SHA = "0" * 64


def mapping(source, ref, quote, topic="SI.PROG", statement="Run self-inspections.", plants=("OSD",)):
    return {"source": source, "ref": ref, "clause_sha256": SHA, "statement": statement, "quote": quote,
            "strength": "recommended", "plant_types": list(plants), "numbers": [], "topic": topic,
            "draft": "draft-000"}


def draft(tmp, mappings, twins=(), empty=()):
    d = Path(tmp) / "draft"
    d.mkdir()
    reqs = [runner.Request(f"draft-{n:03d}", "s", "u", {}, meta={"source": s, "ref": r, "clause_sha256": SHA})
            for n, (s, r) in enumerate(empty)]
    runner.record_requests(d, reqs, "m")
    runner.write_jsonl(d / "results.jsonl", [{"custom_id": r.custom_id, "ok": True, "answer": {
        "obligations": [], "no_obligation_reason": "A heading."}} for r in reqs])
    runner.write_jsonl(d / "mappings.jsonl", mappings)
    runner.write_jsonl(d / "twin-mappings.jsonl", list(twins))
    return d


class Items(unittest.TestCase):
    def test_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = draft(tmp, [mapping("eu.pdf", "9.1", "Self inspections should be conducted."),
                            mapping("who.pdf", "8.3", "A team should be appointed.", topic="SI.TEAM",
                                    statement="Appoint a team.")],
                      twins=[{**mapping("pics.pdf", "9.1", "Self inspections should be conducted."), "twin_of": 0}],
                      empty=[("eu.pdf", "9.4")])
            built, cov = items.build(d, {})
        self.assertEqual([(i["id"], i["mappings"][0]["source"]) for i in built],
                         [("SI-001", "eu.pdf"), ("SI-002", "pics.pdf"), ("SI-003", "who.pdf")])
        self.assertEqual(built[1]["item_text"], built[0]["item_text"])          # twins: identical items
        self.assertEqual(set(built[0]["mappings"][0]), set(items.MAPPING_KEYS))
        self.assertEqual(cov["eu"], {"9.1": {"requirements": ["SI-001"]}, "9.4": {"na": "A heading."}})

    def test_missing_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = draft(tmp, [{**mapping("eu.pdf", "9.1", "x"), "topic": ""}])
            with self.assertRaises(SystemExit):
                items.build(d, {})
            self.assertEqual(items.build(d, {0: "SI.PROG"})[0][0]["topic"], "SI.PROG")

    def test_merge_keeps_ids_and_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, _ = items.build(draft(tmp, [mapping("eu.pdf", "9.1", "Quote one."),
                                               mapping("eu.pdf", "9.2", "Quote two.")]), {})
        first[0]["status"] = "verified"
        first[1]["status"] = "verified"
        first.append({**first[0], "id": "SI-007", "mappings": [{**first[0]["mappings"][0], "clause_ref": "9.9"}]})
        with tempfile.TemporaryDirectory() as tmp:
            new, _ = items.build(draft(tmp, [mapping("eu.pdf", "9.1", "Quote one."),                 # same
                                             mapping("eu.pdf", "9.2", "Quote two.", statement="Changed."),
                                             mapping("eu.pdf", "9.2", "Quote three.")]), {})
        merged, _ = items.merge(first, new)
        st = {(r["mappings"][0]["clause_ref"], r["mappings"][0]["quote"]): (r["id"], r["status"]) for r in merged}
        self.assertEqual(st, {("9.1", "Quote one."): ("SI-001", "verified"),
                              ("9.2", "Quote two."): ("SI-002", "draft"),            # text changed: draft again
                              ("9.2", "Quote three."): ("SI-008", "draft"),          # after the highest id
                              ("9.9", "Quote one."): ("SI-007", "verified")})        # other clause: kept

    def test_merge_retires_items_gone_from_a_redrafted_clause(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, _ = items.build(draft(tmp, [mapping("eu.pdf", "9.1", "Quote one."),
                                               mapping("eu.pdf", "9.1", "Quote two.")]), {})
        with tempfile.TemporaryDirectory() as tmp:
            new, _ = items.build(draft(tmp, [mapping("eu.pdf", "9.1", "Quote one.")]), {})
        merged, _ = items.merge(first, new)
        self.assertEqual([(r["id"], r["status"]) for r in merged], [("SI-001", "draft"), ("SI-002", "retired")])

    def test_write_merges_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "lib"
            built, cov = items.build(draft(tmp, [mapping("eu.pdf", "9.1", "Quote one.")]), {})
            items.write(built, cov, root)
            (Path(tmp) / "draft").rename(Path(tmp) / "draft1")
            built2, cov2 = items.build(draft(tmp, [mapping("who.pdf", "8.1", "Quote two.")]), {})
            rep = items.write(built2, cov2, root)
            doc = json.loads((root / "requirements" / "SI.json").read_text())
            self.assertEqual([r["id"] for r in doc["requirements"]], ["SI-001", "SI-002"])
            self.assertEqual(json.loads((root / "coverage" / "who.json").read_text())["clauses"],
                             {"8.1": {"requirements": ["SI-002"]}})
            self.assertEqual(rep["library_items"], 2)


if __name__ == "__main__":
    unittest.main()
