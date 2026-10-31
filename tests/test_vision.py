"""Page-based drafting checks (tools/pages/vision.py, D45), on a real page: EU Annex 1 page 13."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "pages"))
import vision  # noqa: E402

SRC, PAGE = "eu-20220825_gmp-an1_en_0.pdf", 13
QUOTE = ("For cleanroom classification, the total of particles equal to or greater than 0.5 and 5 µm should be "
         "measured.")


def item(**kw):
    base = {"statement": "Measure particles of 0.5 and 5 µm and larger for cleanroom classification.", "quote": QUOTE,
            "clause_number": "4.27", "strength": "recommended", "plant_types": ["INJ"], "numbers": ["0.5", "5"],
            "condition": "", "topic": "PREM.CLEAN", "runs_over": False, "text_layer_differs": ""}
    return {**base, **kw}


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import quotes  # noqa: E402


class Matching(unittest.TestCase):
    """Whole tokens in order: the review's false passes must fail; real reading differences must pass."""

    def c(self, quote, text, loose=False):
        return quotes.contains(quotes.toks(quote), quotes.toks(text), loose)

    def test_wrong_text_fails(self):
        for quote, text in [("limit 15 ppm", "limit 1.5 ppm"), ("≤ 0.5 µm", "≥ 0.5 µm"), ("10^6", "10^-6"),
                            ("limit of 2", "limit of 20 ppm"), ("5 µm particles", "25 µm particles"),
                            ("appropriate", "inappropriate"), ("0.5", "05")]:
            self.assertFalse(self.c(quote, text), quote)
        for quote, text in [("Class III", "Class I"), ("(iv)", "(v)"), ("should be filled", "should be led")]:
            self.assertFalse(self.c(quote, text, loose=True), quote)

    def test_reading_differences_pass(self):
        self.assertTrue(self.c("specified limits", "speci- fied limits"))
        self.assertTrue(self.c("cross-contamination", "crosscontamination"))
        self.assertTrue(self.c("qualification of rooms", "qualication of rooms", loose=True))
        self.assertFalse(self.c("qualification of rooms", "qualication of rooms"))   # pdftotext keeps ligatures


class Checks(unittest.TestCase):
    def test_a_right_item_passes_in_both_readings(self):
        found, in_layer, in_miner = vision.check_item(item(), SRC, PAGE)
        self.assertEqual(found, [])
        self.assertTrue(in_layer and in_miner)

    def test_a_changed_number_in_the_quote_fails_both_readings(self):
        found, in_layer, in_miner = vision.check_item(item(quote=QUOTE.replace("0.5", "0.3")), SRC, PAGE)
        self.assertFalse(in_layer or in_miner)
        self.assertEqual(found[0][0], "quote")

    def test_table_row_cells_must_be_one_row(self):
        right = vision.check_item(item(quote="C | 352 000 | 3 520 000 | 2 930 | 29 300", statement="Grade C limits: "
                                       "352 000 and 3 520 000; 2 930 and 29 300.", clause_number=""), SRC, PAGE)
        self.assertTrue(right[1] and right[2], right)
        for wrong in ("B | 352 000 | 3 520 000 | 2 930 | 29 300", "A | 3 520 | 3 520 | 20 | 29",
                      "Grade A | 352 000 | 3 520"):
            found, in_layer, in_miner = vision.check_item(item(quote=wrong, clause_number=""), SRC, PAGE)
            self.assertFalse(in_layer or in_miner, wrong)

    def test_body_keeps_list_lines(self):
        text = vision.body(vision.layer_text, "india-schedule-m-2023-GSR922E.pdf", 271)
        self.assertIn("Sterilisation area", text)

    def test_clause_number_must_be_on_the_page(self):
        self.assertEqual(vision.check_item(item(clause_number="4.31"), SRC, PAGE)[0][0][0], "clause")
        self.assertTrue(vision.check_item(item(clause_number="4.27 iii"), SRC, PAGE)[0])   # no "iii" in 4.27
        self.assertEqual(vision.check_item(item(clause_number="9.18"), SRC, PAGE)[0][0][0], "clause")

    def test_number_strength_and_condition(self):
        checks = {c for c, _ in vision.check_item(item(statement="Measure 0.3 µm particles.", strength="mandatory"),
                                                  SRC, PAGE)[0]}
        self.assertEqual(checks, {"numbers", "strength"})
        dropped = vision.check_item(item(statement="Measure particles for cleanroom classification."), SRC, PAGE)[0]
        self.assertIn("numbers", {c for c, _ in dropped})                    # the quote's 0.5 and 5 are gone

    def test_coverage(self):
        gaps = vision.coverage(SRC, PAGE, [item()], [], [])
        self.assertFalse(any("total of particles equal to or greater" in g for g in gaps))
        self.assertTrue(any("Classification activities should be scheduled" in g for g in gaps))
        na = [{"text": "Classification activities should be scheduled and performed", "reason": "example"}]
        self.assertFalse(any("Classification activities should be scheduled" in g
                             for g in vision.coverage(SRC, PAGE, [item()], [], na)))


