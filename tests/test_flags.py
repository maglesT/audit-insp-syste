import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import ecfr  # noqa: E402
import numbered  # noqa: E402
import run  # noqa: E402


def clause(ref, text, page, kind="clause"):
    return common.Clause(source="x.pdf", ref=ref, section="", number=ref, heading=text[:160], text=text,
                         page_start=page, page_end=page, kind=kind)


class Duplicates(unittest.TestCase):
    def test_contents_page_copies_become_toc(self):
        cl = [clause("1", "1 Introduction", 2), clause("1.1", "1.1 Objective", 2), clause("1.2", "1.2 Scope", 2),
              clause("2", "2 Quality Management", 2), clause("_unnumbered:1", "Body", 3, "unnumbered"),
              clause("1", "1 Introduction " + "x" * 400, 5), clause("1.1", "1.1 Objective " + "y" * 300, 5),
              clause("1.2", "1.2 Scope " + "z" * 300, 5), clause("2", "2 Quality Management", 6)]
        out = common.resolve_duplicates(cl)
        self.assertEqual([c.kind for c in out[:4]], ["toc"] * 4)
        self.assertEqual([c.ref for c in out[5:]], ["1", "1.1", "1.2", "2"])

    def test_real_restart_gets_suffix_and_note(self):
        cl = [clause("1", "1. Scope " + "a" * 300, 4), clause("_unnumbered:1", "Appendix A Model form", 9,
                                                               "unnumbered"), clause("1", "1. Name " + "b" * 300, 9)]
        out = common.resolve_duplicates(cl)
        self.assertEqual(out[2].ref, "1 #2")
        self.assertIn("Appendix A Model form", out[2].notes[0])

    def test_stray_number_is_taken_back(self):
        """ICH Q1A: a stray "3" (a list or footnote number) no longer swallows 2.1.9 to 2.2.x."""
        r = {c.ref for c in numbered.parse(common.OFFICIAL / "ich-q1a-r2.pdf")[0] if c.kind == "clause"}
        self.assertTrue({"2.1.9", "2.2", "2.2.1"} <= r)

    def test_stray_list_run_is_taken_back(self):
        """EU GMP Part II: list items "10." to "15." no longer swallow sections 2.5 to 9.46."""
        r = {c.ref for c in numbered.parse(common.OFFICIAL / "eu-2014-08_gmp_part1.pdf")[0] if c.kind == "clause"}
        self.assertTrue({"2.50", "5.40", "9.46"} <= r)

    def test_contents_line_does_not_open_an_appendix(self):
        r = {c.ref for c in numbered.parse(common.OFFICIAL / "who-trs1033-a4-data-integrity.pdf")[0]}
        self.assertIn("1.1", r)
        self.assertNotIn("Appendix 1 1.1", r)

    def test_title_case_chapter_after_subsections(self):
        r = {c.ref for c in numbered.parse(common.OFFICIAL / "eu-annex11_01-2011_en.pdf")[0] if c.kind == "clause"}
        self.assertTrue({"5", "6", "9", "10"} <= r)

    def test_one_principle_per_chapter_and_one_glossary(self):
        r = {c.ref for c in numbered.parse(common.OFFICIAL / "pics-pe009-18-part1.pdf")[0] if c.kind in common.CITABLE}
        self.assertTrue({"Part I 1 Principle", "Part I 9 Principle"} <= r)
        r = [c.ref for c in numbered.parse(common.OFFICIAL / "pics-pe009-18-part2.pdf")[0] if c.kind in common.CITABLE]
        self.assertEqual([x for x in r if "Glossary" in x], ["Part II Glossary"])

    def test_cover_date_is_not_clause_one(self):
        r = {c.ref: c for c in numbered.parse(common.OFFICIAL / "pics-pi043-1-am-cross-contamination.pdf")[0]}
        self.assertTrue(r["1"].text.startswith("1. DOCUMENT HISTORY"))


class Sections(unittest.TestCase):
    def test_glossary_and_appendix_text_are_citable(self):
        clauses, _, _ = numbered.parse(common.OFFICIAL / "who-trs1033-a4-data-integrity.pdf")
        r = {c.ref: c for c in clauses if c.kind in common.CITABLE}
        self.assertIn("Appendix 1", r)
        self.assertIn("Examples in data integrity management", r["Appendix 1"].text)
        self.assertTrue(any(ref.endswith("Glossary") for ref in r))
        self.assertFalse(any(c.text.startswith("References") and c.kind == "section" for c in clauses))


class Cfr(unittest.TestCase):
    def test_lettered_items_below_roman(self):
        clauses, _, _ = ecfr.parse(common.OFFICIAL / "fda-cfr-21-314.81.xml")
        r = {c.ref for c in clauses}
        for ref in ("314.81(b)(2)(ii)(a)", "314.81(b)(2)(vii)(a)(8)(i)", "314.81(b)(3)(iii)(c)(5)"):
            self.assertIn(ref, r)
        self.assertEqual(common.report("x", clauses, 1)["duplicate_refs"], [])

    def test_unmarked_definitions(self):
        r = {c.ref: c for c in ecfr.parse(common.OFFICIAL / "fda-cfr-21-part-207.xml")[0]}
        self.assertIn('207.1 "Content of labeling"(2)', r)
        self.assertIn('207.1 "Foreign"(2)', r)

    def test_italic_markup_decides_deep_levels(self):
        """201.327: a plain "(3)" after italic items is not italic; every eCFR part parses without restarts."""
        for name in ("fda-cfr-21-part-201.xml", "fda-cfr-21-part-207.xml", "fda-cfr-21-314.81.xml"):
            clauses, _, _ = ecfr.parse(common.OFFICIAL / name)
            self.assertFalse([c.ref for c in clauses if "#" in c.ref], name)

    def test_part_211_unchanged(self):
        clauses, _, _ = ecfr.parse(common.OFFICIAL / "ecfr-21cfr211-2026-10-27.xml")
        self.assertFalse(any("#" in c.ref or '"' in c.ref for c in clauses))


class Flags(unittest.TestCase):
    def rep(self, **kw):
        base = {"duplicate_refs": [], "large": [], "obligations": 100, "obligations_outside_numbered": 5,
                "missed_obligations": [], "assigned_share": 1.0}
        base.update(kw)
        return base

    def test_long_front_matter_is_not_a_flag(self):
        self.assertEqual(run.flags(self.rep()), [])
        self.assertEqual(run.flags(self.rep(obligations_outside_numbered=11)), ["obligations outside citable clauses"])


if __name__ == "__main__":
    unittest.main()
