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


class Checks(unittest.TestCase):
    def test_a_right_item_passes_in_both_readings(self):
        found, in_layer, in_miner = vision.check_item(item(), SRC, PAGE)
        self.assertEqual(found, [])
        self.assertTrue(in_layer and in_miner)

    def test_a_changed_number_in_the_quote_fails_both_readings(self):
        found, in_layer, in_miner = vision.check_item(item(quote=QUOTE.replace("0.5", "0.3")), SRC, PAGE)
        self.assertFalse(in_layer or in_miner)
        self.assertEqual(found[0][0], "quote")

    def test_clause_number_must_be_on_the_page(self):
        self.assertEqual(vision.check_item(item(clause_number="4.31"), SRC, PAGE)[0][0][0], "clause")

    def test_number_strength_and_condition(self):
        checks = {c for c, _ in vision.check_item(item(statement="Measure 0.3 µm particles.", strength="mandatory"),
                                                  SRC, PAGE)[0]}
        self.assertEqual(checks, {"numbers", "strength"})

    def test_coverage(self):
        gaps = vision.coverage(SRC, PAGE, [item()], [], [])
        self.assertFalse(any("total of particles equal to or greater" in g for g in gaps))
        self.assertTrue(any("Classification activities should be scheduled" in g for g in gaps))
        na = [{"text": "Classification activities should be scheduled and performed", "reason": "example"}]
        self.assertFalse(any("Classification activities should be scheduled" in g
                             for g in vision.coverage(SRC, PAGE, [item()], [], na)))


if __name__ == "__main__":
    unittest.main()
