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
        entries = dict(graph.glossary_entries("eu-glossary.pdf", "EudraLex Vol 4 Glossary"))
        self.assertIn("AIR-LOCK", entries)
        self.assertTrue(entries["AIR-LOCK"].startswith("An enclosed space"))
        who = dict(graph.glossary_entries("who-trs986-a2-gmp-main.pdf", "WHO GMP main principles"))
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


if __name__ == "__main__":
    unittest.main()