if __name__ == "__main__":
    unittest.main()


class QuoteResult(unittest.TestCase):
    """tools/library/quotes.py: an entry counts only while the quote, the source and the code are unchanged."""

    def test_stale_and_missing_entries(self):
        import json
        import tempfile
        req = {"id": "X-1", "status": "draft", "mappings": [{"source": SRC, "clause_ref": "4.27", "quote": QUOTE}]}
        entry = {"source": SRC, "quote_sha256": quotes.sha256(QUOTE), "source_sha256": "s", "reader": "pdfminer",
                 "found": True}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.json"
            path.write_text(json.dumps({"code_sha256": quotes.code_sha256(), "mappings": {"X-1#1": entry}}))
            self.assertEqual(quotes.findings([req], path, {SRC: "s"}), [])
            changed = {**req, "mappings": [{"source": SRC, "clause_ref": "4.27", "quote": QUOTE + " x"}]}
            self.assertEqual(quotes.findings([changed], path, {SRC: "s"})[0][2], "quote2")
            self.assertEqual(quotes.findings([req], path, {SRC: "other"})[0][2], "quote2")
            path.write_text(json.dumps({"code_sha256": "old", "mappings": {"X-1#1": entry}}))
            self.assertEqual(quotes.findings([req], path, {SRC: "s"})[0][2], "quote2")
            path.write_text(json.dumps({"code_sha256": quotes.code_sha256(),
                                        "mappings": {"X-1#1": {**entry, "found": False}}}))
            self.assertIn("not found", quotes.findings([req], path, {SRC: "s"})[0][3])


class ReviewRound2(unittest.TestCase):
    def test_minus_before_a_number(self):
        self.assertFalse(quotes.contains(quotes.toks("store at 20 °C"), quotes.toks("store at -20 °C")))
        self.assertFalse(quotes.contains(quotes.toks("store at 20 °C"), quotes.toks("store at –20 °C")))
        self.assertTrue(quotes.contains(quotes.toks("cross-contamination"), quotes.toks("cross-contamination")))

    def test_row_needs_its_label(self):
        for wrong in ("352 000 | 3 520 000 | 2 930 | 29 300", "3 520 | 3 520"):
            found, in_layer, in_miner = vision.check_item(item(quote=wrong, clause_number=""), SRC, PAGE)
            self.assertFalse(in_layer or in_miner, wrong)

    def test_body_keeps_a_list_end(self):
        self.assertIn("6 months", vision.body(vision.layer_text, "who-trs1044-a2-sterile.pdf", 19))

    def test_clause_sub_part_and_page_numbers(self):
        self.assertTrue(vision.clause_findings("4.22 iii", SRC, PAGE))     # 4.22 is printed on page 12
        self.assertTrue(vision.clause_findings("12", SRC, PAGE))           # a page number is not a clause
        self.assertEqual(vision.clause_findings("4.29", SRC, PAGE), [])


class D46(unittest.TestCase):
    """Owner decisions of 31 Oct (D46): header-carrying table quotes, footnote marks, lead-in conditions,
    inspection-checklist strength."""

    def test_footnote_mark_after_a_word(self):
        self.assertEqual(quotes.toks("Cumene^1 | 0.7"), ["cumene", "1", "0.7"])
        self.assertEqual(quotes.toks("10^-6"), ["10", "^", "−", "6"])               # a power of ten stays

    def test_table_quote_with_its_headers(self):
        top = "Grade | Maximum limits for total particle ≥ 0.5 µm/m3 | Maximum limits for total particle ≥ 5 µm/m3"
        head = top + " | at rest | in operation | at rest^a | in operation^a"            # both header rows
        q = head + " || C | 352 000 | 3 520 000 | 2 930 | 29 300"
        self.assertEqual(vision.table_quote_found(q, SRC, PAGE), (True, True))
        # the sub-header (at rest / in operation) dropped, or the row cut short: not the table's header and row
        self.assertEqual(vision.table_quote_found(top + " || C | 352 000 | 3 520 000 | 2 930 | 29 300", SRC, PAGE),
                         (False, False))
        self.assertEqual(vision.table_quote_found(head + " || C | 352 000", SRC, PAGE), (False, False))
        swapped = head + " || B | 352 000 | 3 520 000 | 2 930 | 29 300"
        self.assertEqual(vision.table_quote_found(swapped, SRC, PAGE), (False, False))

    def test_lead_in_condition_of_a_table(self):
        row = item(quote="Benzene | 2 | Carcinogen", statement="Limit benzene to 2 ppm.", clause_number="",
                   strength="recommended", topic="MAT.SPEC")
        checks = {c for c, _ in vision.check_item(row, "ich-q3c-r9.pdf", 11)[0]}
        self.assertIn("lead-in", checks)
        kept = dict(row, statement="Unless otherwise justified, and only if its use is unavoidable in order to "
                                   "produce a drug product with a significant therapeutic advance, limit benzene to "
                                   "2 ppm.")
        vague = dict(row, statement="When used, limit benzene to 2 ppm unless justified.")
        self.assertIn("lead-in", {c for c, _ in vision.check_item(vague, "ich-q3c-r9.pdf", 11)[0]})
        self.assertNotIn("lead-in", {c for c, _ in vision.check_item(kept, "ich-q3c-r9.pdf", 11)[0]})

    def test_checklist_row_is_mandatory(self):
        src = "india-cdsco-circ-2024-03-risk-based-inspection.pdf"
        import layer1
        self.assertIn(src, layer1.INSPECTION_CHECKLISTS)
        row = item(quote="Specify the number of air changes in Grade A/B and Grade C areas.",
                   statement="Specify the number of air changes in grade A/B and C areas.", clause_number="",
                   strength="recommended", plant_types=["INJ"])
        self.assertIn("strength", {c for c, _ in vision.check_item(row, src, 45)[0]})


