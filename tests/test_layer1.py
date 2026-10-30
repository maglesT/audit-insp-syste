import copy
import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import layer1  # noqa: E402
import model  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "library"
SOURCES = layer1.catalog()


def requirement(n=0):
    return copy.deepcopy(model.requirements(FIXTURE)[n])


def checks(req):
    return [(f[1], f[2]) for f in layer1.check_requirement(req, SOURCES)]


class Mappings(unittest.TestCase):
    def test_fixture_passes(self):
        findings, coverage, fingerprints = layer1.run(FIXTURE)
        self.assertEqual(findings, [])
        self.assertEqual(fingerprints, [])
        share, missing = coverage["eu-cap9_en"]
        self.assertIn("Chapter 9 9.1", missing)
        self.assertLess(share, 1)

    def test_quote_not_in_clause(self):
        req = requirement()
        req["mappings"][0]["quote"] = "shall be at least twice in a year."
        self.assertIn((1, "quote"), checks(req))

    def test_unknown_clause_and_changed_text(self):
        req = requirement()
        req["mappings"][0]["clause_ref"] = "Part I 99.9"
        self.assertEqual(checks(req), [(1, "clause"), (0, "numbers")])
        req = requirement()
        req["mappings"][0]["clause_sha256"] = "0" * 64
        self.assertEqual(checks(req), [(1, "clause")])

    def test_numbers(self):
        req = requirement()
        req["parameters"]["frequency_max_months"] = 6
        self.assertIn((0, "numbers"), checks(req))
        req = requirement()
        req["item_text"] += " Keep reports for 5 years."
        self.assertEqual(checks(req), [(0, "numbers")])
        self.assertTrue(layer1.number_found("1", ["at least one report"]))      # word form counts
        self.assertFalse(layer1.number_found("1", ["at least 10 reports"]))
        self.assertTrue(layer1.number_found("0.5", ["not more than 0,5 %"]))     # decimal comma

    def test_strength(self):
        req = requirement(1)
        req["mappings"][0]["strength"] = "mandatory"
        self.assertIn((1, "strength"), checks(req))             # quote says "should"
        req = requirement(1)
        req["strength"] = "mandatory"
        self.assertEqual(checks(req), [(0, "strength")])        # strictest mapping is recommended

    def test_scope(self):
        req = requirement(1)
        req["mappings"][0]["plant_types"].append("API")
        req["plant_types"].append("API")
        self.assertIn((1, "scope"), checks(req))                # EU Part I does not cover API
        req = requirement(1)
        req["plant_types"].append("API")
        self.assertEqual(checks(req), [(0, "scope")])           # no mapping covers API

    def test_invalid_library_stops_before_checks(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(FIXTURE, tmp, dirs_exist_ok=True)
        path = tmp / "requirements" / "SI.json"
        data = json.loads(path.read_text())
        data["requirements"][0]["strength"] = "must"
        path.write_text(json.dumps(data))
        findings, _, _ = layer1.run(tmp)
        self.assertTrue(findings and all(f[2] == "structure" for f in findings))


class ReviewFindings(unittest.TestCase):
    """Cases where an earlier version passed what it should have failed."""

    def test_decimals_signs_and_exponents(self):
        self.assertFalse(layer1.number_found("1.5", ["at least one metre"]))
        self.assertFalse(layer1.number_found("12.5", ["every twelve months"]))
        self.assertEqual(layer1.numbers_in("10³ CFU/g and 10^6"), {"10³", "10^6"})
        self.assertFalse(layer1.number_found("10³", ["not more than 10⁶ CFU/g"]))
        self.assertEqual(layer1.numbers_in("store at −20 °C"), {"-20"})
        self.assertFalse(layer1.number_found("-20", ["store at 20 °C"]))
        self.assertEqual(layer1.numbers_in("2-8 °C"), {"2", "8"})

    def test_equivalents_are_whole_words(self):
        self.assertTrue(layer1.equivalent_found(("annually",), ["reviewed annually."]))
        self.assertFalse(layer1.equivalent_found(("annually",), ["reviewed semi-annually."]))
        self.assertFalse(layer1.equivalent_found(("annually",), ["reviewed biannually."]))

    def test_string_parameters_and_number_words_are_checked(self):
        req = requirement()
        req["parameters"]["storage"] = "2-8 °C"
        self.assertEqual(checks(req), [(0, "numbers"), (0, "numbers")])
        req = requirement()
        req["item_text"] = "Self-inspections are run at least twice every year."
        self.assertEqual(checks(req), [(0, "numbers")])
        req = requirement()
        req["item_text"] = "Self-inspections are run at least once every year."   # "once" is in the quote
        self.assertEqual(checks(req), [])

    def test_strength_of_main_clause(self):
        self.assertEqual(layer1.strength_of("Where sterilisation is required, the process should be validated."),
                         "recommended")
        self.assertEqual(layer1.strength_of("Equipment which has to be moved should be checked."), "recommended")
        self.assertEqual(layer1.strength_of("Products may not be released before certification."), "mandatory")
        self.assertEqual(layer1.strength_of("Revised in May 2022, records should be kept."), "recommended")
        self.assertEqual(layer1.strength_of("Records shall be kept."), "mandatory")
        self.assertEqual(layer1.strength_of("Samples may be pooled."), "optional")

    def test_scope_general_and_empty_plant_types(self):
        req = requirement(1)
        req["mappings"][0]["plant_types"].append("API")
        req["plant_types"].append("API")
        req["general"] = True
        self.assertEqual(checks(req), [])                       # explicitly general: allowed
        tmp = self.copy()
        self.edit(tmp, lambda reqs: reqs[1]["mappings"][0].update(plant_types=[]))
        self.assertTrue(any("plant_types" in e for e in model.validate(tmp)))

    def copy(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(FIXTURE, tmp, dirs_exist_ok=True)
        return tmp

    def edit(self, root, change, name="requirements/SI.json"):
        path = root / name
        data = json.loads(path.read_text())
        change(data["requirements"] if "requirements" in data else data["clauses"])
        path.write_text(json.dumps(data))

    def test_coverage_entries_must_point_at_real_mappings(self):
        tmp = self.copy()
        self.edit(tmp, lambda c: c.update({"Chapter 9 9.1": {"requirements": ["SI-002"]},
                                           "Chapter 9 9.9": {"na": "x"}}), "coverage/eu-cap9_en.json")
        messages = [f[3] for f in layer1.run(tmp)[0]]
        self.assertIn("SI-002 has no mapping to this clause", messages)
        self.assertIn("no such clause", messages)
        self.edit(tmp, lambda reqs: reqs[1].update(status="retired"))
        self.assertIn("SI-002 is retired", [f[3] for f in layer1.run(tmp)[0]])
        self.edit(tmp, lambda c: c.update({"Chapter 9 9.2": {"requirements": []}}), "coverage/eu-cap9_en.json")
        self.assertTrue(any("non-empty" in f[3] for f in layer1.run(tmp)[0]))

    def test_unknown_coverage_source_and_changed_fingerprint(self):
        tmp = self.copy()
        (tmp / "coverage" / "no-such-source.json").write_text('{"clauses": {}}')
        self.assertIn(("coverage no-such-source", 0, "coverage", "no such source in sources/catalog.csv"),
                      layer1.run(tmp)[0])
        req = requirement(1)
        self.assertEqual(layer1.check_requirement(req, SOURCES, changed={"eu-cap9_en.pdf"})[0][2], "fingerprint")
        self.assertNotIn("eu-cap9_en.pdf", layer1.uncovered_sources(tmp))


class OnDemand(unittest.TestCase):
    def test_parse_on_demand_matches_stored_clauses(self):
        """In CI library/clauses is not there (gitignored); the clause tree is then parsed from the source."""
        source = "eu-cap9_en.pdf"
        stored = layer1.CLAUSES / "eu-cap9_en.jsonl"
        if not stored.exists():
            self.skipTest("library/clauses not built")
        layer1.clauses_of.__defaults__[0].pop(source, None)
        original = layer1.CLAUSES
        layer1.CLAUSES = Path(tempfile.mkdtemp())
        try:
            parsed = layer1.clauses_of(source)
        finally:
            shutil.rmtree(layer1.CLAUSES)
            layer1.CLAUSES = original
            layer1.clauses_of.__defaults__[0].pop(source, None)
        self.assertEqual(parsed, layer1.clauses_of(source))



class Conditions(unittest.TestCase):
    """Check 9 (D35): condition and limit wording in a quote needs a counterpart in the item."""

    def test_groups(self):
        c = layer1.conditions_in
        self.assertEqual(c("Where applicable, proposals should be recorded."), {"condition"})
        self.assertEqual(c("Samples should be taken prior to release."), {"before"})
        self.assertEqual(c("At least once a year."), {"at_least"})
        self.assertEqual(c("Report within 30 days."), {"deadline"})
        self.assertEqual(c("Not more than 2 batches."), {"at_most"})
        self.assertEqual(c("Unless justified, test every batch."), {"unless"})
        self.assertEqual(c("Only authorised persons may enter."), {"only"})
        self.assertEqual(c("Statements on the actions subsequently taken."), {"after"})

    def test_ordinary_wording_is_not_a_condition(self):
        for text in ("Areas where products are made should be clean.", "Keep the following documents.",
                     "Storage within the facility should be dry.", "Inspect at intervals following a programme.",
                     "Perform them on special occasions, e.g. in the case of recalls, or when an inspection is due.",
                     "Self-inspection should be carried out once a year."):
            self.assertEqual(layer1.conditions_in(text), set(), text)

    def test_paraphrases_count(self):
        self.assertEqual(layer1.conditions_in("Record actions taken afterwards."), {"after"})
        self.assertEqual(layer1.conditions_in("Test before release.") & layer1.conditions_in("prior to use"), {"before"})

    def test_finding(self):
        req = {"id": "SI-001", "item_text": "Audit the supplier to confirm GMP conformity.", "strength": "mandatory",
               "plant_types": ["OSD"], "parameters": {}, "general": False, "mappings": [
                   {"source": "x", "clause_ref": "1", "clause_sha256": "0", "quote": "Where an audit is required, it "
                    "shall determine GMP conformity.", "strength": "mandatory", "plant_types": ["OSD"],
                    "addendum": "", "relation": "same"}]}
        trees = {"x": {"1": {"text": "Where an audit is required, it shall determine GMP conformity."}}}
        with unittest.mock.patch.object(layer1, "clauses_of", trees.get):
            found = [f for f in layer1.check_requirement(req, {"x": {"applies_to": "ALL"}}) if f[2] == "conditions"]
        self.assertEqual(len(found), 1)
        self.assertIn("condition", found[0][3])
        req["item_text"] = "If an audit is required, it must confirm GMP conformity."
        with unittest.mock.patch.object(layer1, "clauses_of", trees.get):
            self.assertFalse([f for f in layer1.check_requirement(req, {"x": {"applies_to": "ALL"}})
                              if f[2] == "conditions"])

    def check(self, req, trees):
        with unittest.mock.patch.object(layer1, "clauses_of", trees.get):
            return [f for f in layer1.check_requirement(req, {"x": {"applies_to": "ALL"}}) if f[2] == "conditions"]

    def requirement(self, item, quote, addendum="", relation="same"):
        req = {"id": "SI-001", "item_text": item, "strength": "mandatory", "plant_types": ["OSD"], "parameters": {},
               "general": False, "mappings": [
                   {"source": "x", "clause_ref": "1", "clause_sha256": "0", "quote": quote, "strength": "mandatory",
                    "plant_types": ["OSD"], "addendum": addendum, "relation": relation}]}
        return req, {"x": {"1": {"text": quote}}}

    def test_addendum_states_the_condition(self):
        req, trees = self.requirement("Audit the supplier.", "Where an audit is required, it shall be done.",
                                      addendum="Where an audit is required.")
        self.assertFalse(self.check(req, trees))

    def test_looser_narrower_and_bad_quotes_are_skipped(self):
        for relation in ("looser", "narrower"):
            req, trees = self.requirement("Audit the supplier.", "Where an audit is required, it shall be done.",
                                          relation=relation)
            self.assertFalse(self.check(req, trees), relation)
        req, trees = self.requirement("Audit the supplier.", "Where an audit is required, it shall be done.")
        trees["x"]["1"]["text"] = "Something else."
        self.assertFalse(self.check(req, trees))

    def test_conditions_anywhere(self):
        c = layer1.conditions_in
        self.assertEqual(c("Keep records. If a batch fails, investigate."), {"condition"})
        self.assertEqual(c("Clean it. • Where needed, dry it."), {"condition"})
        self.assertEqual(c("Test by batches only when it has been shown to work."), {"condition", "only"})
        self.assertEqual(c("Retest it even if it passed."), set())
        self.assertEqual(c("Test, as risk requires."), {"condition"})

    def test_words_that_are_not_limits(self):
        for text in ("Keep information up to date.", "Review not only the alerts but also raw data.",
                     "Meet both the minimum and peak demand.", "The fan is located after the filters.",
                     "Report no later than the audit.", "Keep it at grade A at rest and when in operation.",
                     "Flush with a fluid other than the product.", "Measure particles of 0.5 µm or greater.",
                     "Allow only the minimum number of people."):
            groups = layer1.conditions_in(text)
            self.assertNotIn("at_most", groups, text)
            self.assertNotIn("at_least", groups, text)
            self.assertNotIn("after", groups, text)
            self.assertNotIn("only", groups, text)
            self.assertNotIn("unless", groups, text)
        self.assertEqual(layer1.conditions_in("Report no later than the audit."), {"deadline"})

    def test_limits_and_their_synonyms(self):
        c = layer1.conditions_in
        self.assertEqual(c("The maximum permissible time should be defined."), {"at_most"})
        self.assertEqual(c("Define the longest permitted time."), {"at_most"})
        self.assertEqual(c("Take a minimum of 3 samples."), {"at_least"})
        self.assertEqual(c("Hold it for 24 hours or longer."), {"at_least"})
        self.assertEqual(c("Report within one (1) month."), {"deadline"})
        self.assertEqual(c("Report within 24 h."), {"deadline"})
        self.assertEqual(c("Report within twenty days."), {"deadline"})
        self.assertEqual(c("Report as soon as possible."), {"deadline"})
        self.assertEqual(c("Within the same batch, mix well."), set())
        self.assertEqual(c("Cleaning should precede use."), {"before"})
        self.assertEqual(c("Hold it pending release."), {"until"})

    def test_examples_do_not_hide_limits(self):
        self.assertEqual(layer1.conditions_in("Process APIs, such as milling, to at least the standards."),
                         {"at_least"})
        self.assertEqual(layer1.conditions_in("Use tools (e.g. scoops) only after cleaning."), {"only", "after"})

    def test_until_is_said_by_before_or_after(self):
        self.assertEqual(layer1.conditions_missing("Do not use it until it is released.", {"before"}), [])
        self.assertEqual(layer1.conditions_missing("Do not use it until it is released.", {"after", "only"}), [])
        self.assertEqual(layer1.conditions_missing("Test it before use.", {"until"}), ["before"])

if __name__ == "__main__":
    unittest.main()
