"""Stage 2 consolidation (tools/ai/consolidate.py, D36): rounds, decision checks, library files."""
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ai"))
sys.path.insert(0, str(ROOT / "tools" / "library"))
import consolidate  # noqa: E402
import export  # noqa: E402
import runner  # noqa: E402

SHA = "0" * 64
SOURCES = {"eu.pdf": {"regulator": "EU", "title": "EU GMP"}, "who.pdf": {"regulator": "WHO", "title": "WHO GMP"},
           "india.pdf": {"regulator": "INDIA", "title": "Schedule M"}}
TOPICS = {"SI", "SI.PROG", "SI.REPORT", "QS", "QS.PQS"}
QUOTE_EU = "Self inspections should be conducted in order to monitor the implementation of GMP."
QUOTE_WHO = "Self-inspection should be performed at least once a year."


def ob(oid, source, ref, quote, strength="recommended", plants=("OSD", "INJ")):
    return {"id": oid, "regulator": SOURCES[source]["regulator"], "source": source, "ref": ref,
            "clause_sha256": SHA, "statement": "s", "quote": quote, "strength": strength,
            "plant_types": list(plants), "numbers": [], "draft": "draft-000"}


def decision(oid, req, relation="same", addendum="", topic="", text="", reason="r"):
    return {"obligation": oid, "requirement": req, "relation": relation, "addendum": addendum, "topic": topic,
            "item_text": text, "reason": reason}


def state(obligations):
    return {"draft": "d", "obligations": obligations, "twins": [], "requirements": [], "decisions": {},
            "errors": {}, "rounds": []}


def corpus():
    return export.Corpus({"eu.pdf": [QUOTE_EU], "who.pdf": [QUOTE_WHO]}, [QUOTE_EU, QUOTE_WHO])


class Rounds(unittest.TestCase):
    def test_steps_and_whole_clauses(self):
        s = state([ob("O000", "eu.pdf", "9.1", QUOTE_EU), ob("O001", "eu.pdf", "9.1", QUOTE_EU),
                   ob("O002", "eu.pdf", "9.2", QUOTE_EU), ob("O003", "who.pdf", "8.4", QUOTE_WHO)])
        self.assertEqual([o["id"] for o in consolidate.next_group(s)], ["O000", "O001", "O002"])   # EU step first
        self.assertEqual([o["id"] for o in consolidate.next_group(s, size=2)], ["O000", "O001"])  # whole 9.1
        self.assertEqual([o["id"] for o in consolidate.next_group(s, size=1)], ["O000", "O001"])  # alone if big
        s["decisions"] = {k: {} for k in ("O000", "O001", "O002")}
        self.assertEqual([o["id"] for o in consolidate.next_group(s)], ["O003"])

    def test_round_input_lists_requirements(self):
        s = state([ob("O003", "who.pdf", "8.4", QUOTE_WHO)])
        s["requirements"] = [{"id": "SI-001", "topic": "SI.PROG", "strength": "recommended",
                              "plant_types": ["OSD"], "item_text": "Run a self-inspection programme."}]
        text = consolidate.round_input(s, s["obligations"], SOURCES, {"topics": [
            {"id": "SI", "name": "Self-inspection", "sub": ["SI.PROG"]}]})
        self.assertIn("SI.PROG (Self-inspection)", text)
        self.assertIn("SI-001 [SI.PROG] (recommended; OSD) Run a self-inspection programme.", text)
        self.assertIn("O003 | WHO: WHO GMP | strength recommended", text)
        self.assertIn("quote: " + QUOTE_WHO, text)
        self.assertNotIn("rejected", text)
        s["errors"] = {"O003": ["item text copies source wording: 'x'"]}
        text = consolidate.round_input(s, s["obligations"], SOURCES, {"topics": []})
        self.assertIn("an earlier answer was rejected: item text copies source wording: 'x'", text)


