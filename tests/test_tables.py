import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import crosscheck  # noqa: E402
import tables  # noqa: E402


def t(page, *rows, before=(), after=()):
    """A hand-made table; before/after = lines between it and the page edge (None: another table is there)."""
    return {"page": page, "rows": [list(r) for r in rows], "before": None if before is None else list(before),
            "after": None if after is None else list(after)}


class Rows(unittest.TestCase):
    """Row rules on hand-made tables."""

    def test_header_continuation_caption_and_labels(self):
        doc = [t(1, ("#", "Questions", "Answers"), ("1.1", "Is it needed?", "It should be"), ("", "", "done daily.")),
               t(2, ("#", "Questions", "Answers"), ("", "", "Records must be kept."), ("1.2", "Why?", "Because.")),
               t(4, ("2. Quality Management System", "", ""), ("1.2", "Again?", "Yes."))]
        doc[0]["after"], doc[1]["before"] = [], ["PI 058-1 Page 5 of 29"]
        c = {x.ref: x for x in tables.rows_to_clauses("x.pdf", doc, {0: "4.6"})}
        self.assertEqual(c["Table 1 header"].kind, "table_header")
        self.assertNotIn("Table 1 header #2", c)                       # the repeated header is kept once
        self.assertEqual(c["Table 1 1.1"].text, "1.1 | Is it needed? | It should be done daily. Records must be kept.")
        self.assertEqual((c["Table 1 1.1"].page_start, c["Table 1 1.1"].page_end), (1, 2))
        self.assertEqual(c["Table 1 1.1"].parent, "4.6")
        self.assertIn("Table 2 2. Quality Management System", c)       # page 4 does not follow page 2: new table
        self.assertEqual(c["Table 2 1.2"].section, "2. Quality Management System")
        self.assertIn("Table 1 1.2", c)

    def test_duplicate_and_long_labels(self):
        doc = [t(1, ("Scope", "a should b"), ("Scope", "c should d"),
                 ("A very long first cell that goes on and on and on", "e"))]
        refs = [x.ref for x in tables.rows_to_clauses("x.pdf", doc)]
        self.assertEqual(refs, ["Table 1 Scope", "Table 1 Scope #2",
                                "Table 1 A very long first cell that goes on and…"])

    def test_repeated_data_row_is_not_a_header(self):
        doc = [t(1, ("Grade", "limit"), ("B", "352 000"), ("C", "3 520 000")),
               t(5, ("Grade", "limit"), ("C", "3 520 000"))]
        refs = [x.ref for x in tables.rows_to_clauses("x.pdf", doc)]
        self.assertEqual(refs, ["Table 1 header", "Table 1 B", "Table 1 C", "Table 2 header", "Table 2 C"])

    def test_separate_tables_on_consecutive_pages(self):
        """A caption between two tables, or the next table starting lower on the page, means a new table, and
        nothing carries over from the old one."""
        doc = [t(1, ("Training", "a"), ("Hygiene", "b"), after=[]),
               t(2, ("", "should be done"), ("X", "y"), before=["Table III: Monitoring"])]
        c = {x.ref: x for x in tables.rows_to_clauses("x.pdf", doc, {0: "4.1", 1: "7.2"})}
        self.assertEqual(c["Table 2 row 1"].parent, "7.2")
        self.assertEqual(c["Table 1 Hygiene"].page_end, 1)

    def test_caption_then_header_on_every_page(self):
        """PIC/S aide-memoire layout: each page repeats the caption and the header; a row that runs over the page
        break joins the last data row, not the header."""
        head = ("Area of operations / items", "Notes", "Crucial questions")
        doc = [t(5, ("2. Quality Management System", "", ""), head, ("PQR", "Annual review", "Is it done?"), after=[]),
               t(6, ("2. Quality Management System", "", ""), head, ("", "covering all batches", ""), before=[])]
        c = {x.ref: x for x in tables.rows_to_clauses("x.pdf", doc)}
        self.assertEqual(sorted(c), ["Table 1 2. Quality Management System", "Table 1 PQR", "Table 1 header"])
        self.assertEqual(c["Table 1 PQR"].text, "PQR | Annual review covering all batches | Is it done?")
        self.assertEqual(c["Table 1 PQR"].section, "2. Quality Management System")

    def test_caption_does_not_swallow_rows(self):
        doc = [t(1, ("9. Packaging", "", ""), ("", "Representative label", "Is it in the BMR?"))]
        refs = [x.ref for x in tables.rows_to_clauses("x.pdf", doc)]
        self.assertEqual(refs, ["Table 1 9. Packaging", "Table 1 row 2"])


