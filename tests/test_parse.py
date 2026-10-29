import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import ecfr  # noqa: E402
import numbered  # noqa: E402


def refs(parse, name):
    clauses, _ = parse(common.OFFICIAL / name)
    return {c.ref: c for c in clauses if c.kind in ("clause", "principle")}


class Successor(unittest.TestCase):
    def test_siblings_children_and_higher_levels(self):
        self.assertTrue(numbered.plausible([4, 9], [4, 10])[0])
        self.assertTrue(numbered.plausible([4, 9], [5])[0])
        self.assertTrue(numbered.plausible([4, 9], [4, 9, 1])[0])
        self.assertTrue(numbered.plausible([2, 1], [2, 10])[0])      # ICH Q7 decimals
        self.assertTrue(numbered.plausible([2, 15], [2, 2])[0])
        self.assertTrue(numbered.plausible([2, 15], [2, 20])[0])

    def test_numbers_inside_text_are_rejected(self):
        self.assertFalse(numbered.plausible([4, 9], [2, 5])[0])      # "2.5 mg"
        self.assertFalse(numbered.plausible([4, 9], [1])[0])
        self.assertTrue(numbered.plausible([4, 9], [4, 12])[1])      # skipping two numbers is accepted but flagged
        self.assertFalse(numbered.plausible([4, 9], [4, 13])[0])     # a bigger jump is rejected


class KnownClauses(unittest.TestCase):
    """Clauses the plan cites must be found with the right wording (checked by hand against the PDFs)."""

    def test_eu_chapter_9(self):
        r = refs(numbered.parse, "eu-cap9_en.pdf")
        self.assertIn("All self inspections should be recorded", r["Chapter 9 9.3"].text)

    def test_eu_chapter_4(self):
        r = refs(numbered.parse, "eu-chapter4_01-2011_en.pdf")
        self.assertIn("should be signed and dated", r["4.9"].text)

    def test_who_main_self_inspection_report(self):
        r = refs(numbered.parse, "who-trs986-a2-gmp-main.pdf")
        self.assertIn("A report should be made at the completion of a self-inspection", r["8.5"].text)

    def test_schedule_m_frequency(self):
        r = refs(numbered.parse, "india-schedule-m-2023-GSR922E.pdf")
        self.assertIn("at least once in a year", r["Part I 10.4"].text)

    def test_ich_q7_internal_audits(self):
        r = refs(numbered.parse, "ich-q7.pdf")
        self.assertIn("regular internal audits should be performed", r["2.40"].text)

    def test_cfr_nesting(self):
        r = refs(ecfr.parse, "ecfr-21cfr211-2026-10-27.xml")
        self.assertIn("211.42(c)(10)(vi)", r)
        self.assertIn("shall be routinely calibrated", r["211.68(a)"].text)


if __name__ == "__main__":
    unittest.main()
