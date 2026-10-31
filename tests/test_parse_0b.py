"""0b parser fixes: each test pins a defect the source fidelity check (D39, D40) found, on the real PDF where the
defect was, plus the rule on hand-made input where one exists."""
import sys
import tempfile
import unittest
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import headings  # noqa: E402
import run  # noqa: E402
import tables  # noqa: E402


def parse(name, regulator="WHO"):
    clauses, _, _ = run.parser_for({"file": name, "regulator": regulator})(common.OFFICIAL / name)
    return clauses


def text_of(clauses):
    return "\n".join(c.text for c in clauses)


class LostText(unittest.TestCase):
    """Highlight boxes taken for tables, and a cell left out for a missing rule, lost words (0b item 1)."""

    def test_highlight_boxes_are_not_a_table(self):
        name = "fda-cp-7346-832-preapproval-inspections.pdf"
        with pdfplumber.open(str(common.OFFICIAL / name)) as pdf:
            page = pdf.pages[43]
            words = tables._words(common.OFFICIAL / name, 44)
            found = tables.page_tables(page)
            self.assertTrue(found and tables.stray_words(found[0], words))   # pdfplumber's "table" leaves words out
        c = {x.ref: x for x in parse(name, "FDA")}
        self.assertIn("In addition to its inspectional authority, FDA may conduct remote regulatory assessments",
                      c["Attachment A"].text)
        self.assertFalse(any(x.kind == "table_row" and x.page_start == 44 for x in c.values()))

    def test_cp_7356_002_attachment_a(self):
        t = text_of(parse("fda-cp-7356-002-drug-manufacturing-inspections.pdf", "FDA"))
        self.assertIn("its inspectional authority, FDA may conduct", t)
        self.assertIn("An RRA is an examination of an FDA-regulated establishment and/or its records", t)

    def test_nitrosamine_appendix_a_bullet(self):
        t = text_of(parse("fda-guidance-nitrosamine-control-2024.pdf", "FDA"))
        self.assertIn("Preliminary findings from FDA stability testing raised concerns", t)

    def test_cell_without_box_keeps_its_text(self):
        c = parse("india-cdsco-circ-2024-03-risk-based-inspection.pdf", "INDIA")
        row = [x for x in c if x.page_start == 116 and x.text.startswith("27.4 ")]
        self.assertEqual(len(row), 1)
        self.assertIn("The sterilizers are not studied for heat distribution / penetration.", row[0].text)

    def test_grade_letters_stay_with_their_values(self):
        c = {x.ref: x for x in parse("who-trs1044-a2-sterile.pdf")}
        self.assertEqual(c["Table 1 B"].text, "B | 3 520 | 352 000 | Not specified a | 2 930")
        self.assertEqual(c["Table 1 D"].text, "D | 3 520 000 | Not predetermined b | 29 300 | Not predetermined b")


class Glyphs(unittest.TestCase):
    """WHO TRS 981 Annex 2: a font without a Unicode map, which poppler prints as raw glyph numbers."""

    def test_rule(self):
        self.assertEqual(common.unshift_glyphs("t\x01 4FFO\x01FWFSZ\x01"), "• Seen every")
        self.assertEqual(common.unshift_glyphs("'BJMVSF\x01NPEFT\x01FõFDUT\x01"), "Failure modes effects")
        self.assertEqual(common.unshift_glyphs("t\x01Tool"), "• Tool")             # ordinary letters stay
        self.assertEqual(common.unshift_glyphs("\x01     Quality HAZOP"), "\x01     Quality HAZOP")   # a bullet

    def test_qrm_tables_are_readable(self):
        t = text_of(parse("who-trs981-a2-qrm.pdf"))
        for phrase in ("technique to help identify", "facilities and equipment", "No regulatory issue",
                       "effectively prevent hazard"):
            self.assertIn(phrase, t)
        self.assertNotIn("ufdiojrvf", t.lower())


