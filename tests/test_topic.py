"""Topic units for S3 (tools/ai/topic.py) and twin mappings (D36, tools/ai/pilot.py)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ai"))
import pilot  # noqa: E402
import topic  # noqa: E402


def clause(text, heading="", kind="clause"):
    return {"text": text, "heading": heading or text[:60], "kind": kind, "sha256": str(hash(text))}


SOURCES = {
    "eu.pdf": {"regulator": "EU", "priority": "must", "phase": "pilot", "applies_to": "ALL"},
    "who.pdf": {"regulator": "WHO", "priority": "must", "phase": "pilot", "applies_to": "ALL"},
    "india.pdf": {"regulator": "INDIA", "priority": "must", "phase": "pilot", "applies_to": "OSD;INJ"},
    "draft.pdf": {"regulator": "EU", "priority": "reference", "phase": "pilot", "applies_to": "ALL"},
    "japan.pdf": {"regulator": "JAPAN", "priority": "must", "phase": "phase2", "applies_to": "ALL"},
}
SI = "Self inspections should be conducted regularly."
TREES = {
    "eu.pdf": {"Chapter 9": clause("CHAPTER 9 SELF INSPECTION", kind="section"),
               "Chapter 9 9.1": clause("9.1 " + SI),
               "Chapter 9 9.2": clause("9.2 Reports should be kept by the quality unit."),
               "2.5": clause("2.5 Internal Audits (Self Inspection)"),
               "2.51": clause("2.51 Audit findings should be documented."),
               "2.6": clause("2.6 Batches should be released by a QP."),
               "_toc:9": clause("9 Self inspection should ... 12", kind="toc"),
               "3.1": clause("3.1 Self inspection is described in chapter 9.")},
    "who.pdf": {"8.1": clause("8.1 " + SI), "8.2": clause("8.2 The team should be independent; self-inspection."),
                "8.3": clause("8.3 Suppliers should be audited."),
                "9.1": clause("9.1 Water should be tested.")},
    "india.pdf": {"Part I 10.1": clause("10.1. " + SI), "Part I 10.2": clause("10.2. Self- inspection shall be "
                                                                              "recorded."),
                  "Part I 10.8.1": clause("10.8.1. Suppliers shall be audited."),
                  "Part I 11.1": clause("11.1. " + "Self inspection shall be planned. " * 300)},
    "draft.pdf": {"1": clause("1 " + SI)},
    "japan.pdf": {"1": clause("1 " + SI)},
}


class Select(unittest.TestCase):
    def test_under(self):
        self.assertTrue(topic.under("Chapter 9 9.1", "Chapter 9"))
        self.assertTrue(topic.under("Part XII 2.4.2", "Part XII 2.4"))
        self.assertTrue(topic.under("2.41", "2.4"))
        self.assertTrue(topic.under("8.3", "8"))
        self.assertFalse(topic.under("2.4", "2.4"))
        self.assertFalse(topic.under("2.5", "2.4"))
        self.assertFalse(topic.under("2.410", "2.4"))
        self.assertFalse(topic.under("Part II 2.41", "Part I 2.4"))

    def test_rules(self):
        units, too_long = topic.select("self-inspection", SOURCES, TREES.get)
        why = {(u["source"], u["ref"]): u["why"] for u in units}
        self.assertEqual(why, {
            ("eu.pdf", "Chapter 9 9.1"): "text",
            ("eu.pdf", "Chapter 9 9.2"): "heading",      # under the section heading "CHAPTER 9 SELF INSPECTION"
            ("eu.pdf", "2.51"): "heading",
            ("who.pdf", "8.1"): "text", ("who.pdf", "8.2"): "text", ("who.pdf", "8.3"): "chapter",
            ("india.pdf", "Part I 10.1"): "text", ("india.pdf", "Part I 10.2"): "text",
            ("india.pdf", "Part I 10.8.1"): "chapter"})
        self.assertEqual([(u["source"], u["ref"]) for u in too_long], [("india.pdf", "Part I 11.1")])

    def test_left_out(self):
        units, _ = topic.select("self-inspection", SOURCES, TREES.get)
        keys = {(u["source"], u["ref"]) for u in units}
        for key in [("eu.pdf", "2.6"), ("eu.pdf", "_toc:9"), ("eu.pdf", "3.1"), ("who.pdf", "9.1"),
                    ("draft.pdf", "1"), ("japan.pdf", "1"), ("eu.pdf", "2.5")]:
            self.assertNotIn(key, keys, key)          # no topic, contents, no obligation, reference, phase 2

    def test_twins(self):
        units, _ = topic.select("self-inspection", SOURCES, TREES.get)
        drafted = topic.with_twins(units, TREES.get)
        lead = {(u["source"], u["ref"]): [(t["source"], t["ref"]) for t in u["twins"]] for u in drafted}
        self.assertEqual(lead[("eu.pdf", "Chapter 9 9.1")], [("who.pdf", "8.1"), ("india.pdf", "Part I 10.1")])
        self.assertNotIn(("who.pdf", "8.1"), lead)
        s = topic.summary(drafted)
        self.assertEqual((s["units"], s["drafted"], s["twins"]), (len(units), len(units) - 2, 2))


class Twins(unittest.TestCase):
    def mapping(self, quote, plants=("OSD", "LIQ")):
        return {"source": "eu.pdf", "ref": "Chapter 9 9.1", "clause_sha256": "x", "statement": "Run them.",
                "quote": quote, "strength": "recommended", "plant_types": list(plants), "numbers": []}

    def test_copies(self):
        units = [{"source": "eu.pdf", "ref": "Chapter 9 9.1", "twins": [
            {"source": "who.pdf", "ref": "8.1", "regulator": "WHO"},
            {"source": "india.pdf", "ref": "Part I 10.1", "regulator": "INDIA"}]}]
        copies, rejected = pilot.twin_mappings([self.mapping(SI)], units, SOURCES, TREES.get)
        self.assertEqual([(c["source"], c["plant_types"], c["twin_of"]) for c in copies],
                         [("who.pdf", ["OSD", "LIQ"], 0), ("india.pdf", ["OSD"], 0)])
        self.assertEqual(copies[1]["clause_sha256"], TREES["india.pdf"]["Part I 10.1"]["sha256"])
        self.assertEqual(rejected, [])

    def test_rejects(self):
        units = [{"source": "eu.pdf", "ref": "Chapter 9 9.1", "twins": [
            {"source": "india.pdf", "ref": "Part I 10.2", "regulator": "INDIA"}]}]
        _, rejected = pilot.twin_mappings([self.mapping(SI)], units, SOURCES, TREES.get)
        self.assertEqual(rejected[0]["reason"], "quote not found in the twin clause")
        units[0]["twins"][0]["ref"] = "Part I 10.1"
        _, rejected = pilot.twin_mappings([self.mapping(SI, plants=["LIQ"])], units, SOURCES, TREES.get)
        self.assertEqual(rejected[0]["reason"], "no plant type inside the twin source's scope")

    def test_twin_quote_keeps_the_twins_wording(self):
        self.assertEqual(pilot.twin_quote("The self-inspection shall be documented", "1. The self- inspection shall "
                                          "be documented."), "The self- inspection shall be documented")
        self.assertEqual(pilot.twin_quote("The self- inspection", "The self-inspection is done."), "The self-inspection")
        self.assertIsNone(pilot.twin_quote("The self inspection shall", "The self-inspection shall"))

    def test_coverage_ignores_the_clause_number(self):
        req = pilot.runner.Request("draft-000", "s", "u", {}, meta={"source": "x", "ref": "9.3"})
        trees = {"x": {"9.3": {"text": "9.3 All self inspections should be recorded."}}}
        m = {"source": "x", "ref": "9.3", "quote": "All self inspections should be recorded."}
        self.assertEqual(pilot.coverage([req], [m], trees.get), [])

    def test_topic_pilot(self):
        self.assertEqual(pilot.topic_pilot([{"source": "a", "ref": "1"}, {"source": "b", "ref": "2"},
                                            {"source": "a", "ref": "3"}]), {"a": ["1", "3"], "b": ["2"]})


if __name__ == "__main__":
    unittest.main()
