"""XML profile (tools/fda/xmlprofile.py, D47): exact-text checks on 21 CFR 211."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "fda"))
import xmlprofile as X  # noqa: E402

SRC = "ecfr-21cfr211-2026-10-27.xml"


def item(**kw):
    base = {"statement": "Withhold each lot of components, containers and closures from use until it has been sampled, "
                         "tested or examined and released by the quality control unit.",
            "quote": "Each lot of components, drug product containers, and closures shall be withheld from use until the "
                     "lot has been sampled, tested, or examined, as appropriate, and released for use by the quality "
                     "control unit.",
            "clause_number": "211.84(a)", "strength": "mandatory", "plant_types": ["OSD"], "numbers": [],
            "condition": "", "topic": "MAT.TEST"}
    return {**base, **kw}


class Checks(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(X.parent("211.84(c)(1)"), "211.84(c)")
        self.assertEqual(X.section_of("211.84(c)(1)"), "211.84")
        self.assertIn("211.84", X.sections(SRC))

    def test_right_item(self):
        found, ok = X.check_item(item(), SRC)
        self.assertTrue(ok)
        self.assertNotIn("quote", {c for c, _ in found})

    def test_wrong_paragraph_or_text(self):
        self.assertFalse(X.check_item(item(clause_number="211.84(b)"), SRC)[1])
        self.assertFalse(X.check_item(item(quote=item()["quote"].replace("shall", "should")), SRC)[1])
        self.assertEqual(X.check_item(item(clause_number="211.999(z)"), SRC)[0][0][0], "clause")

    def test_sub_paragraph_takes_the_lead_in_strength(self):
        sub = item(quote="The containers of components selected shall be cleaned when necessary in a manner to prevent "
                         "introduction of contaminants into the component.", clause_number="211.84(c)(1)",
                   statement="When necessary, clean selected component containers so that no contaminants enter.",
                   strength="recommended")
        self.assertIn("strength", {c for c, _ in X.check_item(sub, SRC)[0]})


if __name__ == "__main__":
    unittest.main()
