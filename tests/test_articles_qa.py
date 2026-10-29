import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import articles  # noqa: E402
import common  # noqa: E402
import crosscheck  # noqa: E402
import emahtml  # noqa: E402
import qa  # noqa: E402
import run  # noqa: E402


def refs(parse, name):
    clauses, _, _ = parse(common.OFFICIAL / name)
    return {c.ref: c for c in clauses if c.kind in common.CITABLE}


class Articles(unittest.TestCase):
    def test_regulation_articles_paragraphs_points(self):
        r = refs(articles.parse, "eu-regulation-1252-2014-gmp-active-substances.pdf")
        self.assertIn("conduct regular internal audits", r["Article 3(3)"].text)
        self.assertIn("Article 4(2)(c)", r)
        self.assertIn("Recital (11)", r)
        self.assertIn("Article 3", r)                       # "Article 3" at a page top is not a running header

    def test_directive_footnotes_are_not_recitals(self):
        path = common.OFFICIAL / "eu-directive-2017-1572-gmp.pdf"
        clauses, _, _ = articles.parse(path)
        r = {c.ref: c for c in clauses if c.kind == "clause"}
        self.assertEqual([k for k in r if k.startswith("Recital")], [f"Recital ({n})" for n in range(1, 11)])
        self.assertNotIn("OJ L 311", r["Recital (7)"].text)
        self.assertEqual(crosscheck.missed_obligations(path, clauses), [])


class QA(unittest.TestCase):
    def test_hbel_qa(self):
        r = refs(qa.parse, "ema-hbel-qa-cross-contamination.pdf")
        self.assertEqual([k for k in r if k.startswith("Q")], [f"Q{n}" for n in range(1, 14)])
        self.assertIn("How should manufacturers use the HBELs?", r["Q3"].text)

    def test_contents_list_is_skipped(self):
        clauses, _, _ = qa.parse(common.OFFICIAL / "ema-nitrosamines-qa-mah-rev23-2025.pdf")
        q = [c.ref for c in clauses if c.ref.startswith("Q")]
        self.assertEqual(len(q), len(set(q)))
        self.assertGreaterEqual(len(q), 20)

    def test_chooser_keeps_numbered_texts(self):
        clauses, _, _ = run.text_parser(common.OFFICIAL / "eu-chapter4_01-2011_en.pdf")
        self.assertFalse(any(n.startswith("parser:") for c in clauses for n in c.notes))
        clauses, _, _ = run.text_parser(common.OFFICIAL / "ema-hbel-qa-cross-contamination.pdf")
        self.assertIn("parser: qa", clauses[0].notes)
        clauses, _, _ = run.text_parser(common.OFFICIAL / "eu-directive-2017-1572-gmp.pdf")
        self.assertIn("parser: articles", clauses[0].notes)


class EmaPage(unittest.TestCase):
    def test_questions_under_topics(self):
        r = refs(emahtml.parse, "ema-gmp-gdp-qa.html")
        q1 = r["EU GMP guide part I: Chapter 1: Pharmaceutical quality system Q1"]
        self.assertIn("The product review is expected annually", q1.text)
        self.assertGreaterEqual(len(r), 100)

    def test_topic_label(self):
        title = "EU GMP guide annexes: Supplementary requirements: Annex 11: Computerised systems"
        self.assertEqual(emahtml.topic_label(title), "EU GMP guide annexes: Annex 11: Computerised systems")


if __name__ == "__main__":
    unittest.main()
