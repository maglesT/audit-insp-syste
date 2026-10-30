import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import export  # noqa: E402
import model  # noqa: E402

SOURCES = {"eu.pdf": {"regulator": "EU", "applies_to": "OSD;LIQ;SEMI;INJ"},
           "who.pdf": {"regulator": "WHO", "applies_to": "OSD;LIQ;SEMI;INJ"},
           "q7.pdf": {"regulator": "ICH", "applies_to": "API"}}
CLAUSE_TEXT = ("9.3 All self inspections should be recorded. Reports should contain all the observations made "
               "during the inspections and, where applicable, proposals for corrective measures.")
CLAUSES = {"eu.pdf": {"9.3": {"text": CLAUSE_TEXT}}, "who.pdf": {"8.4": {"text": "8.4 The frequency should be "
                                                                         "stated in the procedure."}},
           "q7.pdf": {}}


def mapping(source, regulator_relation="same", addendum="", strength="recommended", plant_types=("OSD", "INJ")):
    return {"source": source, "clause_ref": "9.3", "clause_sha256": "0" * 64, "quote": "All self inspections should "
            "be recorded", "strength": strength, "relation": regulator_relation, "plant_types": list(plant_types),
            "addendum": addendum}


def requirement(rid, mappings, status="verified", plant_types=("OSD", "INJ"), general=False, text=None):
    return {"id": rid, "topic": "SI.REPORT", "item_text": text or "Keep a written record of every self-inspection.",
            "strength": "recommended", "plant_types": list(plant_types), "parameters": {}, "general": general,
            "status": status, "mappings": mappings}


class Compile(unittest.TestCase):
    def test_strictest_wins(self):
        req = requirement("SI-001", [mapping("eu.pdf"),
                                     mapping("who.pdf", "stricter", "Sign each record within one week.",
                                             "mandatory")])
        eu = export.compile_items([req], SOURCES, ["EU"], "OSD")
        self.assertEqual(eu, [{"id": "SI-001", "item_text": "Keep a written record of every self-inspection.",
                               "topic": "SI.REPORT", "regulators": ["EU"], "plant_types": ["OSD"],
                               "strength": "recommended"}])
        both = export.compile_items([req], SOURCES, ["EU", "WHO"], "OSD")[0]
        self.assertEqual(both["item_text"], "Keep a written record of every self-inspection. Sign each record "
                                            "within one week.")
        self.assertEqual((both["regulators"], both["strength"]), (["EU", "WHO"], "mandatory"))

    def test_what_is_left_out(self):
        reqs = [requirement("SI-001", [mapping("eu.pdf")], status="draft"),            # not verified
                requirement("SI-002", [mapping("eu.pdf")], plant_types=("INJ",)),      # other plant type
                requirement("SI-003", [mapping("who.pdf")]),                            # other regulator
                requirement("SI-004", [mapping("eu.pdf", plant_types=("INJ",))]),       # mapping not for OSD
                requirement("SI-005", [mapping("eu.pdf", plant_types=("INJ",))], general=True),
                requirement("SI-006", [mapping("eu.pdf", "looser", "Less is fine.")])]  # looser: no addendum
        items = export.compile_items(reqs, SOURCES, ["EU"], "OSD")
        self.assertEqual([i["id"] for i in items], ["SI-005", "SI-006"])
        self.assertNotIn("Less is fine", items[1]["item_text"])

    def test_export_document(self):
        req = requirement("SI-001", [mapping("eu.pdf")])
        doc = export.export([req], SOURCES, ["EU", "EMA"], "OSD", {"SI.REPORT": "Self-inspection"})
        self.assertEqual(set(doc), set(export.TOP_FIELDS))
        self.assertEqual(doc["regulators"], ["EU"])                       # EU and EMA show as one name
        self.assertEqual(doc["topics"], {"SI.REPORT": "Self-inspection"})
        self.assertEqual(set(doc["items"][0]), set(export.ITEM_FIELDS))
        text = json.dumps(doc)
        for secret in ("9.3", "All self inspections should be recorded", "eu.pdf", "clause"):
            self.assertNotIn(secret, text)


