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


class ReviewQueue(unittest.TestCase):
    def test_decisions_are_attributable_and_ship_only_when_proven(self):
        import json
        import tempfile
        import review
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            items = [dict(item(), id="a", source=SRC), dict(item(), id="b", source=SRC), dict(item(), id="c", source=SRC)]
            (run / "items.jsonl").write_text("\n".join(json.dumps(i) for i in items))
            (run / "route.json").write_text(json.dumps({"route": {"a": "auto", "b": "review", "c": "review"}}))
            dec = run / "decisions.jsonl"
            self.assertEqual(review.shipped(run, dec), ["a"])
            with self.assertRaises(SystemExit):
                review.decide(run, "b", "correct", by=" ", path=dec)                 # a name is required
            with self.assertRaises(SystemExit):
                review.decide(run, "b", "fix", by="QA", quote="not in the regulation", statement="x", path=dec)
            rec = review.decide(run, "b", "correct", by="QA lead", path=dec)
            self.assertEqual(rec["by"], "QA lead")
            self.assertTrue(rec["at"].endswith("+00:00"))
            review.decide(run, "c", "reject", by="QA lead", path=dec)
            self.assertEqual(sorted(review.shipped(run, dec)), ["a", "b"])


class Tuning(unittest.TestCase):
    """The three tuning steps after the 211 trial (docs/fda-211-trial.md)."""
    LEAD = ("There shall be separate or defined areas or such other control systems for the firm's operations as are "
            "necessary to prevent contamination or mixups during the course of the following procedures:")

    def test_qualifier_lead_in(self):
        self.assertTrue(X.qualifier_missing(self.LEAD, "Separate or defined areas are provided for receipt of components."))
        self.assertEqual(X.qualifier_missing(self.LEAD, "Provide separate or defined areas or other controls as necessary "
                                                        "to prevent contamination or mixups for receipt of components."), [])
        self.assertTrue(X.qualifier_missing("Aseptic processing, which includes as appropriate:", "Use HEPA filters."))

    def test_lead_ins_chain_to_grandparent(self):
        lead = X.lead_in_text("211.42(c)(10)(i)", dict(X.paragraphs(SRC)))
        self.assertIn("as appropriate", lead)
        self.assertIn("prevent contamination or mixups", lead)
        sub = item(clause_number="211.42(c)(10)(i)",
                   quote="Floors, walls, and ceilings of smooth, hard surfaces that are easily cleanable",
                   statement="Aseptic processing areas have smooth, hard, easily cleanable floors, walls and ceilings.")
        self.assertIn("lead-in", {c for c, _ in X.check_item(sub, SRC)[0]})

    def test_sterile_scope(self):
        q = ("Appropriate written procedures, designed to prevent objectionable microorganisms in drug products not "
             "required to be sterile, shall be established and followed.")
        it = item(clause_number="211.113(a)", quote=q, plant_types=["OSD", "INJ"],
                  statement="Establish and follow written procedures to prevent objectionable microorganisms in drug "
                            "products not required to be sterile.")
        self.assertIn("plants", {c for c, _ in X.check_item(it, SRC)[0]})
        self.assertNotIn("plants", {c for c, _ in X.check_item(dict(it, plant_types=["OSD", "LIQ"]), SRC)[0]})
        self.assertTrue(X.plants_finding("drug products purporting to be sterile", ["OSD", "INJ"]))
        self.assertEqual(X.plants_finding("drug products purporting to be sterile", ["INJ"]), "")

    def test_lead_in_sentence_coverage(self):
        follow = "The written program shall be followed and shall include:"
        kids = [item(clause_number=f"211.166(a)({n})", statement="x", quote="x") for n in range(1, 6)]
        self.assertFalse(X.lead_in_covered("211.166(a)", follow, kids, SRC))       # two duties: needs its own item
        subs = [item(clause_number=f"211.42(c)({n})", quote="x", statement="Provide areas as necessary to prevent "
                     "contamination or mixups.") for n in range(1, 11)]
        self.assertFalse(X.lead_in_covered("211.42(c)", self.LEAD, subs[:9], SRC))  # (c)(10) has no item
        self.assertTrue(X.lead_in_covered("211.42(c)", self.LEAD, subs, SRC))
