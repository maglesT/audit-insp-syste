"""XML profile (tools/fda/xmlprofile.py, D47): exact-text checks on 21 CFR 211."""
import re
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



class ReviewQueue(unittest.TestCase):
    def test_decisions_are_attributable_and_ship_only_when_proven(self):
        import json
        import tempfile
        import review
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            items = [dict(item(), id="a", source=SRC), dict(item(), id="b", source=SRC), dict(item(), id="c", source=SRC)]
            (run / "items.jsonl").write_text("\n".join(json.dumps(i) for i in items))
            (run / "route.json").write_text(json.dumps({"route": {"a": "auto", "b": "review", "c": "review"},
                                                        "hashes": {"a": X.item_hash(items[0])}}))
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


class Status(unittest.TestCase):
    def test_row_and_json(self):
        import json
        import tempfile
        import status
        md = ("| # | Document | File | Priority | Plant types | Pages | Status | Items | Auto | Review |\n"
              "|---|---|---|---|---|---|---|---|---|---|\n"
              "| 1 | 21 CFR 211 | `a.xml` | must | OSD | - | not started | | | |\n"
              "| 2 | 21 CFR 210 | `b.xml` | must | ALL | - | not started | | | |\n")
        with tempfile.TemporaryDirectory() as tmp:
            wl, st = Path(tmp) / "w.md", Path(tmp) / "s.json"
            wl.write_text(md)
            status.set_status("a.xml", "verified", items=10, auto=8, review=2, usage=50, run="r1", path=st, worklist=wl)
            rows = wl.read_text().splitlines()
            self.assertEqual(rows[2], "| 1 | 21 CFR 211 | `a.xml` | must | OSD | - | verified | 10 | 8 | 2 |")
            self.assertEqual(rows[3], md.splitlines()[3])
            self.assertEqual(json.loads(st.read_text())["documents"]["a.xml"]["runs"], ["r1"])
            with self.assertRaises(SystemExit):
                status.set_status("zzz.xml", "drafted", path=st, worklist=wl)


class SecondReview(unittest.TestCase):
    def test_section_heading_is_not_quotable_but_section_text_is(self):
        self.assertFalse(X.check_item(item(clause_number="211.192", quote="Production record review."), SRC)[1])
        gaps = [g["sentence"] for g in X.coverage(SRC, "211.142", [], [])]
        self.assertTrue(any(g.startswith("Written procedures describing") for g in gaps))
        intro = "Written procedures describing the warehousing of drug products shall be established and followed."
        it = item(clause_number="211.142", quote=intro, statement="Establish and follow written warehousing procedures.")
        gaps = [g["sentence"] for g in X.coverage(SRC, "211.142", [it], [])]
        self.assertFalse(any(g.startswith("Written procedures describing") for g in gaps))

    def test_short_sentence_not_applicable_whole(self):
        s = "Such depyrogenation processes shall be validated."
        self.assertIn(s, [g["sentence"] for g in X.coverage(SRC, "211.94", [], [])])
        na = [{"clause_number": "211.94(c)", "text": s, "reason": "test"}]
        self.assertNotIn(s, [g["sentence"] for g in X.coverage(SRC, "211.94", [], na)])

    def test_redraft_is_a_new_run(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "verify").mkdir()
            (Path(tmp) / "source.json").write_text('{"source": "%s"}' % SRC)
            with self.assertRaises(SystemExit):
                X.ingest_draft(tmp)


class LeadInSentence(unittest.TestCase):
    def test_only_the_list_introducing_sentence_is_the_lead_in(self):
        lead = X.lead_in_text("11.10(a)", dict(X.paragraphs("fda-cfr-21-part-11.xml")))
        self.assertNotIn("when appropriate", lead)
        self.assertTrue(lead.rstrip().endswith(":"))
        self.assertIn("prevent contamination or mixups", X.lead_in_text("211.42(c)(1)", dict(X.paragraphs(SRC))))


class LeadInNumbers(unittest.TestCase):
    def test_statement_may_carry_the_lead_in_number(self):
        src = "fda-cfr-21-314.81.xml"
        ref = next(r for r, t in X.paragraphs(src) if r == "314.81(b)(1)(i)")
        q = X.own_text(ref, dict(X.paragraphs(src))[ref])
        self.assertIn("3 working days", " ".join(X.ancestors_text(ref, dict(X.paragraphs(src)))))
        it = item(clause_number=ref, quote=q, plant_types=["OSD"], statement="Within 3 working days, report " + q)
        self.assertNotIn("numbers", {c for c, _ in X.check_item(it, src)[0]})
        it2 = dict(it, statement="Within 4 working days, report " + q)
        self.assertIn("numbers", {c for c, _ in X.check_item(it2, src)[0]})