class D46Review(unittest.TestCase):
    def test_drop_running_keeps_body_lines_with_other_numbers(self):
        pages = [["Header line of the guide", "x"], ["Keep records for at least 5 years.", "body", "y",
                 "Page 6 of 9"], ["Keep records for at least 1 years.", "z", "Page 7 of 9"]]
        kept = quotes.drop_running(pages)
        self.assertIn("Keep records for at least 5 years.", kept[1])
        self.assertNotIn("Page 6 of 9", kept[1])

    def test_caption_is_not_a_reference(self):
        self.assertIsNone(vision.CAPTION.match("Table 6 should apply."))
        self.assertTrue(vision.CAPTION.match("Table 2: Maximum permitted"))
        self.assertTrue(vision.CAPTION.match("TABLE 2. Class 2 solvents"))

    def test_footnote_mark_is_not_a_quote_number(self):
        row = item(quote="Cumene^1 | 0.7 | 70", statement="Limit cumene to 0.7 mg/day (70 ppm).", clause_number="",
                   topic="MAT.SPEC")
        self.assertFalse([m for c, m in vision.check_item(row, "ich-q3c-r9.pdf", 12)[0] if c == "numbers"])

    def test_checklist_rule_only_without_a_lead_in(self):
        import layer1
        self.assertEqual(layer1.lead_in_strength("visit the site", "Following criteria should be applied: visit the "
                                                 "site"), "recommended")


class D46Review2(unittest.TestCase):
    def test_unruled_header_must_be_whole(self):
        q3c = "ich-q3c-r9.pdf"
        self.assertEqual(vision.table_quote_found("Solvent | Concentration limit | Concern || Benzene | 2 | Carcinogen",
                                                  q3c, 11)[0], False)
        self.assertEqual(vision.table_quote_found("Solvent | Concentration limit (ppm) | Concern || Benzene | 2 | "
                                                  "Carcinogen", q3c, 11)[0], True)

    def test_unruled_header_columns_in_order(self):
        self.assertEqual(vision.table_quote_found("Solvent | Concern | Concentration limit (ppm) || Benzene | 2 | "
                                                  "Carcinogen", "ich-q3c-r9.pdf", 11)[0], False)

    def test_marks_out_keeps_grade_letters(self):
        self.assertNotEqual(vision._marks_out("Grade A B C D"), vision._marks_out("Grade D C B A"))
        self.assertEqual(vision._marks_out("at rest (a)"), vision._marks_out("at rest^a"))

    def test_lead_in_needs_the_whole_condition(self):
        lead = ("However, if their use is unavoidable in order to produce a drug product with a significant "
                "therapeutic advance, then their levels should be restricted as shown in Table 1, unless otherwise "
                "justified.")
        part = "Only if use is unavoidable in order to produce a drug product, limit benzene to 2 ppm, unless otherwise justified."
        self.assertTrue(vision.lead_in_missing(lead, part))


class PreScaling(unittest.TestCase):
    def test_descriptive_may_and_captions_do_not_count(self):
        self.assertFalse(vision.counts_for_coverage("Depending on the purpose, inspection coverage may include "
                                                    "different numbers of systems."))
        self.assertFalse(vision.counts_for_coverage("Secondary amines may be present as impurities."))
        self.assertFalse(vision.counts_for_coverage("Table 1: Maximum permitted total particle concentration should "
                                                    "not exceed the limits."))
        self.assertTrue(vision.counts_for_coverage("Quality reviews may be grouped by product type where "
                                                   "scientifically justified."))
        self.assertTrue(vision.counts_for_coverage("The disinfection process should be validated."))

    def test_continued_table_header_from_its_page(self):
        q = "Solvent | PDE (mg/day) | Concentration limit (ppm) || Nitromethane | 0.5 | 50"
        self.assertEqual(vision.table_quote_found(q, "ich-q3c-r9.pdf", 13, header_page=12), (True, True))
        self.assertEqual(vision.table_quote_found(q, "ich-q3c-r9.pdf", 13), (False, False))     # not on p13
        wrong = "Solvent | Concentration limit (ppm) | PDE (mg/day) || Nitromethane | 0.5 | 50"
        self.assertEqual(vision.table_quote_found(wrong, "ich-q3c-r9.pdf", 13, header_page=12), (False, False))
