import contextlib
import io
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
           "ema.pdf": {"regulator": "EMA", "applies_to": "ALL"},
           "who.pdf": {"regulator": "WHO", "applies_to": "OSD;LIQ;SEMI;INJ"},
           "cfr.xml": {"regulator": "FDA", "applies_to": "OSD;LIQ;SEMI;INJ"},
           "pics.pdf": {"regulator": "PICS", "applies_to": "ALL"}}
CLAUSE_TEXT = ("9.3 All self inspections should be recorded. Reports should contain all the observations made "
               "during the inspections and, where applicable, proposals for corrective measures.")
SEGMENTS = {
    "pics.pdf": [],
    "eu.pdf": [{"kind": "toc", "text": "Contents Chapter 9 Self inspection page 1"},
               {"kind": "clause", "text": CLAUSE_TEXT},
               {"kind": "unnumbered", "text": "Weigh and delump the required amount of active substance and "
                                              "intra-granular excipients before granulation starts."}],
    "ema.pdf": [{"kind": "clause", "text": "Water for injections should be stored in a loop."}],
    "who.pdf": [{"kind": "clause", "text": "8.4 The frequency should be stated in the procedure."},
                {"kind": "clause", "text": "Results outside these limits will require speciﬁed action and "
                                           "investiga­tion by the quality unit."}],
    "cfr.xml": [{"kind": "clause", "text": "(b) Personnel shall practice good sanitation and health habits."},
                {"kind": "clause", "text": "(c) Only personnel authorized by supervisory personnel shall enter "
                                           "those areas of the buildings."}],
}


def mapping(source, strength="recommended", plant_types=("OSD", "INJ"), quote="All self inspections should be recorded"):
    return {"source": source, "clause_ref": "9.3", "clause_sha256": "0" * 64, "quote": quote, "strength": strength,
            "plant_types": list(plant_types)}


def requirement(rid, mappings, status="verified", plant_types=("OSD", "INJ"), general=False, text=None,
                strength="recommended"):
    return {"id": rid, "topic": "SI.REPORT", "item_text": text or "Keep a written record of every self-inspection.",
            "strength": strength, "plant_types": list(plant_types), "parameters": {}, "general": general,
            "status": status, "mappings": mappings}


def corpus(reqs=()):
    return export.corpus_for(list(reqs), SOURCES, SEGMENTS.get, all_sources=True)


class Compile(unittest.TestCase):
    def test_one_item_per_regulator_and_twins_shown_once(self):
        """D37: each item is one regulator's obligation; identical items of selected regulators show once."""
        reqs = [requirement("SI-001", [mapping("eu.pdf")]), requirement("SI-002", [mapping("pics.pdf")]),
                requirement("SI-003", [mapping("who.pdf", "mandatory")], text="Sign each record within one week.",
                            strength="mandatory")]
        eu = export.compile_items(reqs, SOURCES, ["EU"], "OSD")
        self.assertEqual(eu, [{"id": "SI-001", "item_text": "Keep a written record of every self-inspection.",
                               "topic": "SI.REPORT", "regulators": ["EU"], "plant_types": ["OSD"],
                               "strength": "recommended", "group": "SI-001"}])
        both = export.compile_items(reqs, SOURCES, ["EU", "PIC/S", "WHO"], "OSD")
        self.assertEqual([(i["id"], i["regulators"], i["strength"]) for i in both],
                         [("SI-001", ["EU", "PIC/S"], "recommended"), ("SI-003", ["WHO"], "mandatory")])
        self.assertEqual(export.compile_items(reqs, SOURCES, ["PIC/S"], "OSD")[0]["id"], "SI-002")

    def test_near_identical_items_share_a_group(self):
        reqs = [requirement("SI-001", [mapping("eu.pdf")], text="Keep a written record of every self-inspection."),
                requirement("SI-002", [mapping("who.pdf")], text="Keep a written record of every self-inspection "
                                                                  "carried out."),
                requirement("SI-003", [mapping("who.pdf")], text="Appoint an independent team.")]
        items = export.compile_items(reqs, SOURCES, ["EU", "WHO"], "OSD")
        self.assertEqual([i["group"] for i in items], ["SI-001", "SI-001", "SI-003"])

    def test_what_is_left_out(self):
        reqs = [requirement("SI-001", [mapping("eu.pdf")], status="draft"),            # not verified
                requirement("SI-002", [mapping("eu.pdf")], plant_types=("INJ",)),      # other plant type
                requirement("SI-003", [mapping("who.pdf")]),                            # other regulator
                requirement("SI-004", [mapping("eu.pdf", plant_types=("INJ",))]),       # mapping not for OSD
                requirement("SI-005", [mapping("eu.pdf", plant_types=("INJ",))], general=True)]
        items = export.compile_items(reqs, SOURCES, ["EU"], "OSD")
        self.assertEqual([i["id"] for i in items], ["SI-005"])

    def test_eu_includes_ema(self):
        req = requirement("SI-001", [mapping("ema.pdf")])
        self.assertEqual([i["regulators"] for i in export.compile_items([req], SOURCES, ["EU"], "OSD")], [["EU"]])
        self.assertEqual(export.selection("EU,EMA,pics,US FDA"), ["EU", "PIC/S", "US FDA"])
        with self.assertRaises(SystemExit):
            export.selection("Mars")
        with self.assertRaises(ValueError):
            export.export([req], SOURCES, ["eu"], "OSD", {})

    def test_export_document(self):
        req = requirement("SI-001", [mapping("eu.pdf")])
        doc = export.export([req], SOURCES, ["EU", "India"], "OSD", {"SI.REPORT": "Self-inspection"})
        self.assertEqual(set(doc), set(export.TOP_FIELDS))
        self.assertEqual(doc["regulators"], ["EU"])                       # India has no item: not in the header
        self.assertEqual(doc["topics"], {"SI.REPORT": "Self-inspection"})
        self.assertEqual(set(doc["items"][0]), set(export.ITEM_FIELDS))
        text = json.dumps(doc)
        for secret in ("9.3", "All self inspections should be recorded", "eu.pdf", "clause"):
            self.assertNotIn(secret, text)
        empty = export.export([req], SOURCES, ["India"], "LIQ", {"SI.REPORT": "Self-inspection"})
        self.assertEqual((empty["regulators"], empty["items"]), ([], []))


