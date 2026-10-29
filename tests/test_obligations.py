import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import crosscheck  # noqa: E402
import numbered  # noqa: E402
import obligations  # noqa: E402


class Sentences(unittest.TestCase):
    def test_abbreviations_do_not_split(self):
        s = obligations.sentences("Records, e.g. batch records, should be kept. They must be legible.")
        self.assertEqual(len(s), 2)

    def test_strength_classes(self):
        self.assertEqual(obligations.strength("The area shall be cleaned."), "mandatory")
        self.assertEqual(obligations.strength("Reports should be recorded."), "recommended")
        self.assertEqual(obligations.strength("External audits may be useful."), "permissive")
        self.assertIsNone(obligations.strength("This annex applies to sterile products."))

    def test_numbers_with_units(self):
        self.assertEqual(obligations.numbers("at least once in 12 months at 25 °C or 0.5 µm"),
                         ["12 months", "25 °C", "0.5 µm"])


class SafetyNet(unittest.TestCase):
    def test_every_obligation_of_eu_chapter_9_is_found(self):
        clauses, _, _ = numbered.parse(common.OFFICIAL / "eu-cap9_en.pdf")
        found = obligations.extract(clauses)
        self.assertEqual(len([o for o in found if o["strength"] == "recommended"]), 6)
        self.assertEqual(crosscheck.missed_obligations(common.OFFICIAL / "eu-cap9_en.pdf", clauses), [])

    def test_crosscheck_detects_dropped_text(self):
        clauses, _, _ = numbered.parse(common.OFFICIAL / "eu-cap9_en.pdf")
        clauses = [c for c in clauses if c.ref != "Chapter 9 9.3"]          # simulate a parser losing a clause
        missed = crosscheck.missed_obligations(common.OFFICIAL / "eu-cap9_en.pdf", clauses)
        self.assertTrue(any("self inspections should be recorded" in m.lower() for m in missed))


if __name__ == "__main__":
    unittest.main()
