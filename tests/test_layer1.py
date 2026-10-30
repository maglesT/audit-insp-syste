import copy
import json
import shutil
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