class Apply(unittest.TestCase):
    def setUp(self):
        self.s = state([ob("O000", "eu.pdf", "9.1", QUOTE_EU), ob("O001", "who.pdf", "8.4", QUOTE_WHO,
                                                                 strength="mandatory", plants=["LIQ"])])

    def test_new_and_existing(self):
        errors = consolidate.apply(self.s, ["O000", "O001"], {"decisions": [
            decision("O000", "NEW-1", topic="SI.PROG", text="Run planned self-inspections of GMP."),
            decision("O001", "NEW-1", relation="stricter", addendum="At least once a year.")]}, TOPICS, corpus(),
            existing_ids=["SI-004"])
        self.assertEqual(errors, {})
        self.assertEqual([r["id"] for r in self.s["requirements"]], ["SI-005"])
        r = self.s["requirements"][0]
        self.assertEqual((r["strength"], r["plant_types"]), ("mandatory", ["INJ", "LIQ", "OSD"]))
        self.assertEqual(self.s["decisions"]["O001"]["relation"], "stricter")
        errors = consolidate.apply(self.s, ["O001"], {"decisions": [decision("O001", "SI-005")]}, TOPICS, corpus())
        self.assertEqual(errors, {})

    def test_rejections(self):
        cases = [
            (decision("O000", "NEW-1", relation="adds", addendum="x.", topic="SI.PROG", text="Run them."),
             "first use of a new key must be 'same'"),
            (decision("O000", "NEW-1", topic="SI", text="Run them."), "unknown sub-topic"),
            (decision("O000", "NEW-1", topic="SI.PROG", text=QUOTE_EU), "copies source wording"),
            (decision("O000", "NEW-1", topic="SI.PROG", text="Run them as in Annex 15."), "reference"),
            (decision("O000", "NEW-2"), "never defined"),
            (decision("O000", "SI-099"), "unknown requirement"),
            (decision("O000", "NEW-1", relation="same", addendum="More.", topic="SI.PROG", text="Run them."),
             "takes no addendum"),
            (decision("O009", "NEW-1", topic="SI.PROG", text="Run them."), None),
        ]
        for d, expected in cases:
            s = json.loads(json.dumps(self.s))
            errors = consolidate.apply(s, ["O000"], {"decisions": [d]}, TOPICS, corpus())
            self.assertIn("O000", errors, d)
            if expected:
                self.assertIn(expected, "; ".join(errors["O000"]), d)
            else:
                self.assertEqual(errors["O000"], ["no decision"])
            self.assertEqual(s["decisions"], {})
            self.assertEqual(s["requirements"], [])

    def test_rejected_definition_holds_back_its_uses(self):
        errors = consolidate.apply(self.s, ["O000", "O001"], {"decisions": [
            decision("O000", "NEW-1", topic="SI.NOPE", text="Run them."),
            decision("O001", "NEW-1", relation="stricter", addendum="At least once a year.")]}, TOPICS, corpus())
        self.assertEqual(set(errors), {"O000", "O001"})
        self.assertEqual(self.s["decisions"], {})

    def test_stricter_needs_addendum_and_twice(self):
        errors = consolidate.apply(self.s, ["O000", "O001"], {"decisions": [
            decision("O000", "NEW-1", topic="SI.PROG", text="Run them."),
            decision("O001", "NEW-1", relation="stricter"),
            decision("O000", "NEW-1")]}, TOPICS, corpus())
        self.assertIn("needs an addendum", "; ".join(errors["O001"]))
        self.assertIn("decided twice", "; ".join(errors["O000"]))     # ambiguous: both wait for a later round
        self.assertEqual(self.s["decisions"], {})


class Write(unittest.TestCase):
    def test_library_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft"
            draft.mkdir()
            req = runner.Request("draft-000", "sys", "user", {}, meta={"source": "eu.pdf", "ref": "9.4",
                                                                       "clause_sha256": SHA})
            runner.record_requests(draft, [req], "m")
            runner.write_jsonl(draft / "results.jsonl", [{"custom_id": "draft-000", "ok": True, "answer": {
                "obligations": [], "no_obligation_reason": "A heading only."}}])
            (draft / "topic.json").write_text(json.dumps({"units": [{"source": "eu.pdf", "ref": "9.4", "twins": [
                {"source": "who.pdf", "ref": "8.9"}]}]}))
            s = state([ob("O000", "eu.pdf", "9.1", QUOTE_EU), ob("O001", "who.pdf", "8.4", QUOTE_WHO,
                                                                 strength="mandatory", plants=["LIQ"])])
            s["twins"] = [{**ob("", "india.pdf", "10.1", QUOTE_EU, plants=["OSD"]), "lead": "O000"}]
            consolidate.apply(s, ["O000", "O001"], {"decisions": [
                decision("O000", "NEW-1", topic="SI.PROG", text="Run planned self-inspections of GMP."),
                decision("O001", "NEW-1", relation="stricter", addendum="At least once a year.")]}, TOPICS, corpus())
            by_topic, cov = consolidate.library_files(s, SOURCES, None, draft)
        r = by_topic["SI"][0]
        self.assertEqual((r["id"], r["status"], r["strength"]), ("SI-001", "draft", "mandatory"))
        self.assertEqual([(m["source"], m["relation"]) for m in r["mappings"]],
                         [("eu.pdf", "same"), ("india.pdf", "same"), ("who.pdf", "stricter")])
        self.assertEqual(cov["india"], {"10.1": {"requirements": ["SI-001"]}})
        self.assertEqual(cov["eu"]["9.4"], {"na": "A heading only."})
        self.assertEqual(cov["who"]["8.9"], {"na": "A heading only."})


if __name__ == "__main__":
    unittest.main()
