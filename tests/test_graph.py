import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "ai"))
import graph  # noqa: E402
import layer1  # noqa: E402
import model  # noqa: E402

SOURCES = {
    "ch1.pdf": {"regulator": "EU", "title": "Part I Chapter 1 Pharmaceutical Quality System"},
    "ch5.pdf": {"regulator": "EU", "title": "Part I Chapter 5 Production"},
    "an15.pdf": {"regulator": "EU", "title": "Annex 15 Qualification and Validation"},
    "an15d.pdf": {"regulator": "EU", "title": "DRAFT revised Annex 15 - Qualification"},
    "gl.pdf": {"regulator": "EU", "title": "EudraLex Vol 4 Glossary"},
    "pics.pdf": {"regulator": "PICS", "title": "PE 009-18 Guide to GMP - Part I"},
    "p211.xml": {"regulator": "FDA", "title": "21 CFR Part 211 - CGMP for finished pharmaceuticals"},
    "p210.xml": {"regulator": "FDA", "title": "21 CFR Part 210 - CGMP general"},
}
SHARED = ("Changes should be assessed for their impact on product quality, and the assessment should be "
          "documented and approved before the change is implemented in the manufacturing process.")


def seg(ref, text, kind="clause", section=""):
    return {"ref": ref, "text": text, "kind": kind, "section": section, "heading": ""}


SEGMENTS = {
    "ch1.pdf": [seg("_toc:1.4", "1.4 Contents entry see 1.9", "toc"),
                seg("1.4", "1.4 Records are kept as described in paragraph 1.9 and Annex 15."),
                seg("1.9", "1.9 Quality control covers sampling, see 5.21 and Chapter 5; the qualified person signs."),
                seg("1.10", SHARED),
                seg("1.11", "1.11 This chapter, Chapter 1, applies. Annex 2 also applies.")],
    "ch5.pdf": [seg("Chapter 5 5.21", "5.21 Sampling should follow a written procedure.")],
    "an15.pdf": [seg("1", "1 Qualification should be planned.")],
    "an15d.pdf": [seg("1", "1 Draft text.")],
    "gl.pdf": [seg("_unnumbered:1", "Qualified Person: The person responsible for batch certification.", "unnumbered"),
               seg("_unnumbered:2", "Batch: A defined quantity of material.", "unnumbered")],
    "pics.pdf": [seg("Part I 1.10", SHARED.replace("documented", "documented,"))],
    "p211.xml": [seg("211.84", "Testing as in § 211.80 and § 210.3."),
                 seg("211.80", "(a) There shall be written procedures."), seg("211.80(b)", "(b) More text.")],
    "p210.xml": [seg("210.3", "Definitions apply.")],
}


def entries_of(source, title):
    """Stand-in for reading the glossary PDF."""
    if source != "gl.pdf":
        return []
    return [("QUALIFIED PERSON", "The person responsible for batch certification."),
            ("Batch (or Lot)", "A defined quantity of material."), ("Appendix 1. Tables", "Not a term.")]


def clauses_of(source):
    return {s["ref"]: s for s in SEGMENTS[source] if s["kind"] in layer1.CITABLE}