class OptionA(unittest.TestCase):
    def setUp(self):
        self.known = export.shingles([c["text"] for f in CLAUSES.values() for c in f.values()])
        self.doc = export.export([requirement("SI-001", [mapping("eu.pdf")])], SOURCES, ["EU"], "OSD",
                                 {"SI.REPORT": "Self-inspection"})

    def test_clean_export_passes(self):
        self.assertEqual(export.check(self.doc, self.known), [])

    def test_extra_or_source_fields_fail(self):
        self.doc["items"][0]["quote"] = "x"
        self.doc["source_list"] = []
        found = export.check(self.doc, self.known)
        self.assertTrue(any("field 'source_list' is not allowed" in f for f in found))
        self.assertTrue(any("fields must be exactly" in f for f in found))
        self.assertTrue(any(".quote: field name speaks" in f for f in found))

    def test_copied_words_fail(self):
        copied = ("Reports should contain ALL the observations made during the inspections, and where applicable "
                  "proposals for corrective measures.")                    # case and punctuation changed
        self.doc["items"][0]["item_text"] = copied
        self.assertTrue(any("12 consecutive words" in f for f in export.check(self.doc, self.known)))
        eleven = "Remember: reports should contain all the observations made during the inspections today."
        self.doc["items"][0]["item_text"] = eleven                        # 11 words in a row: allowed
        self.assertEqual(export.check(self.doc, self.known), [])

    def test_clause_references_fail(self):
        for text in ("Follow Annex 15 for validation.", "As required by 21 CFR 211.68(b).",
                     "See clause 10.8.2.", "Schedule M asks for this.", "Chapter 4 applies.", "See § 5."):
            self.doc["items"][0]["item_text"] = text
            self.assertTrue(any("clause reference" in f for f in export.check(self.doc, self.known)), text)
        for text in ("Keep the pH at 6.5.", "Review at least once a year.", "Part of the process is cleaning."):
            self.doc["items"][0]["item_text"] = text
            self.assertEqual(export.check(self.doc, self.known), [], text)

    def test_topic_ids_are_not_field_names(self):
        self.doc["topics"] = {"DOC.REF": "Documentation"}                  # a topic id containing "REF"
        self.assertEqual(export.check(self.doc, self.known), [])


class Library(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        shutil.copy(model.LIBRARY / "topics.json", self.root / "topics.json")
        (self.root / "requirements").mkdir()

    def write(self, reqs):
        (self.root / "requirements" / "SI.json").write_text(json.dumps({"requirements": reqs}))

    def test_check_library(self):
        self.write([requirement("SI-001", [mapping("eu.pdf")])])
        self.assertEqual(export.check_library(self.root, SOURCES, CLAUSES.get), [])
        self.write([requirement("SI-001", [mapping("eu.pdf")], text="Ensure all self inspections should be "
                                "recorded. Reports should contain all the observations made during inspections.")])
        found = export.check_library(self.root, SOURCES, CLAUSES.get)
        self.assertTrue(found)
        self.assertTrue(all("consecutive words" in f for f in found))
        self.assertTrue(any(f.startswith("EU/OSD") for f in found))

    def test_every_compilation_is_checked(self):
        combos = list(export.compilations(SOURCES))
        self.assertIn((["EU", "ICH", "WHO"], "OSD"), combos)
        self.assertIn((["ICH"], "API"), combos)
        self.assertEqual(len(combos), len(model.PLANT_TYPES) * 4)

    def test_real_library_passes(self):
        self.assertEqual(export.check_library(), [])

    def test_regulator_names_cover_the_catalog(self):
        self.assertEqual({r["regulator"] for r in export.catalog().values()} - set(export.REGULATOR_NAMES), set())


if __name__ == "__main__":
    unittest.main()