class OptionA(unittest.TestCase):
    def setUp(self):
        self.known = corpus([requirement("SI-001", [mapping("eu.pdf")])])
        self.doc = export.export([requirement("SI-001", [mapping("eu.pdf")])], SOURCES, ["EU"], "OSD",
                                 {"SI.REPORT": "Self-inspection"})

    def found(self, text):
        return export.check_text(text, self.known)

    def test_clean_export_passes(self):
        self.assertEqual(export.check(self.doc, self.known), [])

    def test_extra_or_source_fields_fail(self):
        self.doc["items"][0]["quote"] = "x"
        self.doc["source_list"] = []
        found = export.check(self.doc, self.known)
        self.assertTrue(any("field 'source_list' is not allowed" in f for f in found))
        self.assertTrue(any("fields must be exactly" in f for f in found))
        self.assertTrue(any(".quote: field name speaks" in f for f in found))

    def test_values_are_checked(self):
        self.doc["items"][0]["regulators"] = ["EudraLex"]
        self.doc["items"][0]["topic"] = "NOPE"
        self.doc["topics"] = {"SI.REPORT": {"nested": "x"}}
        found = " ".join(export.check(self.doc, self.known))
        for part in ("regulators: unknown", "topics: must map", "topic: not in"):
            self.assertIn(part, found)

    def test_copied_words_fail(self):
        self.assertTrue(self.found("Reports should contain ALL the observations made during the inspections, and "
                                   "where applicable proposals for corrective measures."))
        self.assertEqual(self.found("Remember: reports should contain all the observations made during the "
                                    "inspections today."), [])               # 11 words in a row

    def test_unnumbered_text_and_runs_across_segments(self):
        self.assertTrue(self.found("Weigh and delump the required amount of active substance and intra-granular "
                                   "excipients first."))                     # unnumbered segment
        self.assertTrue(self.found("Personnel shall practice good sanitation and health habits."))  # short clause
        self.assertTrue(self.found("Keep good sanitation and health habits. Only personnel authorized by "
                                   "supervisory personnel shall enter."))     # across two clauses
        self.assertEqual(self.found("Contents chapter self inspection page."), [])   # contents entries ignored

    def test_unicode_tricks_do_not_hide_copies(self):
        typed = "Results outside these limits will require specified action and investigation by the quality unit."
        self.assertTrue(self.found(typed))                                    # source has a ligature, soft hyphen
        self.assertTrue(self.found("Reports should contain all the оbservations made during the inspections and "
                                   "where applicable."))                     # Cyrillic о
        self.assertTrue(self.found("Ｒeports should contain all the observations made during the inspections and "
                                   "where applicable."))                     # full-width R

    def test_short_quotes_fail(self):
        known = corpus([requirement("SI-001", [mapping("eu.pdf", quote="stored in a loop at all times")])])
        self.assertTrue(export.check_text("Keep water stored in a loop at all times.", known))

    def test_clause_references_fail(self):
        for text in ("Follow Annex 15 for validation.", "As required by 21 CFR 211.68(b).", "See clause 10.8.2.",
                     "Schedule M asks for this.", "Chapter 4 applies.", "See § 5.", "Annexes 1 and 15 apply.",
                     "Annex15 applies.", "Chapter-4 applies.", "per 21CFR211", "Art. 5(3) applies.", "sect. 5",
                     "para. 4 says", "point 4.29 says", "See 211.68.", "As in ICH Q9.", "As in PE 009.",
                     "WHO TRS guidance.", "EudraLex says so.", "EMA/CHMP/QWP/245074/2015", "Part I applies."):
            self.assertTrue(any("reference" in f for f in self.found(text)), text)
        for text in ("Keep the pH at 6.5.", "Review at least once a year.", "Part of the process is cleaning.",
                     "Check part c of the form.", "Store at 2 to 8 °C."):
            self.assertEqual(self.found(text), [], text)

    def test_allowlist(self):
        self.assertTrue(export.check_text("Record it in Section 1 of the batch record.", self.known))
        self.assertEqual(export.check_text("Record it in Section 1 of the batch record.", self.known,
                                           ["section 1 of the batch record"]), [])

    def test_topic_ids_are_not_field_names(self):
        self.doc["topics"] = {"DOC.REF": "Documentation"}
        self.doc["items"][0]["topic"] = "DOC.REF"
        self.assertEqual(export.check(self.doc, self.known), [])