class References(unittest.TestCase):
    def setUp(self):
        self.docs = graph.documents(SOURCES)

    def refs(self, source):
        return graph.references(source, SEGMENTS[source], SOURCES, self.docs, clauses_of)

    def test_documents_from_titles(self):
        self.assertEqual(self.docs[("EU", "annex", "15")], "an15.pdf")            # the draft is left out
        self.assertEqual(self.docs[("EU", "chapter", "5")], "ch5.pdf")
        self.assertEqual(self.docs[("PICS", "part", "I")], "pics.pdf")
        self.assertEqual(self.docs[("FDA", "cfr", "211")], "p211.xml")

    def test_find_ref(self):
        tree = {"Chapter 5 5.21": 0, "211.80": 0, "211.84(a)": 0}
        self.assertEqual(graph.find_ref(tree, "5.21"), "Chapter 5 5.21")
        self.assertEqual(graph.find_ref(tree, "211.80"), "211.80")
        self.assertEqual(graph.find_ref(tree, "211.84"), "211.84(a)")              # first paragraph
        self.assertIsNone(graph.find_ref(tree, "1.21"))

    def test_eu_references(self):
        links = {(a, b, c) for a, b, c, _ in self.refs("ch1.pdf")}
        self.assertIn(("1.4", "ch1.pdf", "1.9"), links)                         # paragraph in the same source
        self.assertIn(("1.4", "an15.pdf", None), links)                         # Annex 15, document level
        self.assertIn(("1.9", "ch5.pdf", "Chapter 5 5.21"), links)              # "see 5.21" in another chapter
        self.assertIn(("1.9", "ch5.pdf", None), links)                          # Chapter 5
        self.assertNotIn(("1.11", "ch1.pdf", None), links)                      # the chapter naming itself
        self.assertIn(("1.11", None, None), links)                              # Annex 2 is not catalogued
        self.assertFalse(any(a.startswith("_toc") for a, _, _ in links))        # contents entries are skipped

    def test_cfr_references(self):
        links = {(a, b, c) for a, b, c, _ in self.refs("p211.xml")}
        self.assertEqual(links, {("211.84", "p211.xml", "211.80"), ("211.84", "p210.xml", "210.3")})


class Definitions(unittest.TestCase):
    def test_glossary_terms_and_uses(self):
        terms = graph.glossary_terms("gl.pdf", SEGMENTS["gl.pdf"], SOURCES["gl.pdf"]["title"], entries_of)
        self.assertEqual([t[:2] for t in terms], [("_unnumbered:1", "QUALIFIED PERSON")])  # "Batch": too short
        self.assertEqual(terms[0][2], "The person responsible for batch certification.")
        rows = graph.definitions({"EU": ["gl.pdf", "ch1.pdf"]}, SEGMENTS.get, SOURCES, entries_of)
        self.assertEqual(rows, [("gl.pdf", "_unnumbered:1", "ch1.pdf", "1.9", "QUALIFIED PERSON")])

    def test_glossary_entries_from_layout(self):
        if not (graph.model.ROOT / "sources" / "official" / "eu-glossary.pdf").exists():
            self.skipTest("source not present")
        entries = {t: d for _, t, d in graph.glossary_entries("eu-glossary.pdf", "EudraLex Vol 4 Glossary")}
        self.assertIn("AIR-LOCK", entries)
        self.assertTrue(entries["AIR-LOCK"].startswith("An enclosed space"))
        who = {t: d for _, t, d in graph.glossary_entries("who-trs986-a2-gmp-main.pdf", "WHO GMP main principles")}
        self.assertIn("airlock", who)


class SameText(unittest.TestCase):
    def test_near_identical_clauses_across_sources(self):
        clauses = [(("ch1.pdf", "1.10"), SHARED), (("pics.pdf", "Part I 1.10"), SHARED.replace("documented", "documented,")),
                   (("ch1.pdf", "1.9"), SEGMENTS["ch1.pdf"][2]["text"]), (("an15.pdf", "1"), "1 Qualification.")]
        pairs = graph.same_text(clauses)
        self.assertEqual([(a, b) for a, b, _ in pairs], [(("ch1.pdf", "1.10"), ("pics.pdf", "Part I 1.10"))])
        self.assertGreaterEqual(pairs[0][2], graph.SAME_TEXT)
        self.assertEqual(graph.same_text([(("a", "1"), SHARED), (("a", "2"), SHARED)]), [])   # same source

    def test_different_text_is_not_paired(self):
        other = SHARED.replace("before the change is implemented", "after a risk review by the head of QA")
        self.assertEqual(graph.same_text([(("a", "1"), SHARED), (("b", "1"), other)]), [])


def req(rid, mappings):
    return {"id": rid, "status": "verified", "mappings": [
        {"source": s, "clause_ref": r, "relation": rel} for s, r, rel in mappings]}


