import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import crosscheck  # noqa: E402
import fdahtml  # noqa: E402
import headings  # noqa: E402


def refs(parse, name):
    clauses, _, _ = parse(common.OFFICIAL / name)
    return {c.ref: c for c in clauses if c.kind in common.CITABLE}


class Outline(unittest.TestCase):
    def test_roman_letters_digits(self):
        o = headings.Outline()
        for mark, ref in (("I.", "I"), ("II.", "II"), ("A.", "II.A"), ("1.", "II.A.1"), ("2.", "II.A.2"),
                          ("B.", "II.B"), ("III.", "III"), ("A.", "III.A")):
            self.assertTrue(o.accept(mark), mark)
            self.assertEqual(o.ref(), ref)

    def test_letter_i_after_h_and_parts(self):
        o = headings.Outline()
        for mark in ("I.", "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I."):
            self.assertTrue(o.accept(mark))
        self.assertEqual(o.ref(), "I.I")                       # the letter I, not Roman II
        o = headings.Outline()
        for mark in ("PART II", "1.", "2.", "A."):
            o.accept(mark)
        self.assertEqual(o.ref(), "Part II 2.A")

    def test_body_list_is_not_a_jump(self):
        o = headings.Outline()
        for mark in ("I.", "II.", "A."):
            o.accept(mark)
        self.assertFalse(o.accept("7."))                      # "7. Fully document ..." in a body list


class Guidances(unittest.TestCase):
    """Sections the plan cites, found with the right wording (checked by hand against the PDFs)."""

    def test_oos_phase_ii(self):
        r = refs(headings.parse, "fda-oos-2022.pdf")
        self.assertIn("IV.A", r)
        self.assertIn("Review of Production", r["IV.A"].heading)
        self.assertNotIn("_toc", " ".join(r))

    def test_process_validation_stage_2(self):
        r = refs(headings.parse, "fda-process-validation-2011.pdf")
        self.assertIn("IV.C.2", r)
        self.assertIn("Process Performance Qualification", r["IV.C.2"].heading)

    def test_margin_line_numbers_are_removed(self):
        r = refs(headings.parse, "fda-guidance-part11-scope-application-2003.pdf")
        self.assertIn("III.B.2", r)
        self.assertTrue(r["I"].heading.startswith("I."))

    def test_compliance_program_parts(self):
        r = refs(headings.parse, "fda-cp-7356-002-drug-manufacturing-inspections.pdf")
        self.assertIn("Part III 3.A", r)
        self.assertIn("Quality System", r["Part III 3.A"].heading)

    def test_contents_entries_all_found(self):
        for name in ("fda-aseptic-2004.pdf", "fda-guidance-container-closure-systems-1999.pdf"):
            clauses, _, _ = headings.parse(common.OFFICIAL / name)
            self.assertEqual([n for c in clauses for n in c.notes if n.startswith("gap")], [], name)
            self.assertEqual(crosscheck.missed_obligations(common.OFFICIAL / name, clauses), [], name)


    def test_wrapped_last_contents_entry(self):
        r = refs(headings.parse, "fda-guidance-voluntary-recalls-initiation-2022.pdf")
        self.assertIn("III.D", r)

    def test_heading_with_plural_or_shorter_title(self):
        r = refs(headings.parse, "fda-cp-7356-002a-sterile-drug-process.pdf")
        self.assertIn("Part II 2.1", r)                           # contents "Objective", body "OBJECTIVES"

    def test_body_list_items_are_not_headings_without_contents(self):
        self.assertFalse(headings.heading_like("For CGMP coverage that may result in an OAI status, enter a"))
        self.assertTrue(headings.heading_like("Program Management Instructions"))
        self.assertTrue(headings.heading_like("BACKGROUND"))


    def test_appendices_end_the_last_section(self):
        r = refs(headings.parse, "fda-aseptic-2004.pdf")
        self.assertIn("Appendix 1", r)
        self.assertLess(len(r["XII"].text), 15000)
        self.assertNotIn("GLOSSARY", r["Appendix 3"].text)

    def test_attachment_listing_is_not_the_attachment(self):
        r = refs(headings.parse, "fda-cp-7356-002-drug-manufacturing-inspections.pdf")
        self.assertGreater(len(r["Attachment A"].text), 1000)
        self.assertNotIn("Attachment A #2", r)


    def test_level_below_the_contents_list(self):
        r = refs(headings.parse, "fda-guidance-container-closure-systems-1999.pdf")
        self.assertTrue({"III.B.1", "III.B.4"} <= set(r))
        r = refs(headings.parse, "fda-aseptic-2004.pdf")
        self.assertIn("Appendix 1 A", r)
        self.assertNotIn("XII.A", r)


class Pages(unittest.TestCase):
    def test_qa_page_questions_in_order(self):
        clauses, _, _ = fdahtml.parse(common.OFFICIAL / "fda-cgmp-qa-laboratory-controls.html")
        qs = [c.ref for c in clauses if c.ref.startswith("Q")]
        self.assertEqual(qs, [f"Q{n}" for n in range(1, 18)])
        q7 = next(c for c in clauses if c.ref == "Q7")
        self.assertTrue(q7.text.startswith("7. Is it ever appropriate to use an unvalidated method"))

    def test_qa_index_is_not_a_clause(self):
        clauses, _, _ = fdahtml.parse(common.OFFICIAL / "fda-cgmp-qa-equipment.html")
        self.assertEqual(sum(c.kind == "toc" for c in clauses), sum(c.ref.startswith("Q") for c in clauses))

    def test_qa_index_never_duplicates_a_question(self):
        clauses, _, _ = fdahtml.parse(common.OFFICIAL / "fda-cgmp-qa-production-process-controls.html")
        self.assertEqual([c.ref for c in clauses if c.ref.startswith("¶")], [])
        self.assertEqual(len([c for c in clauses if c.ref.startswith("Q")]), 24)

    def test_list_marker_survives_nested_paragraph(self):
        parser = fdahtml.Blocks()
        parser.feed('<article><ol type="A"><li>First</li><li><p>Second item text</p></li></ol>'
                    "<p>[Previous Chapter] [Table of Contents]</p></article>")
        self.assertEqual([(b["marker"], b["text"]) for b in parser.blocks[:2]],
                         [("A", "First"), ("B", "Second item text")])
        self.assertTrue(fdahtml.NAV.match(parser.blocks[2]["text"]))

    def test_inspection_guide_paragraphs(self):
        clauses, _, _ = fdahtml.parse(common.OFFICIAL / "fda-ora-guide-cleaning-validation-1993.html")
        text = " ".join(c.text for c in clauses)
        self.assertIn("FDA expects firms to have written procedures (SOP's) detailing the cleaning processes", text)
        self.assertNotIn("Content current as of", text)
        self.assertTrue(all(c.ref.startswith(("¶", "_")) for c in clauses))


if __name__ == "__main__":
    unittest.main()
