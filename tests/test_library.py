import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import build  # noqa: E402
import model  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "library"


class Library(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        shutil.copytree(FIXTURE, self.dir, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def edit(self, change):
        path = self.dir / "requirements" / "SI.json"
        data = json.loads(path.read_text())
        change(data["requirements"])
        path.write_text(json.dumps(data))

    def test_fixture_is_valid_and_builds(self):
        self.assertEqual(model.validate(self.dir), [])
        db = sqlite3.connect(build.build(self.dir))
        self.addCleanup(db.close)
        self.assertEqual(db.execute("SELECT count(*) FROM mapping").fetchone()[0], 3)
        self.assertEqual(db.execute("SELECT na_reason IS NOT NULL FROM coverage WHERE clause_ref LIKE '%Principle'")
                         .fetchone()[0], 1)

    def test_bad_values_are_reported(self):
        def break_it(reqs):
            reqs[0]["strength"] = "must"
            reqs[0]["plant_types"] = ["TABLETS"]
            reqs[1]["id"] = "SI-001"
            reqs[1]["mappings"][0]["source"] = "unknown.pdf"
            reqs[1]["mappings"][0]["extra"] = 1
            reqs[2]["mappings"].append(dict(reqs[2]["mappings"][0]))  # one item, one source clause (D37)
        self.edit(break_it)
        errors = "\n".join(model.validate(self.dir))
        for text in ("strength must be", "plant_types", "duplicate id", "exactly one mapping", "unknown source",
                     "unknown field 'extra'"):
            self.assertIn(text, errors)
        with self.assertRaises(ValueError):
            build.build(self.dir)

    def test_coverage_entries(self):
        path = self.dir / "coverage" / "eu-cap9_en.json"
        path.write_text(json.dumps({"clauses": {"9.1": {"requirements": ["SI-999"]}, "9.2": {"na": ""},
                                                "9.4": {"other": 1}}}))
        errors = "\n".join(model.validate(self.dir))
        self.assertIn("unknown requirement SI-999", errors)
        self.assertIn("needs a reason", errors)
        self.assertIn("entry must be", errors)

    def test_real_library_is_valid(self):
        self.assertEqual(model.validate(), [])


if __name__ == "__main__":
    unittest.main()
