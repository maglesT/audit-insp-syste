import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "extract"))
import cdsco  # noqa: E402
import tagged  # noqa: E402


def cell(text, x0, x1, top=100):
    return {"text": text, "box": [x0, top, x1, top + 10]}


def qrow(no, ref, question, top=100):
    return [cell(no, 70, 96, top), cell(ref, 120, 158, top), cell(question, 177, 468, top),
            cell(" ", 500, 600, top), cell(" ", 650, 700, top)]


class RulesTest(unittest.TestCase):
    def test_restore_rounded_numbers(self):
        self.assertEqual(cdsco.restore_number("39.1", ("39", 10)), "39.11")
        self.assertEqual(cdsco.restore_number("39.2", ("39", 14)), "39.15")   # half up
        self.assertEqual(cdsco.restore_number("39.2", ("39", 1)), "39.2")     # the real 39.2
        self.assertEqual(cdsco.restore_number("39.3", ("39", 10)), "39.3")    # not the rounding of 39.11
        self.assertEqual(cdsco.restore_number("40.1", ("39", 19)), "40.1")    # new section
        self.assertEqual(cdsco.restore_number("4.17.1", ("4", 17)), "4.17.1")

    def test_columns_by_position(self):
        self.assertEqual(cdsco.column([70, 0, 96, 0]), "no")
        self.assertEqual(cdsco.column([111, 0, 164, 0]), "reference")
        self.assertEqual(cdsco.column([109, 0, 471, 0]), "question")

    def test_symbol_bullets(self):
        self.assertEqual(cdsco.clean("a:\uf0be b \uf0b7 c"), "a:\u2014 b \u2022 c")

    def test_page_break_and_headings(self):
        pages = [
            {"page": 24, "rows": [[cell("4 Water system: -", 65, 274)],
                                  qrow("4.6", "WHO TRS-970", "Phase 1: Whether defined.", 200)], "outside": ""},
            {"page": 25, "rows": [[cell("Whether records maintained.", 177, 468, 80)],
                                  [cell(" ", 70, 96), cell("ANNEXE-06", 111, 164, 90), cell(" ", 177, 200)],
                                  qrow("4.7", "Sch-M", "Next question.", 120),
                                  qrow("4.8", "", "Building and Facilities:-", 140),
                                  [cell("Do the records show details", 109, 471, 160)]], "outside": ""},
        ]
        questions, _ = cdsco.build(pages)
        self.assertEqual([q["no"] for q in questions], ["4.6", "4.7", ""])
        self.assertEqual(questions[0]["question"], "Phase 1: Whether defined. Whether records maintained.")
        self.assertEqual(questions[0]["section"], "4 Water system: -")
        self.assertIn("no number printed", questions[2]["flags"])

    def test_page_top_reference_tail_joins_reference(self):
        pages = [
            {"page": 30, "rows": [qrow("18.13", "WHO TRS-961", "Specify the air classification.")], "outside": ""},
            {"page": 31, "rows": [[cell(" ", 70, 96), cell("ANNEXE-06", 111, 164, 80), cell(" ", 177, 180)],
                                  [cell("19 Monitoring:-", 65, 242, 90)]], "outside": ""},
        ]
        questions, _ = cdsco.build(pages)
        self.assertEqual(questions[0]["reference"], "WHO TRS-961 ANNEXE-06")
        self.assertEqual(questions[0]["question"], "Specify the air classification.")


class StoredExtractTest(unittest.TestCase):
    def test_stored_extract_report(self):
        data = json.loads(cdsco.OUT_JSON.read_text())
        r = data["report"]
        self.assertEqual(r["questions"], 554)
        self.assertEqual(r["cross_check"].get("number differs", 0), 0)
        self.assertGreaterEqual(r["cross_check"]["exact"], 535)
        ids = [q["id"] for q in data["questions"]]
        self.assertEqual(len(ids), len(set(ids)))
        flag = "the PDF prints this number for more than one question"
        twice = sorted({q["no"] for q in data["questions"] if flag in q["flags"]})
        self.assertEqual(twice, ["11.11"])  # printed twice in both parts of the PDF
        row = next(q for q in data["questions"] if q["no"] == "4.18")
        self.assertEqual(row["question"], "Verify whether the circulation rate of purified water & WFI is at least "
                                          "twice the storage capacity of the holding vessels per hour.")

    def test_tagged_reader_on_source(self):
        pdf = ROOT / "sources" / "official" / cdsco.SOURCE
        page = tagged.read_rows(pdf, pages={45})[0]
        texts = [" ".join(c["text"].split()) for r in page["rows"] for c in r]
        self.assertIn("18.13", texts)


if __name__ == "__main__":
    unittest.main()