class Turned(unittest.TestCase):
    def test_landscape_pages_are_found(self):
        self.assertEqual(common.turned_pages(common.OFFICIAL / "who-trs1010-a8-hvac-nonsterile.pdf"),
                         {15: 90, 16: 90, 17: 90})
        self.assertEqual(common.turned_pages(common.OFFICIAL / "who-trs1060-a3-excipients.pdf"), {})  # /Rotate set

    def test_upright_copy_reads_forwards(self):
        name = "who-trs1010-a8-hvac-nonsterile.pdf"
        with tempfile.TemporaryDirectory() as d:
            copy = common.upright_copy(common.OFFICIAL / name, d)
            self.assertEqual(copy.name, name)
            self.assertIn("Comparison of filter test standards", common.pdf_pages(copy)[14])
        t = text_of(parse(name))
        self.assertNotIn("elbat", t)
        self.assertIn("Comparison of filter test standards", t)

    def test_turned_margin_title_beside_a_table(self):
        for name, backwards in (("who-trs1052-a4-qc-labs.pdf", "2501 .oN"), ("who-trs1033-a2-hbel-cleaning.pdf",
                                                                             "3301 .oN")):
            t = text_of(parse(name))
            self.assertNotIn(backwards, t)
            self.assertNotIn("WHO Technical Report Series, No. 1052, 2024", t)


class Superscripts(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(tables.mark_exponents("SAL of ≤10-6 and 107 CFU", ["-6", "7"]),
                         ("SAL of ≤10^-6 and 10^7 CFU", []))
        self.assertEqual(tables.mark_exponents("page 1107", ["7"]), ("page 1107", ["7"]))   # not a power of ten

    def test_powers_of_ten(self):
        t = text_of(parse("ema-sterilisation-guideline.pdf", "EMA"))
        self.assertIn("SAL of ≤10^-6", t)
        t = text_of(parse("india-drugs-rules-1945-consolidated-2024-07.pdf", "INDIA"))
        self.assertIn("1 x 10^10", t)
        self.assertIn("10^-5, 10^-6", t)


class RunningLines(unittest.TestCase):
    def test_line_key_spacing_and_roman_numbers(self):
        keys = {common.line_key(x) for x in ("PE 009-18 (Part I) -6- 24 September 2026",
                                              "PE 009-18 (Part I)   - 10 -   24 September 2026",
                                              "PE 009-18 (Part I) - ii - 24 September 2026")}
        self.assertEqual(len(keys), 1)

    def test_pics_footer_not_in_clauses(self):
        for name in ("pics-pe009-18-part1.pdf", "pics-pe009-18-part2.pdf"):
            t = text_of(parse(name, "PICS"))
            self.assertNotIn("(Part I) -1- 24 September", t)
            self.assertNotIn("(Part II) -3- 24 September", t)

    def test_margin_number_of_an_empty_line(self):
        page = "\n".join(["1   One", "2   Two", "3   Three", "4   A heading", "5", "6   Text goes on", "7   Seven",
                          "40", "8   Eight", "9   Nine", "10   Ten", "11   Eleven", "12   Twelve"])
        kept = [x for _, x in headings.body_lines([page])[0]]
        self.assertNotIn("5", kept)                  # the next number of the margin's sequence on its own: dropped
        self.assertIn("40", kept)                    # any other number on its own line is text
        c = {x.ref: x for x in parse("fda-guidance-analytical-procedures-validation-2015.pdf", "FDA")}
        self.assertTrue(c["II"].text.startswith("II. BACKGROUND Each NDA and ANDA must include"))

    def test_header_band_does_not_continue_the_last_row(self):
        c = parse("india-cdsco-circ-2024-03-risk-based-inspection.pdf", "INDIA")
        self.assertFalse([x.ref for x in c if x.kind == "table_row" and x.text.endswith("Quality Rating")])
        self.assertFalse([x.ref for x in c if x.kind == "table_row" and "NA Quality Rating" in x.text])


if __name__ == "__main__":
    unittest.main()
