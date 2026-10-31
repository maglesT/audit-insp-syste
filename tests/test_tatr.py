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
        for page in doc["pages"].values():                   # each page names the run (pins) that made it
            made = doc["runs"][page["run"]]["models"]
            for name, pin in tatr.PINS.items():
                self.assertEqual(made[name]["revision"], pin["revision"])
                self.assertEqual(made[name]["files"], pin["files"])
        trial = {f"{s}:{p}" for s, pages in tatr.TRIAL.items() for p in pages}
        self.assertEqual(set(doc["pages"]), trial)
        for key in doc["pages"]:
            self.assertEqual(doc["pages"][key]["sha256"], tatr.sha256(common.OFFICIAL / key.rsplit(":", 1)[0]))

    def test_adopted_pages_are_trial_pages_with_a_grid(self):
        for key in tatr.ADOPTED:
            source, page = key.rsplit(":", 1)
            self.assertIn(int(page), tatr.TRIAL[source])
            self.assertTrue(tatr.adopted_grids(source)[int(page)])

    def test_an_adopted_page_without_a_grid_is_refused(self):
        import tempfile
        key = next(iter(tatr.ADOPTED))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "grids.json"
            path.write_text(json.dumps({"runs": [], "pages": {}}))
            with self.assertRaises(SystemExit):
                tatr.adopted_grids(key.rsplit(":", 1)[0], path)

    def test_parsing_never_loads_the_model(self):
        import subprocess
        code = ("import sys; sys.path.insert(0, 'tools/parse'); import run, common; "
                "run.parser_for({'file': 'ich-q3c-r9.pdf', 'regulator': 'ICH'})(common.OFFICIAL / 'ich-q3c-r9.pdf'); "
                "print(any(m in sys.modules for m in ('torch', 'transformers', 'timm')))")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                             cwd=Path(__file__).resolve().parents[1]).stdout.strip()
        self.assertEqual(out, "False")

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

    def test_span_takes_whole_cells_only(self):
        # a span box that reaches a little into the next column: only the cells whose centre it covers join it
        grid = dict(self.GRID, spanning=[[100, 0, 240, 20]])
        g = tables.Grid(grid)
        self.assertEqual(g.rows[0].cells, [(0, 0, 100, 20), (100, 0, 200, 20), (200, 0, 300, 20)])
        words = [(230, 5, 238, 15, "x")]
        self.assertEqual(tables.twice_words(g, words), [])
        # a span over two rows of one column
        g = tables.Grid(dict(self.GRID, spanning=[[0, 20, 100, 60]]))
        self.assertEqual(g.rows[1].cells[0], (0, 20, 100, 60))
        self.assertIsNone(g.rows[2].cells[0])

    def test_outline_holds_every_cell(self):
        g = tables.Grid(dict(self.GRID, bbox=[2, 3, 298, 58]))
        self.assertEqual(g.bbox, (0, 0, 300, 60))

    def test_twice_words(self):
        g = tables.Grid(self.GRID)
        g.rows[0].cells[2] = (150, 0, 300, 20)               # overlaps cell 2 of row 1
        self.assertEqual([w[4] for w in tables.twice_words(g, [(160, 5, 170, 15, "y")])], ["y"])


class AdoptedPages(unittest.TestCase):
    def test_a_trial_page_not_adopted_keeps_the_pdfplumber_grid(self):
        self.assertNotIn("who-trs1044-a2-sterile.pdf:17", tatr.ADOPTED)
        rows = {c.ref: c.text for c in parse("who-trs1044-a2-sterile.pdf") if c.kind == "table_row"}
        self.assertEqual(rows["Table 1 C"], "C | 352 000 | 3 520 000 | 2 930 | 29 300")

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