class Packing(unittest.TestCase):
    def test_batches_by_size(self):
        secs = {"a": [("a", "x" * 15000)], "b": [("b", "x" * 6000)], "c": [("c", "x" * 30000)], "d": [("d", "x")]}
        self.assertEqual(X.pack(list(secs), secs), [["a"], ["b"], ["c"], ["d"]])
        small = {str(i): [(str(i), "x")] for i in range(12)}
        self.assertEqual([len(b) for b in X.pack(list(small), small)], [10, 2])


class DescriptiveMay(unittest.TestCase):
    def test_may_affect_is_not_optional(self):
        self.assertIsNone(X.strength_words("Changes that may affect drug substance or drug product sterility assurance"))
        self.assertEqual(X.strength_words("The applicant may commence distribution"), "optional")


class QuestionHeadings(unittest.TestCase):
    def test_heading_ending_in_question_mark(self):
        t = "§ 207.54 What listing information must a registrant submit for a drug that it salvages? A registrant must list."
        self.assertEqual(X.own_text("207.54", t), "A registrant must list.")


class ThirdReview(unittest.TestCase):
    def test_permission_may_stays_optional(self):
        self.assertEqual(X.strength_words("The declaration may contain common or decimal fractions."), "optional")
        self.assertEqual(X.strength_words("The statement may appear highlighted."), "optional")

    def test_reference_numbers_in_lead_in_lend_nothing(self):
        src = "fda-cfr-21-314.81.xml"
        paras = dict(X.paragraphs(src))
        self.assertFalse(any("(3)" in t or "(a)" in t for t in X.ancestors_text("314.81(b)(3)(iii)(c)(1)", paras)))

    def test_scoping_fragment_before_list_sentence_is_kept(self):
        lead = X.lead_in_text("201.326(a)(1)(iii)(A)", dict(X.paragraphs("fda-cfr-21-part-201.xml"))) \
            if "fda-cfr-21-part-201.xml" in {p.name for p in X.OFFICIAL.iterdir()} else "For products labeled for adults only. x:"
        self.assertIn("adults only", lead)


class CrossReferences(unittest.TestCase):
    def test_cross_references_are_not_numbers(self):
        self.assertNotIn("211", X.without_refs("as required in § 211.192 and parts 600 through 680"))
        self.assertIn("30", X.without_refs("within 30 days, see §§ 211.68 and 211.188(b)(11)"))
        refs = "addressed by §§ 211.101(c) or (d), 211.103, 211.182, or 211.188(b)(11) can; under §§ 211.198, 211.204, or 211.208 of"
        self.assertFalse(re.findall(r"\d", X.without_refs(refs)))
        q = ("Any unexplained discrepancy shall be thoroughly investigated, in accordance with the written procedures "
             "of § 211.192")
        self.assertEqual(X.without_refs(q).count("211"), 0)