class Library(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        shutil.copy(model.LIBRARY / "topics.json", self.root / "topics.json")
        (self.root / "requirements").mkdir()

    def write(self, reqs, allow=None):
        (self.root / "requirements" / "SI.json").write_text(json.dumps({"requirements": reqs}))
        if allow is not None:
            (self.root / export.ALLOW_FILE).write_text(json.dumps({"phrases": allow}))

    def check(self):
        return export.check_library(self.root, SOURCES, SEGMENTS.get)

    def test_check_library(self):
        self.write([requirement("SI-001", [mapping("eu.pdf")])])
        self.assertEqual(self.check(), [])
        self.write([requirement("SI-001", [mapping("eu.pdf")], text="Ensure all self inspections should be "
                                "recorded. Reports should contain all the observations made during inspections.")])
        found = self.check()
        self.assertTrue(found and all("copies source wording" in f for f in found))
        self.assertTrue(any(f.startswith("SI-001: ") for f in found))
        self.assertTrue(any(f.startswith("EU/OSD") for f in found))

    def test_every_item_text_is_checked(self):
        req = requirement("SI-001", [mapping("eu.pdf")], text="Keep it for one year; Annex 15 has more.")
        self.assertEqual(export.visible_texts(req, SOURCES), ["Keep it for one year; Annex 15 has more."])
        self.write([req])
        self.assertTrue(any("reference" in f for f in self.check()))
        self.write([req], allow=["Annex 15 has more"])
        self.assertEqual(self.check(), [])

    def test_compilations(self):
        combos = list(export.compilations())
        self.assertIn((export.NAMES, "OSD"), combos)
        self.assertIn((["EU"], "API"), combos)
        self.assertEqual(len(combos), len(model.PLANT_TYPES) * (len(export.NAMES) + 1))

    def test_cli(self):
        self.write([])                                        # the CLI uses the real catalog and sources
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as stop:
            export.main(["check", "--library", str(self.root)])
        self.assertEqual(stop.exception.code, 0)
        self.assertIn("option A: 0 findings (0 verified items of 0)", out.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            export.main(["build", "--library", str(self.root), "--regulators", "EU,PICS", "--plant", "OSD"])
        doc = json.loads(out.getvalue())
        self.assertEqual((doc["items"], doc["plant_type"]), ([], "OSD"))
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            export.main(["build", "--library", str(self.root), "--plant", "OSD"])

    def test_drafts_are_listed_not_failed(self):
        draft = requirement("SI-001", [mapping("eu.pdf")], status="draft", text="Ensure all self inspections should "
                            "be recorded and reports contain all the observations made during the inspections.")
        self.write([draft])
        self.assertEqual(self.check(), [])
        self.assertTrue(export.check_library(self.root, SOURCES, SEGMENTS.get, all_sources=True, drafts=True))

    def test_real_library_passes(self):
        self.assertEqual(export.check_library(), [])

    def test_regulator_names_cover_the_catalog(self):
        self.assertEqual({r["regulator"] for r in export.catalog().values()} - set(export.REGULATOR_NAMES), set())


if __name__ == "__main__":
    unittest.main()
