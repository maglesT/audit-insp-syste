"""Table Transformer trial (D41, D43): the committed grids, the adopted pages, and the Grid adapter. The model
itself never runs here (CI has no torch); these tests read library/tables-tatr/grids.json only."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "parse"))
import common  # noqa: E402
import run  # noqa: E402
import tables  # noqa: E402
import tatr  # noqa: E402


def parse(name, regulator="WHO"):
    clauses, _, _ = run.parser_for({"file": name, "regulator": regulator})(common.OFFICIAL / name)
    return clauses


class Pins(unittest.TestCase):
    def test_grids_carry_the_pins_and_every_trial_page(self):
        doc = json.loads(tatr.GRIDS.read_text())
        for name, pin in tatr.PINS.items():
            self.assertEqual(doc["models"][name]["revision"], pin["revision"])
            self.assertEqual(doc["models"][name]["files"], pin["files"])
        trial = {f"{s}:{p}" for s, pages in tatr.TRIAL.items() for p in pages}
        self.assertEqual(set(doc["pages"]), trial)
        for key in doc["pages"]:
            self.assertEqual(doc["pages"][key]["sha256"], tatr.sha256(common.OFFICIAL / key.rsplit(":", 1)[0]))

    def test_adopted_pages_are_trial_pages_with_a_grid(self):
        for key in tatr.ADOPTED:
            source, page = key.rsplit(":", 1)
            self.assertIn(int(page), tatr.TRIAL[source])
            self.assertTrue(tatr.adopted_grids(source)[int(page)])

    def test_a_changed_pdf_is_refused(self):
        doc = json.loads(tatr.GRIDS.read_text())
        key = next(iter(tatr.ADOPTED))
        doc["pages"][key]["sha256"] = "0" * 64
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "grids.json"
            path.write_text(json.dumps(doc))
            with self.assertRaises(SystemExit):
                tatr.adopted_grids(key.rsplit(":", 1)[0], path)


class GridAdapter(unittest.TestCase):
    GRID = {"bbox": [0, 0, 300, 60], "rows": [[0, 0, 300, 20], [0, 20, 300, 40], [0, 40, 300, 60]],
            "columns": [[0, 0, 100, 60], [100, 0, 200, 60], [200, 0, 300, 60]],
            "headers": [], "spanning": [[100, 0, 300, 20]]}

    def test_cells_and_spanning_cell(self):
        g = tables.Grid(self.GRID)
        self.assertEqual(len(g.rows), 3)
        self.assertEqual(g.rows[0].cells, [(0, 0, 100, 20), (100, 0, 300, 20), None])
        self.assertEqual(g.rows[1].cells[2], (200, 20, 300, 40))
        words = [(10, 5, 30, 15, "Grade"), (150, 5, 250, 15, "Limits"), (10, 25, 20, 35, "A"),
                 (110, 25, 130, 35, "1"), (210, 25, 230, 35, "2"), (10, 45, 20, 55, "B"), (210, 45, 230, 55, "3")]
        self.assertEqual(tables._cells(g, words), [["Grade", "Limits", ""], ["A", "1", "2"], ["B", "", "3"]])
        self.assertEqual(tables.stray_words(g, words), [])


class AdoptedPages(unittest.TestCase):
    def test_who_1044_microbial_limits_have_their_grades(self):
        rows = {c.ref: c.text for c in parse("who-trs1044-a2-sterile.pdf") if c.kind == "table_row"}
        self.assertEqual(rows["Table 2 B"], "B | 10 | 5 | 5")
        self.assertEqual(rows["Table 2 D"], "D | 200 | 100 | 50")
        text = {c.ref: c.text for c in parse("who-trs1044-a2-sterile.pdf")}["4.31"]
        self.assertNotIn("B 10 5 5", text)

    def test_q3c_class_1_table(self):
        rows = [c.text for c in parse("ich-q3c-r9.pdf", "ICH") if c.kind == "table_row" and c.page_start == 11]
        self.assertIn("Benzene | 2 | Carcinogen", rows)
        self.assertIn("1,1,1-Trichloroethane | 1500 | Environmental hazard", rows)


if __name__ == "__main__":
    unittest.main()
