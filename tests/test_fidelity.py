"""Source fidelity check (tools/parse/fidelity.py, D38)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "parse"))
import fidelity  # noqa: E402


def clause(ref, text, kind="clause", pages=(1, 1)):
    return {"ref": ref, "text": text, "kind": kind, "page_start": pages[0], "page_end": pages[1]}


class Fidelity(unittest.TestCase):
    def test_words_are_normalised(self):
        self.assertEqual(fidelity.words("Manufac- turing ﬁles, SOFT­WARE; 9.3"),
                         ["manufacturing", "files", "software", "9", "3"])

    def test_share(self):
        page = fidelity.words("Header line. 9.3 All self inspections should be recorded. Footer 12")
        self.assertEqual(fidelity.share(fidelity.words("9.3 All self inspections should be recorded."), page), 1.0)
        self.assertEqual(fidelity.share(fidelity.words("All self inspections must be recorded."), page), 5 / 6)
        self.assertEqual(fidelity.share(fidelity.words("recorded be should"), page), 1 / 3)       # order counts
        self.assertEqual(fidelity.share(fidelity.words("recorded be should"), page, bag=True), 1.0)  # tables

    def test_compare_uses_the_clause_pages_with_a_margin(self):
        pages = [fidelity.words("intro"), fidelity.words("A B C"), fidelity.words("D E"), fidelity.words("far away")]
        rows = fidelity.compare([clause("1", "C D", pages=(2, 2)), clause("2", "far away", pages=(1, 1)),
                                 clause("t", "toc 3", kind="toc")], pages)
        self.assertEqual([(r, s) for r, _, s, _ in rows], [("1", 1.0), ("2", 0.0)])      # page 4 is out of reach

    def test_flags_and_explanations(self):
        doc = {"clause_min": 0.99, "source_min": 0.995, "sources": {
            "a.pdf": fidelity.source_summary([("1", "clause", 1.0, 10), ("2", "clause", 0.5, 10)]),
            "b.pdf": fidelity.source_summary([("1", "clause", 0.9, 10)])}}
        self.assertEqual(doc["sources"]["a.pdf"]["median"], 0.75)
        missing = fidelity.unexplained(doc, {})
        self.assertEqual([(f, r) for f, r, _ in missing], [("a.pdf", "*"), ("a.pdf", "2"), ("b.pdf", "*"), ("b.pdf", "1")])
        why = {("a.pdf", "*"): "figure text", ("b.pdf", "1"): "flowchart"}
        self.assertEqual([(f, r) for f, r, _ in fidelity.unexplained(doc, why)], [("b.pdf", "*")])

    def test_committed_report_is_explained(self):
        if not fidelity.REPORT.exists():
            self.skipTest("no fidelity report yet")
        import json
        doc = json.loads(fidelity.REPORT.read_text(encoding="utf-8"))
        self.assertEqual(fidelity.unexplained(doc, fidelity.explanations()), [])


if __name__ == "__main__":
    unittest.main()
