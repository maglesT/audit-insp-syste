"""HTML profile (tools/fda/htmlprofile.py, D47 D): units, references and exact-text checks on FDA web pages."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "fda"))
import htmlprofile as H  # noqa: E402

QA = "fda-cgmp-qa-buildings-facilities.html"
GUIDE = "fda-ora-guide-cleaning-validation-1993.html"


def item(**kw):
    base = {"statement": "Take precautions to prevent the use of wood products treated with or exposed to a halogenated "
                         "phenolic preservative anywhere in the supply chain.",
            "quote": "FDA recommends that manufacturers and distributors take precautions to prevent the use of wood "
                     "products treated with or exposed to a halogenated phenolic preservative anywhere in the supply "
                     "chain.",
            "clause_number": "Q8.1", "strength": "recommended", "plant_types": ["OSD"], "numbers": [],
            "condition": "", "topic": "MAT.TEST"}
    return {**base, **kw}


class Units(unittest.TestCase):
    def test_qa_units_and_references(self):
        us = H.units(QA)
        self.assertEqual(list(us)[:3], ["Q1", "Q2", "Q3"])
        self.assertEqual(len(us), 10)
        refs = [p["ref"] for p in us["Q4"]]
        self.assertEqual(refs[0], "Q4")
        texts = " ".join(p["text"] for p in us["Q4"])
        self.assertIn("211.42(d)", texts)                       # the list under the answer stays
        self.assertNotIn("FDA CGMP regulations (21 CFR parts 210", texts)   # the reference list goes
        self.assertNotIn("Date:", texts)
        self.assertEqual(H.clause_of(QA, "Q4.2"), "Q4")

    def test_guide_paragraphs_and_units(self):
        ps = H.cited(GUIDE)
        self.assertIn("¶1", ps)
        self.assertTrue(ps["¶9"]["text"].startswith("FDA expects firms to have written procedures"))
        units = list(H.units(GUIDE))
        self.assertTrue(all("-" in u or u.startswith("¶") for u in units))
        self.assertEqual(sum(1 for p in H.paragraphs(GUIDE) if p["cite"]), len(ps))

    def test_lead_in_of_a_list_item(self):
        self.assertTrue(H.lead_in("Q4.2", QA).endswith(":"))
        self.assertEqual(H.lead_in("Q4.1", QA), "")


class Checks(unittest.TestCase):
    def test_right_item(self):
        found, ok = H.check_item(item(), QA, "Q8")
        self.assertTrue(ok)
        self.assertEqual(found, [])

    def test_quote_must_be_exact_and_start_in_its_paragraph(self):
        self.assertFalse(H.check_item(item(quote="FDA recommends that firms take precautions"), QA)[1])
        self.assertFalse(H.check_item(item(clause_number="Q7.1"), QA)[1])
        self.assertIn("clause", {c for c, _ in H.check_item(item(clause_number="Q99.1"), QA)[0]})
        self.assertIn("clause", {c for c, _ in H.check_item(item(), QA, "Q7")[0]})

    def test_expects_is_recommended(self):
        self.assertEqual(H.strength_of("FDA expects firms to have written procedures"), "recommended")
        self.assertIn("strength", {c for c, _ in H.check_item(item(strength="mandatory"), QA)[0]})

    def test_investigator_instructions_count_for_coverage(self):
        self.assertTrue(H.counts("Determine the number of cleaning processes for each piece of equipment."))
        self.assertTrue(H.counts("FDA expects firms to have written general procedures."))
        self.assertFalse(H.counts("This guide is intended to cover equipment cleaning for chemical residues only."))

    def test_regulation_references_are_not_numbers(self):
        q = "21 CFR 211.42(d): Separation of facility and equipment"
        it = item(quote=q, clause_number="Q4.2", statement="Separate facilities and equipment for penicillin.",
                  strength="mandatory")
        self.assertNotIn("numbers", {c for c, _ in H.check_item(it, QA)[0]})

    def test_coverage_finds_and_closes_gaps(self):
        gaps = H.coverage(QA, "Q8", [], [])
        self.assertEqual([g["clause"] for g in gaps], ["Q8.1", "Q8.1", "Q8.2", "Q8.2"])
        self.assertEqual(len(H.coverage(QA, "Q8", [item()], [])), 3)
        na = [{"clause_number": g["clause"], "text": " ".join(g["sentence"].split()[:9]), "reason": "x"}
              for g in gaps[1:]]
        self.assertEqual(H.coverage(QA, "Q8", [item()], na), [])
        self.assertEqual(len(H.coverage(QA, "Q8", [item()], [dict(n, clause_number="Q8.3") for n in na])), 3)

class Review(unittest.TestCase):
    def test_review_queue_reads_html_items(self):
        import review
        it = dict(item(), source=QA)
        self.assertIn("Q8.1", review.source_text(it))
        self.assertTrue(review.quote_in_source(it, it["quote"]))
        self.assertFalse(review.quote_in_source(it, "words that are not on the page at all"))


if __name__ == "__main__":
    unittest.main()
