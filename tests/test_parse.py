import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import ecfr  # noqa: E402
import numbered  # noqa: E402


def refs(parse, name):
    clauses, _, _ = parse(common.OFFICIAL / name)
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

    def test_cfr_inline_paragraph_after_heading(self):
        r = refs(ecfr.parse, "ecfr-21cfr211-2026-10-27.xml")
        for ref in ("211.132(c)", "211.132(c)(1)", "211.132(c)(1)(i)", "211.132(c)(2)", "211.132(b)(1)"):
            self.assertIn(ref, r)
        self.assertNotIn("211.132(i)", r)

    def test_cfr_letter_i_after_h_is_a_letter(self):
        self.assertEqual(ecfr.level("i", [(0, "h"), (1, "3")]), 0)
        self.assertEqual(ecfr.level("i", [(0, "c"), (1, "1")]), 2)
        self.assertEqual(ecfr.level("ii", [(0, "h"), (1, "3"), (2, "i")]), 2)

    def test_leading_zero_is_not_a_clause_number(self):
        self.assertIsNone(numbered.NUM.match("01 March 2009 Date for coming into operation"))
        self.assertFalse(numbered.plausible([11], [2])[0])         # decimal rule is for multi-part numbers only

    def test_annex1_scope_and_no_contents_duplicates(self):
        clauses, _, _ = numbered.parse(common.OFFICIAL / "eu-20220825_gmp-an1_en_0.pdf")
        r = [c.ref for c in clauses if c.kind == "clause"]
        self.assertEqual(len(r), len(set(r)))
        self.assertIn("Annex 1 1", r)

    def test_repeated_body_lines_are_kept(self):
        clauses, _, _ = numbered.parse(common.OFFICIAL / "pics-pi041-1-data-integrity.pdf")
        self.assertIn("Expectation", " ".join(c.text for c in clauses))

    def test_who_side_header_is_not_clause_text(self):
        r = refs(numbered.parse, "who-trs1044-a2-sterile.pdf")
        self.assertIn("may be necessary, depending on the validated campaign length", r["4.21"].text)
        self.assertNotIn("Technical Report Series", r["4.21"].text)

    def test_cfr_nesting(self):
        r = refs(ecfr.parse, "ecfr-21cfr211-2026-10-27.xml")
        self.assertIn("211.42(c)(10)(vi)", r)
        self.assertIn("shall be routinely calibrated", r["211.68(a)"].text)


if __name__ == "__main__":
    unittest.main()