class ReviewFixes(unittest.TestCase):
    """Findings of the independent review of the XML profile and the review queue (31 Oct 2026)."""

    def test_empty_heading_or_child_quote_is_not_confirmed(self):
        self.assertFalse(X.check_item(item(quote=""), SRC)[1])
        self.assertFalse(X.check_item(item(quote=".;"), SRC)[1])
        child = "Floors, walls, and ceilings of smooth, hard surfaces that are easily cleanable"
        self.assertFalse(X.check_item(item(clause_number="211.42", quote=child), SRC)[1])
        self.assertTrue(X.check_item(item(clause_number="211.110(a)(2)", quote="Disintegration time;"), SRC)[1])
        self.assertFalse(X.check_item(item(clause_number="211.110(a)(2)", quote="time;"), SRC)[1])
        intro = "Written procedures describing the warehousing of drug products shall be established and followed."
        self.assertTrue(X.check_item(item(clause_number="211.142", quote=intro), SRC)[1])   # section text itself
        self.assertFalse(X.check_item(item(clause_number="211.42(c)", quote=child), SRC)[1])
        self.assertTrue(X.check_item(item(clause_number="211.42(c)(10)(i)", quote=child), SRC)[1])
        undivided = "A written record of the investigation shall be made and shall include the conclusions and followup."
        self.assertTrue(X.check_item(item(clause_number="211.192", quote=undivided), SRC)[1])   # no paragraphs

    def test_quote_runs_into_sub_paragraph_without_designation(self):
        q = ("Samples shall be collected in accordance with the following procedures: The containers of components "
             "selected shall be cleaned")
        found, ok = X.check_item(item(clause_number="211.84(c)", quote=q, statement="Collect samples as follows."), SRC)
        self.assertTrue(ok)
        q2 = q.replace("procedures: The", "procedures: (1) The")
        found, ok = X.check_item(item(clause_number="211.84(c)", quote=q2, statement="Collect samples as follows."), SRC)
        self.assertNotIn("numbers", {c for c, _ in found})

    def test_item_from_another_section(self):
        self.assertIn("clause", {c for c, _ in X.check_item(item(), SRC, "211.42")[0]})

    def test_not_applicable_needs_eight_words_of_its_paragraph(self):
        base = len(X.coverage(SRC, "211.84", [], []))
        self.assertGreater(base, 0)
        self.assertEqual(len(X.coverage(SRC, "211.84", [], [{"clause_number": "", "text": "a", "reason": "x"}])), base)
        self.assertEqual(len(X.coverage(SRC, "211.84", [], [{"clause_number": "", "text": "shall", "reason": "x"}])),
                         base)

    def test_route_needs_one_a_and_one_b_on_the_item_as_shown(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "verify" / "batches").mkdir(parents=True)
            (run / "verify" / "answers").mkdir()
            its = [dict(item(), id=n, hash=X.item_hash(item())) for n in ("x", "y", "z")]
            for role, n in (("a", 1), ("b", 2)):
                (run / "verify" / "batches" / f"batch_00{n}_{role}.json").write_text(json.dumps(
                    {"role": role, "items": [{"id": i["id"], "hash": i["hash"]} for i in its]}))
            a = [{"id": "x", "verdict": "correct"}, {"id": "y", "verdict": "correct"}, {"id": "y", "verdict": "correct"},
                 {"id": "z", "verdict": "correct"}]
            b = [{"id": "x", "verdict": "correct"}, {"id": "y", "verdict": "correct"}]
            (run / "verify" / "answers" / "batch_001_a.json").write_text(json.dumps({"answers": a}))
            (run / "verify" / "answers" / "batch_002_b.json").write_text(json.dumps({"answers": b}))
            self.assertEqual(X.proven_by_both(run, its), {"x"})              # y answered twice by A, z never by B
            redrafted = [dict(its[0], statement="something else")]
            redrafted[0]["hash"] = X.item_hash(redrafted[0])
            self.assertEqual(X.proven_by_both(run, redrafted), set())
            self.assertEqual(X.proven_by_both(run, [dict(its[0], condition="changed")]), set())   # stale stored hash
            # one verifier's answers saved under both names: the B batch file decides the role, so it counts once
            (run / "verify" / "batches" / "batch_002_b.json").write_text(json.dumps(
                {"role": "a", "items": [{"id": i["id"], "hash": i["hash"]} for i in its]}))
            self.assertEqual(X.proven_by_both(run, its), set())

    def test_decisions_belong_to_their_run_and_item_and_reject_beats_auto(self):
        import json
        import tempfile
        import review
        with tempfile.TemporaryDirectory() as tmp:
            r1, r2 = Path(tmp) / "r1", Path(tmp) / "r2"
            dec = Path(tmp) / "decisions.jsonl"
            for r, stmt in ((r1, item()["statement"]), (r2, "A different redrafted statement.")):
                r.mkdir()
                (r / "items.jsonl").write_text(json.dumps(dict(item(statement=stmt), id="i", source=SRC)) + "\n" +
                                               json.dumps(dict(item(), id="j", source=SRC)))
                (r / "route.json").write_text(json.dumps({"route": {"i": "review", "j": "auto"},
                                                          "hashes": {"j": X.item_hash(item())}}))
            review.decide(r1, "i", "correct", by="QA lead", path=dec)
            self.assertEqual(sorted(review.shipped(r1, dec)), ["i", "j"])
            self.assertEqual(review.shipped(r2, dec), ["j"])                 # r1's decision is not r2's item
            review.decide(r1, "j", "reject", by="QA lead", note="spot check", path=dec)
            self.assertEqual(review.shipped(r1, dec), ["i"])
            # items.jsonl rewritten after routing: the old "auto" does not ship the new item under that id
            (r2 / "items.jsonl").write_text(json.dumps(dict(item(statement="Redrafted."), id="j", source=SRC)))
            self.assertEqual(review.shipped(r2, dec), [])