class Uses(unittest.TestCase):
    def setUp(self):
        self.rows = graph.links(SOURCES, SEGMENTS.get, clauses_of, reqs=[], files=list(SEGMENTS),
                                entries_of=entries_of)

    def test_links_cover_every_kind(self):
        kinds = {r[0] for r in self.rows}
        self.assertEqual(kinds, {"refers_to", "defines", "same_text_as"})
        self.assertTrue(all(len(r) == 6 and all(isinstance(x, str) for x in r) for r in self.rows))

    def test_library_links(self):
        rows = graph.library_links([req("SI-001", [("ch1.pdf", "1.4", "same"), ("p211.xml", "211.84", "stricter")])])
        self.assertIn(("maps_to", "", "SI-001", "ch1.pdf", "1.4", "same"), rows)
        self.assertIn(("stricter_than", "p211.xml", "211.84", "ch1.pdf", "1.4", "SI-001"), rows)

    def test_context(self):
        items = graph.context("ch1.pdf", "1.9", self.rows, SEGMENTS.get, SOURCES, entries_of)
        whys = [w for w, _, _, _ in items]
        self.assertTrue(any("5.21" in w for w in whys))
        self.assertTrue(any("QUALIFIED PERSON" in w for w in whys))
        self.assertTrue(all(t for _, _, _, t in items))                        # texts filled in
        block = graph.context_block(items)
        self.assertTrue(block.startswith("CONTEXT (for understanding only; do not draft"))
        self.assertIn("Sampling should follow a written procedure", block)
        self.assertIn("The person responsible for batch certification.", block)   # the definition only
        self.assertIn("further context left out", graph.context_block(items, limit=10))
        self.assertEqual(graph.context_block([]), "")

    def test_impact(self):
        reqs = [req("SI-001", [("ch5.pdf", "Chapter 5 5.21", "same")]), req("SI-002", [("ch1.pdf", "1.9", "same")]),
                req("SI-003", [("an15.pdf", "1", "same")])]
        hit = graph.impact("ch5.pdf", self.rows, reqs)
        self.assertEqual(set(hit), {"SI-001", "SI-002"})                       # 1.9 refers to 5.21
        self.assertEqual(set(graph.impact("gl.pdf", self.rows, reqs)), {"SI-002"})   # uses a defined term

    def test_consistency(self):
        reqs = [req("SI-001", [("ch1.pdf", "1.10", "same")]), req("SI-002", [("pics.pdf", "Part I 1.10", "same")])]
        self.assertEqual(len(graph.consistency(self.rows, reqs)), 1)
        reqs = [req("SI-001", [("ch1.pdf", "1.10", "same"), ("pics.pdf", "Part I 1.10", "same")])]
        self.assertEqual(graph.consistency(self.rows, reqs), [])

    def test_layer1_twins(self):
        texts = {"ch1.pdf": clauses_of("ch1.pdf"), "pics.pdf": clauses_of("pics.pdf")}
        reqs = [req("SI-001", [("ch1.pdf", "1.10", "same")]), req("SI-002", [("pics.pdf", "Part I 1.10", "same")])]
        found = layer1.check_twins(reqs, texts.get)
        self.assertEqual([f[2] for f in found], ["twins"])

    def test_report(self):
        text = graph.report(self.rows)
        self.assertIn("| ch1.pdf |", text)
        self.assertIn("Annex 2", text)                                          # listed as unresolved

    def test_build_writes_link_table(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        shutil.copy(model.LIBRARY / "topics.json", root / "topics.json")
        (root / "requirements").mkdir()
        import build
        db = sqlite3.connect(build.build(root, links=self.rows))
        n = db.execute("SELECT count(*) FROM link WHERE kind = 'refers_to'").fetchone()[0]
        self.assertEqual(n, sum(1 for r in self.rows if r[0] == "refers_to"))
        db.close()


class Pilot(unittest.TestCase):
    def test_context_is_added_only_when_asked(self):
        import pilot
        self.assertEqual(pilot.with_context("CLAUSE", "s", "r", None), "CLAUSE")
        self.assertEqual(pilot.with_context("CLAUSE", "s", "r", lambda s, r: ""), "CLAUSE")
        self.assertEqual(pilot.with_context("CLAUSE", "s", "r", lambda s, r: "CONTEXT x"), "CLAUSE\n\nCONTEXT x")


COMBINED = {
    "an.pdf": {"regulator": "PICS", "title": "PE 009-18 Guide to GMP - Annexes 1-20"},
    "p1.pdf": {"regulator": "PICS", "title": "PE 009-18 Guide to GMP - Part I"},
    "a17.pdf": {"regulator": "EU", "title": "Annex 17 Real Time Release Testing"},
    "qa.html": {"regulator": "EMA", "title": "EMA Questions and answers"},
    "c5.pdf": {"regulator": "EU", "title": "Part I Chapter 5 Production"},
    "gdp.pdf": {"regulator": "EU", "title": "Guidelines on GDP of active substances"},
    "p211.xml": SOURCES["p211.xml"], "p11.xml": {"regulator": "FDA", "title": "21 CFR Part 11 Electronic Records"},
    "s314.xml": {"regulator": "FDA", "title": "21 CFR 314.70 Supplements"},
    "sm.pdf": {"regulator": "INDIA", "title": "Schedule M"},
}
TREES = {
    "an.pdf": {r: {} for r in ("Annex 1", "Annex 1 3.2", "Annex 19", "Annex 19 2.2", "Annex 19 3.2", "Annex 2A 3.6",
                               "Annex 4", "Annex 4 7", "Annex 15", "Annex 15 1")},
    "p1.pdf": {r: {} for r in ("Part I 3.6", "Part I 5.1")},
    "a17.pdf": {r: {} for r in ("4.9", "4.10")}, "qa.html": {"Q3": {}}, "c5.pdf": {"Chapter 5 5.1": {}, "4.9": {}},
    "gdp.pdf": {"5.1": {}}, "p11.xml": {"11.10(a)": {}}, "s314.xml": {"314.70(b)(2)": {}},
    "p211.xml": {r: {} for r in ("211.84(a)", "211.84(d)", "211.180", "211.182")},
    "sm.pdf": {r: {} for r in ("Part I 1.1", "Part XII", "Part XII 1.1")},
}


class Resolution(unittest.TestCase):
    def refs(self, source, ref, text):
        docs = graph.documents(COMBINED)
        return {(b, c) for _, b, c, _ in graph.references(source, [seg(ref, text)], COMBINED, docs, TREES.get)}

    def test_combined_file_stays_in_its_own_annex(self):
        self.assertEqual(self.refs("an.pdf", "Annex 19 2.2", "Keep samples, see 3.2 below."),
                         {("an.pdf", "Annex 19 3.2")})
        self.assertEqual(self.refs("an.pdf", "Annex 4 7", "Facilities (point 3.6) may be dispensed with."),
                         {("p1.pdf", "Part I 3.6")})                  # Part I, not Annex 2A 3.6
        self.assertEqual(self.refs("an.pdf", "Annex 1 3.2", "Qualify it as set out in Annex 15."),
                         {("an.pdf", "Annex 15")})
        self.assertEqual(self.refs("an.pdf", "Annex 19 2.2", "Samples per Annex 19 are kept."), set())

    def test_scope_named_before_the_number(self):
        self.assertIn(("a17.pdf", "4.9"), self.refs("qa.html", "Q3", "As in annex 17 section 4.9 for release."))
        self.assertEqual(self.refs("qa.html", "Q3", "Described in CTD section 3.2.P.3.5 of the dossier."), set())
        self.assertEqual(self.refs("qa.html", "Q3", "Design per clause 7.3 of ISO 13485 applies."), {(None, None)})

    def test_headings_and_other_documents_chapters(self):
        self.assertEqual(self.refs("an.pdf", "Annex 4 7", "CHAPTER 5 PRODUCTION General text."), set())
        self.assertEqual(self.refs("gdp.pdf", "5.1", "See also chapter 5 of these guidelines for premises."),
                         {(None, None)})                              # not the GMP Part I chapter

    def test_cfr_forms(self):
        found = self.refs("p211.xml", "211.84(a)", "As in §§ 211.180 and 211.182, 21 CFR Part 11, 21 CFR 314.70(b)(2), "
                          "part 11 of this chapter and paragraph (d) of this section.")
        self.assertEqual(found, {("p211.xml", "211.180"), ("p211.xml", "211.182"), ("p11.xml", None),
                                 ("s314.xml", "314.70(b)(2)"), ("p211.xml", "211.84(d)")})

    def test_parts_inside_one_file(self):
        self.assertEqual(self.refs("sm.pdf", "Part I 1.1", "The requirements of Part XII apply."),
                         {("sm.pdf", "Part XII")})

    def test_running_headers_are_not_references(self):
        graph.header_lines.__defaults__[0]["an.pdf"] = ["Annex 1 Manufacture of sterile medicinal products"]
        self.addCleanup(graph.header_lines.__defaults__[0].pop, "an.pdf")
        self.assertEqual(self.refs("an.pdf", "Annex 19 2.2", "Where steam is Annex 1 Manufacture of sterile "
                                   "medicinal products used to condition."), set())

    def test_contents_pages_are_skipped(self):
        self.assertTrue(graph.looks_like_contents("Annex 1 ...... 4 Annex 2 ...... 9"))
        self.assertFalse(graph.looks_like_contents("See Annex 15 for qualification."))


class GlossaryLayout(unittest.TestCase):
    def test_entries_without_blank_lines(self):
        lines = ["GLOSSARY", "", "BULK PRODUCT", "    Any product which has completed all processing stages.",
                 "CALIBRATION", "    The set of operations which establish the relationship.", "",
                 "RECORD", "    See Chapter 4."]
        entries = {t: d for _, t, d in graph._entries(lines, 0, len(lines))}
        self.assertEqual(entries["BULK PRODUCT"], "Any product which has completed all processing stages.")
        self.assertIn("CALIBRATION", entries)

    def test_section_ends_at_the_next_part(self):
        lines = ["Glossary", "", "Acceptance Criteria", "Numerical limits for acceptance of results.", "",
                 "5 REFERENCES", "", "Spiking studies with impurities", "Table text that is not a definition."]
        (start, stop), = graph._sections(lines, "ICH Q2")
        self.assertEqual(stop, 5)
        self.assertEqual([t for _, t, _ in graph._entries(lines, start, stop)], ["Acceptance Criteria"])


class Definitions2(unittest.TestCase):
    def test_longest_term_wins_and_generic_words_are_out(self):
        segs = {"g.pdf": [seg("Glossary", "Glossary", "section")],
                "u.pdf": [seg("1", "Packaging materials should be sampled before use.")]}
        entries = lambda s, t: [("PACKAGING", "Packing."), ("PACKAGING MATERIALS", "Any material."),
                                ("MATERIAL", "Stuff.")] if s == "g.pdf" else []
        src = {"g.pdf": {"regulator": "EU", "title": "EudraLex Vol 4 Glossary"}, "u.pdf": {"regulator": "EU", "title": "x"}}
        rows = graph.definitions({"EU": ["g.pdf", "u.pdf"]}, segs.get, src, entries)
        self.assertEqual([r[4] for r in rows], ["PACKAGING MATERIALS"])

    def test_context_shows_every_term_of_one_glossary(self):
        rows = [("defines", "g.pdf", "Glossary", "u.pdf", "1", "TERM ONE"),
                ("defines", "g.pdf", "Glossary", "u.pdf", "1", "TERM TWO")]
        items = graph.context("u.pdf", "1", rows, {"g.pdf": [seg("Glossary", "x")]}.get,
                              {"g.pdf": {"title": "Glossary"}}, lambda s, t: [("TERM ONE", "first."), ("TERM TWO", "second.")])
        self.assertEqual([t for _, _, _, t in items], ["first.", "second."])

    def test_long_context_items_are_cut_not_dropped(self):
        block = graph.context_block([("a", "s", "1", "x " * 5000), ("b", "s", "2", "short")])
        self.assertIn("[...]", block)
        self.assertIn("short", block)


class SameText2(unittest.TestCase):
    def test_renumbered_twins_pair(self):
        text = SHARED
        pairs = graph.same_text([(("eu", "3.7"), "3.7 " + text), (("who", "12.25"), "12.25 " + text)])
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][2], 1.0)

if __name__ == "__main__":
    unittest.main()
