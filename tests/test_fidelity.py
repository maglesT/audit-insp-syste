"""Source fidelity check (tools/parse/fidelity.py, D39): the comparison must catch wrong stored text."""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "parse"))
import fidelity  # noqa: E402

T = fidelity.tokens


def text_flags(stored, printed, small=(), starts=()):
    return fidelity.describe(fidelity.compare_text(T(stored), T(printed), set(small), set(starts)))


PAGE = ("Header line. 9.3 Samples should not be released before testing is complete. The limit is 0.5 % and "
        "products are stored at 25 °C. Footer")


class Tokens(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(T("Store at < 0.5 % and -20 °C; ﬁles, SOFT­WARE (cid:3)"),
                         ["store", "at", "<", "0.5", "%", "and", "−", "20", "c", "files", "software"])

    def test_ligatures_only_as_pairs(self):
        self.assertTrue(fidelity.same("qualification", "qualication"))
        self.assertFalse(fidelity.same("off", "on"))
        self.assertFalse(fidelity.same("five", "four"))


class Catches(unittest.TestCase):
    """Review of D39: errors in stored text that the comparison must flag."""

    def test_exact_text_passes(self):
        self.assertEqual(text_flags("Samples should not be released before testing is complete.", PAGE), "")

    def test_dropped_not(self):
        self.assertEqual(text_flags("Samples should be released before testing is complete.", PAGE), "+not")

    def test_dropped_end_of_clause(self):
        self.assertIn("-", text_flags("Samples should not be released before testing is complete. The limit is 5",
                                      PAGE))

    def test_numbers_signs_units(self):
        self.assertEqual(text_flags("The limit is 5 % and", PAGE), "-5 | +0.5")
        self.assertEqual(text_flags("The limit is 0.5 % and products are stored at 52 °C.", PAGE), "-52 | +25")
        self.assertEqual(text_flags("The limit is < 0.5 % and", "The limit is > 0.5 % and"), "-< | +>")
        self.assertEqual(text_flags("stored at 25 °C here", "stored at 25 °F here"), "-c | +f")
        self.assertEqual(text_flags("stored at -20 °C", "stored at 20 °C"), "-−")

    def test_truncated_or_swapped_word(self):
        self.assertEqual(text_flags("Samples should not be relea before testing", PAGE), "-relea | +released")
        self.assertEqual(text_flags("Samples must not be released", PAGE), "-must | +should")

    def test_one_word_in_a_long_clause(self):
        long = " ".join(f"word{chr(97 + n % 26)}{chr(97 + n // 26)}" for n in range(150))
        self.assertEqual(text_flags(long.replace("wordzb", "wrong"), long), "-wrong | +wordzb")

    def test_exponent_is_not_a_footnote_mark(self):
        printed = T("not more than 10 6 CFU")
        small = {printed.index("6")}
        self.assertEqual(fidelity.describe(fidelity.compare_text(T("not more than 10 CFU"), printed, small)), "+6")


class Tolerates(unittest.TestCase):
    """What the second engine reads differently while the words are the same."""

    def test_split_joined_and_ligature_words(self):
        self.assertEqual(text_flags("a cross- contamination risk", "a crosscontamination risk"), "")
        self.assertEqual(text_flags("a crosscontamination risk", "a cross contamination risk"), "")
        self.assertEqual(text_flags("the qualification of staff", "the qualication of staff"), "")
        self.assertEqual(text_flags("a multidisciplinary team", "a multi 73 disciplinary team"), "")

    def test_footnote_marks(self):
        printed = T("re 23 qualification of systems")
        self.assertEqual(fidelity.describe(fidelity.compare_text(T("requalification of systems"), printed,
                                                                {printed.index("23")})), "")
        self.assertEqual(text_flags("the annex. 1 Records are kept", "the annex. Records are kept",
                                    starts={"1"}), "")

    def test_vertical_text(self):
        self.assertEqual(text_flags("records are kept", "records w h o t r s are kept"), "")


class Coverage(unittest.TestCase):
    def reading(self, *pages):
        return [(T(p), set(), set()) for p in pages], False

    def clause(self, ref, text, page=1, kind="clause"):
        return {"ref": ref, "text": text, "kind": kind, "page_start": page, "page_end": page}

    def test_cut_off_clause_end_is_uncovered(self):
        reading = self.reading("1.1 Samples should not be released before testing is complete. "
                               "1.2 Records are kept for five years.")
        rows, uncovered = fidelity.compare([self.clause("1.1", "1.1 Samples should not be released before"),
                                            self.clause("1.2", "1.2 Records are kept for five years.")], reading)
        self.assertEqual([d for _, _, _, d in rows], ["", ""])
        self.assertEqual(uncovered, [(1, "testing is complete")])

    def test_contents_count_toward_coverage(self):
        reading = self.reading("Contents Scope of the guide 3 1.1 Records are kept for five years.")
        rows, uncovered = fidelity.compare([self.clause("_toc", "Contents Scope of the guide 3", kind="toc"),
                                            self.clause("1.1", "1.1 Records are kept for five years.")], reading)
        self.assertEqual((len(rows), uncovered), (1, []))


class Tables(unittest.TestCase):
    def test_rows_as_a_bag_in_their_own_stretch(self):
        window = T("Grade A 3 520 20 Grade B 352 000 2 900")
        self.assertEqual(fidelity.compare_table(T("A 20 520 3 Grade"), window), [])
        self.assertTrue(fidelity.compare_table(T("Grade A 3 521 20"), window))


class Check(unittest.TestCase):
    def doc(self, discrepancy="-25 | +52"):
        return {"code_sha256": fidelity.code_sha256(), "sources": {"a.pdf": {
            "pdf_sha256": "h", "clauses": 2, "tokens": 9,
            "flagged": [{"ref": "1", "kind": "clause", "tokens": 5, "discrepancy": discrepancy}]}}}

    def test_explanations_must_match_the_discrepancy(self):
        why = [("a.pdf", "1", "-25 | +52", "reason")]
        self.assertEqual(fidelity.problems(self.doc(), why), [])
        self.assertEqual(len(fidelity.problems(self.doc("-25 | +53"), why)), 1)        # changed: lapses
        self.assertEqual(fidelity.problems(self.doc("+ii 3 i 151"), [("a.pdf", "*", r"\+ii 3 i \d+", "gazette")]), [])
        self.assertEqual(len(fidelity.problems(self.doc("-25 | +52"), [("a.pdf", "*", r"\+ii 3 i \d+", "gazette")])), 1)

    def test_stale_reports_and_coverage_fail(self):
        why = [("a.pdf", "1", "-25 | +52", "reason")]
        stale = {**self.doc(), "code_sha256": "old"}
        self.assertIn("another version", fidelity.problems(stale, why)[0][2])
        self.assertIn("differs", fidelity.problems(self.doc(), why, inventory={"a.pdf": "other"})[0][2])
        self.assertIn("missing", fidelity.problems(self.doc(), why, pilot=["a.pdf", "b.pdf"])[0][2])

    def test_committed_report(self):
        import json
        doc = json.loads(fidelity.REPORT.read_text(encoding="utf-8"))
        self.assertEqual(fidelity.problems(doc, fidelity.explanations(), fidelity.inventory_hashes(),
                                           fidelity.pilot_pdfs()), [])


class Rework(unittest.TestCase):
    """Session 4 rework: alignment, tables, repeated lines, page edges; each tolerance next to an error it must
    still catch."""

    def test_a_far_stray_match_does_not_stretch_the_clause(self):
        window = T("9.1 The URS should be complete. " + "Unrelated text follows here. " * 40 + "16")
        self.assertEqual(text_flags("9.1 The URS should be complete. 16", " ".join(window)), "-16")

    def test_chain_restarts_on_a_better_block(self):
        clause = T("4 considerations for marketed products this guideline is not intended to be applied retrospectively")
        window = T("for marketed products " + "filler words " * 60 + clause_text())
        self.assertEqual(fidelity.describe(fidelity.compare_text(clause, window)), "")

    def test_text_held_by_another_clause_is_not_this_clauses(self):
        clause = T("Samples are kept. Records are kept for five years.")
        window = T("Samples are kept. 12 Refer to the annex on storage periods. Records are kept for five years.")
        held = fidelity.grams(T("Refer to the annex on storage periods."))
        self.assertEqual(fidelity.describe(fidelity.compare_text(clause, window, elsewhere=held)), "")
        self.assertEqual(fidelity.describe(fidelity.compare_text(clause, window)), "+12 refer to the annex on storage periods")
        dropped = T("Samples are kept. Records are kept for years.")
        self.assertEqual(fidelity.describe(fidelity.compare_text(dropped, T("Samples are kept. Records are kept for "
                                                                             "five years."), elsewhere=held)), "+five")

    def test_a_table_inside_the_text_is_held_by_its_rows(self):
        clause = T("The limits are given below. Monitoring is continuous.")
        window = T("The limits are given below. Grade A 3 520 Grade B 352 000 Monitoring is continuous.")
        rows = [Counter(T("A | 3 520 | Grade")) + Counter(T("Grade B | 352 000"))]
        self.assertEqual(fidelity.describe(fidelity.compare_text(clause, window, tables=rows)), "")
        self.assertTrue(fidelity.describe(fidelity.compare_text(clause, T("The limits are given below. Grade A 3 521 "
                                                                         "Grade B 352 000 Monitoring is continuous."),
                                                                tables=rows)))

    def test_optional_repeated_lines(self):
        clause = T("records are kept")
        window = T("records who expert committee report are kept")
        soft = {1, 2, 3, 4}
        self.assertEqual(fidelity.describe(fidelity.compare_text(clause, window, soft=soft)), "")
        self.assertIn("are", fidelity.describe(fidelity.compare_text(T("records kept"), window, soft=soft)))

    def test_spaced_capitals_at_the_clause_edge(self):
        window = T("text before 3 d rug p roduct the samples should be tested")
        self.assertEqual(text_flags("3 Drug product The samples should be tested", " ".join(window)), "")
        self.assertIn("-drug substance", text_flags("3 Drug substance The samples should be tested", " ".join(window)))

    def test_table_row_band(self):
        window = T("does the manufacturer have a procedure 4.1 1.12 is it approved")
        place = [(0, 100)] * 6 + [(0, 102), (0, 102), (0, 112), (0, 112), (0, 112)]
        self.assertEqual(fidelity.compare_table(T("1.12 | does the manufacturer have a procedure | 4.1"), window,
                                                place=place), [])
        self.assertTrue(fidelity.compare_table(T("1.21 | does the manufacturer have a procedure | 4.1"), window,
                                               place=place))

    def test_footnote_number_before_held_text(self):
        held = fidelity.grams(T("Refer to compliance program 7356.002F for samples"))
        self.assertTrue(fidelity.stored_elsewhere(T("29 Refer to compliance program 7356.002F for samples"), held))
        self.assertFalse(fidelity.stored_elsewhere(T("29 25 Refer to compliance"), held))

    def test_page_numbers_and_running_lines(self):
        pages = [[[("Article", False, 50.0), (str(n), False, 50.0)], [("Body", False, 300.0), ("text", False, 300.0)],
                  [("iv", False, 780.0)]] for n in range(1, 7)]
        reading, _ = fidelity.read_pages(pages)
        self.assertEqual(reading[0][0], ["article", "1", "body", "text"])  # "Article #" differs by number: kept;
        # the roman page number at the page edge is dropped

    def test_numbered_lines_read_last(self):
        pages = [[[(w, False, 100.0 + 12 * n) for w in f"line of guidance text {n}".split()] for n in range(1, 30)]]
        reading, numbered = fidelity.read_pages(pages)
        self.assertTrue(numbered)
        self.assertNotIn("7", reading[0][0])

    def test_spelled_runs(self):
        self.assertTrue(fidelity.spelled(T("d o c u m e n a n d r ec o r")))
        self.assertFalse(fidelity.spelled(T("samples should not be released")))


def clause_text():
    return "4 c onsiderations f or m arketed p roducts this guideline is not intended to be applied retrospectively"


if __name__ == "__main__":
    unittest.main()