class LeadInWordForms(unittest.TestCase):
    """Equivalent wording of a lead-in condition is not flagged; a dropped or changed condition still is (Part 4)."""
    P4 = "fda-cfr-21-part-4.xml"

    def lead(self, ref):
        return X.lead_in_text(ref, dict(X.paragraphs(self.P4)))

    def test_word_forms_carry_the_condition(self):
        import vision
        lead = "If you manufacture a combination product, the requirements listed in this section apply as follows:"
        self.assertEqual(vision.stem("manufacture"), vision.stem("manufacturing"))
        self.assertEqual(vision.stem("elect"), vision.stem("elected"))
        self.assertEqual(vision.lead_in_missing(lead, "When manufacturing a combination product, comply with the "
                                                      "drug CGMP regulations."), [])
        self.assertEqual(vision.lead_in_missing(lead, "If combination products are manufactured, comply with ..."), [])

    def test_dropped_or_changed_condition_still_caught(self):
        import vision
        lead = "If you manufacture a combination product, the requirements listed in this section apply as follows:"
        self.assertTrue(vision.lead_in_missing(lead, "Comply with the drug CGMP regulations."))           # dropped
        self.assertTrue(vision.lead_in_missing(lead, "When manufacturing a drug, comply with the drug CGMP."))  # changed
        self.assertTrue(vision.lead_in_missing("If cut labeling is used for immediate container labels, ...:",
                                               "Where cut labeling is used, examine it."))        # part of it dropped
        q3c = ("However, if their use is unavoidable in order to produce a drug product with a significant "
               "therapeutic advance, then their levels should be restricted as shown in Table 1.")
        self.assertTrue(vision.lead_in_missing(q3c, "When used, limit benzene to 2 ppm."))

    def test_role_as_a(self):
        import vision
        lead = "If you are a constituent part applicant:"
        self.assertEqual(vision.lead_in_missing(lead, "As a constituent part applicant, keep the records."), [])
        self.assertTrue(vision.lead_in_missing(lead, "As a manufacturer, keep the records."))       # another role
        self.assertTrue(vision.lead_in_missing(lead, "Keep the records as required."))              # no role at all

    def test_references_list_tail_and_cgmp_are_not_condition_words(self):
        import vision
        lead = self.lead("4.4(b)(1)")
        self.assertIn("paragraph (b) of this section", lead)
        self.assertEqual(vision.lead_in_missing(lead, "Where you elect to establish a CGMP operating system under the "
                                                      "streamlined approach, also meet ..."), [])
        self.assertTrue(vision.lead_in_missing(lead, "Where a CGMP operating system exists, also meet ..."))
        change = "Registrants must update the NDC when there is a change to any of the following information:"
        self.assertEqual(vision.lead_in_missing(change, "Use a new product code when the drug's name changes."), [])
        self.assertTrue(vision.lead_in_missing(change, "Use a new product code for the drug."))

    def test_review_cases_stay_flagged(self):
        import vision
        m = vision.lead_in_missing
        self.assertTrue(m("Unless you are a small business, keep the records:", "As a small business, keep the records."))
        self.assertTrue(m("If it is a combination product, the following apply:", "Label the drug as a combination product."))
        self.assertTrue(m("Where the firm is a contract manufacturer:", "The firm keeps records as the contract manufacturer requires."))
        self.assertTrue(m("If you are a contract manufacturer:", "Keep the records, as a contract manufacturer may be audited."))
        self.assertTrue(m("If any of the following occur during sterile drug manufacturing:", "If a deviation occurs, investigate it."))
        self.assertTrue(m("Where the products are manufactured for each of the following markets in the European Union:",
                          "Where products are manufactured, test them."))
        self.assertTrue(m("If the product is terminally sterilized:", "If the product is terminally sterile, test it."))
        self.assertTrue(m("If the method is validated:", "If the method is valid, use it."))
        self.assertTrue(m("If the drug is not sterile:", "If the drug is sterile, test it."))
        self.assertTrue(m("Only if the batch fails:", "If the batch fails, investigate."))
        self.assertEqual(m("If you process the drug:", "When processing the drug, test it."), [])
        self.assertEqual(m("If the product is sterilized:", "When sterilization is used for the product, ..."), [])

    def test_qualifier_by_stem(self):
        lead = ("such other control systems for the firm's operations as are necessary to prevent contamination or "
                "mixups during the course of the following procedures:")
        self.assertEqual(X.qualifier_missing(lead, "Provide control systems as needed to prevent contaminating or "
                                                   "mixups during storage."), [])
        self.assertEqual(X.qualifier_missing(lead, "Provide control systems as needed to prevent contamination or "
                                                   "mixups during storage."), [])
        self.assertTrue(X.qualifier_missing(lead, "Provide separate areas for storage."))


if __name__ == "__main__":
    unittest.main()