class Sources(unittest.TestCase):
    """Table-format sources: rows come out whole, and the cross-check finds no lost obligation."""

    def test_pics_annex1_interpretation(self):
        path = common.OFFICIAL / "pics-pi058-1-annex1-interpretation.pdf"
        clauses, _, _ = tables.parse(path)
        r = {c.ref: c for c in clauses}
        row = next(c for ref, c in r.items() if ref.endswith(" 2.3 (Q#1)"))
        self.assertIn("How frequently should the effectiveness of the CCS be reviewed?", row.text)
        self.assertIn("Continued suitability of the CCS should be assured on an ongoing basis", row.text)
        self.assertEqual(crosscheck.missed_obligations(path, clauses), [])

    def test_ich_q7_qa(self):
        path = common.OFFICIAL / "ich-q7-qa.pdf"
        clauses, _, _ = tables.parse(path)
        row = next(c for c in clauses if c.kind == "table_row" and c.text.startswith("2.5 |"))
        self.assertIn("What should be the frequency of a product quality review?", row.text)
        self.assertEqual(crosscheck.missed_obligations(path, clauses), [])

    def test_no_words_lost_against_plain_layout(self):
        """Every word of the plain layout parse is still there; only the page footer ("PI 058-1 Page 5 of 29
        28 October 2026") that used to leak into table text is gone, and a subscript split ("H2O2" -> "H 2 O 2")."""
        from collections import Counter
        import numbered
        path = common.OFFICIAL / "pics-pi058-1-annex1-interpretation.pdf"
        words = lambda cl: Counter(w for c in cl for w in crosscheck.norm_words(c.text))  # noqa: E731
        lost = words(numbered.parse(path)[0]) - words(tables.parse(path)[0])
        self.assertLessEqual(set(lost), {"pi", "page", "of", "october", "h2o2"})

    def test_table_parent_is_the_enclosing_clause(self):
        clauses, _, _ = tables.parse(common.OFFICIAL / "eu-20220825_gmp-an1_en_0.pdf")
        rows = [c for c in clauses if c.kind == "table_row" and c.parent == "Annex 1 4.31"]
        self.assertIn("B | 10 | 5 | 5", [c.text for c in rows])
        self.assertNotIn("[[TABLE", " ".join(c.text for c in clauses))

    def test_ich_q10_tables_stay_apart(self):
        clauses, _, _ = tables.parse(common.OFFICIAL / "ich-q10.pdf")
        parents = {c.ref.split()[1]: c.parent for c in clauses if c.kind == "table_row"}
        self.assertGreaterEqual(len(parents), 4)                   # Tables I to IV, not merged
        self.assertFalse(any(p.startswith("_") for p in parents.values()))

    def test_hindi_table_rows_are_dropped(self):
        clauses, _, _ = tables.parse(common.OFFICIAL / "india-gsr127e-2025-schm-timeline.pdf")
        self.assertFalse(any(common.devanagari_share(c.text) > 0.05 for c in clauses))

    def test_cell_text_is_not_garbled(self):
        clauses, _, _ = tables.parse(common.OFFICIAL / "india-cdsco-circ-2024-03-risk-based-inspection.pdf")
        text = " ".join(c.text for c in clauses if c.kind == "table_row")
        self.assertIn("Building and premises", text)
        self.assertNotIn("S acnhd- Mpremises", text)

    def test_row_with_several_numbered_items_is_split(self):
        clauses, _, _ = tables.parse(common.OFFICIAL / "pics-pi038-2-am-qrm.pdf")
        refs = {c.ref for c in clauses if c.kind == "table_row"}
        self.assertTrue({"Table 2 1.2", "Table 2 1.3", "Table 2 1.10"} <= refs)

    def test_numbered_text_unchanged_without_tables(self):
        """Without tables, table mode is the plain numbered parse (pinned clauses: test_parse.KnownClauses)."""
        import numbered
        path = common.OFFICIAL / "eu-chapter4_01-2011_en.pdf"
        self.assertEqual([c.to_json() for c in tables.parse(path)[0]], [c.to_json() for c in numbered.parse(path)[0]])


if __name__ == "__main__":
    unittest.main()
