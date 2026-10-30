"""Source fidelity check (tools/parse/fidelity.py, D39): the comparison must catch wrong stored text."""
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
