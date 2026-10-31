"""review.py import-artifact: the owner's review-page decisions into library/review/decisions.jsonl (D47)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "fda"))
import review  # noqa: E402
import xmlprofile as X  # noqa: E402

SRC = "ecfr-21cfr211-2026-10-27.xml"
ITEM = {"statement": "Withhold each lot of components from use until released by the quality control unit.",
        "quote": "Each lot of components, drug product containers, and closures shall be withheld from use until the "
                 "lot has been sampled, tested, or examined, as appropriate, and released for use by the quality "
                 "control unit.",
        "clause_number": "211.84(a)", "strength": "mandatory", "plant_types": ["OSD"], "numbers": [],
        "condition": "", "topic": "MAT.TEST", "source": SRC}


class ImportArtifact(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.runs, self.dec = base / "runs", base / "decisions.jsonl"
        self.run = self.runs / "20261031T000000Z-xml-draft"
        self.run.mkdir(parents=True)
        items = [dict(ITEM, id="i"), dict(ITEM, id="j", statement="Another statement.")]
        (self.run / "items.jsonl").write_text("\n".join(json.dumps(i) for i in items))
        (self.run / "route.json").write_text(json.dumps({"route": {"i": "review", "j": "review"}, "hashes": {}}))
        self.h = {i["id"]: X.item_hash(i) for i in items}

    def tearDown(self):
        self.tmp.cleanup()

    def rec(self, **kw):
        base = {"id": "i", "run": self.run.name, "item_hash": self.h["i"], "decision": "correct", "by": "Owner",
                "note": "", "at": "2026-10-30T12:00:00Z"}
        return {**base, **kw}

    def export(self, rows, form="list"):
        f = Path(self.tmp.name) / "export.json"
        if form == "docs":
            f.write_text(json.dumps({"docs": [{"id": f"{r['run']}+{r['id']}", "data": r, "version": 1}
                                              for r in rows]}))
        elif form == "lines":
            f.write_text("\n".join(json.dumps({"id": "x", "data": r}) for r in rows))
        else:
            f.write_text(json.dumps(rows))
        return f

    def imp(self, rows, form="list"):
        return review.import_artifact(self.export(rows, form), path=self.dec, runs=self.runs)

    def test_imports_with_original_time_and_ships(self):
        out = self.imp([self.rec(), self.rec(id="j", item_hash=self.h["j"], decision="fix",
                                             statement="Corrected.", at="2026-10-30T11:00:00+00:00")], form="docs")
        self.assertEqual(len(out["imported"]), 2)
        lines = [json.loads(ln) for ln in self.dec.read_text().splitlines()]
        self.assertEqual([d["at"] for d in lines], ["2026-10-30T11:00:00+00:00", "2026-10-30T12:00:00Z"])
        self.assertEqual(lines[0]["statement"], "Corrected.")
        self.assertTrue(all(d["via"] == "review page" for d in lines))
        self.assertEqual(sorted(review.shipped(self.run, self.dec)), ["i", "j"])

    def test_json_lines_export_and_no_duplicates(self):
        self.imp([self.rec()], form="lines")
        out = self.imp([self.rec()], form="lines")
        self.assertEqual(out["imported"], [])
        self.assertEqual(len(self.dec.read_text().splitlines()), 1)

    def test_run_and_hash_rules(self):
        out = self.imp([self.rec(item_hash="0" * 16), self.rec(run="no-such-run"), self.rec(id="zz"),
                        self.rec(run="../x"), self.rec(decision="maybe"), self.rec(decision="fix"),
                        self.rec(by=" "), self.rec(at="yesterday"), self.rec(at=None)])
        self.assertEqual(out["imported"], [])
        self.assertEqual(len(out["skipped"]), 9)
        self.assertFalse(self.dec.exists())
        self.assertEqual(review.shipped(self.run, self.dec), [])

    def test_wrong_corrected_quote_is_refused(self):
        out = self.imp([self.rec(decision="fix", statement="X.", quote="words that are not in the paragraph")])
        self.assertEqual(out["skipped"][0][1], "the corrected quote is not in the source text")

    def test_latest_by_time_not_by_file_order(self):
        self.imp([self.rec(decision="reject", at="2026-10-30T13:00:00Z")])
        self.imp([self.rec(decision="correct", at="2026-10-30T12:00:00Z")])      # older, imported later
        self.assertEqual(review.decisions(self.dec, self.run, review.load(self.run)[1])["i"]["decision"], "reject")
        self.assertEqual(review.shipped(self.run, self.dec), [])
        self.imp([self.rec(decision="correct", at="2026-10-30T14:00:00Z")])
        self.assertEqual(review.shipped(self.run, self.dec), ["i"])

    def test_times_must_be_full_with_zone_and_not_future(self):
        out = self.imp([self.rec(at="2026-10-31"), self.rec(at="2026-W44-6"), self.rec(at="2026-10-30T12:00:00"),
                        self.rec(at="9999-12-31T00:00:00Z")])
        self.assertEqual(out["imported"], [])
        self.assertEqual(len(out["skipped"]), 4)
        self.assertEqual(len(self.imp([self.rec(at="2026-10-30T14:00:00.5+02:00")])["imported"]), 1)

    def test_malformed_exports_are_skipped_not_crashing(self):
        for bad in ("[1, null]", '{"docs": {"a": 1}}', "5"):
            f = Path(self.tmp.name) / "bad.json"
            f.write_text(bad)
            out = review.import_artifact(f, path=self.dec, runs=self.runs)
            self.assertEqual(out["imported"], [])
            self.assertTrue(out["skipped"])
        f = Path(self.tmp.name) / "lines.json"
        f.write_text(json.dumps(self.rec()) + "\n{not json\n")
        out = review.import_artifact(f, path=self.dec, runs=self.runs)
        self.assertEqual((len(out["imported"]), len(out["skipped"])), (1, 1))
        out = self.imp([self.rec(decision="fix", statement=5), self.rec(note=["x"]), self.rec(quote=5)])
        self.assertEqual((len(out["imported"]), len(out["skipped"])), (0, 3))

    def test_duplicates_are_reported_and_same_instant_is_one(self):
        self.imp([self.rec()])
        out = self.imp([self.rec(at="2026-10-30T12:00:00+00:00"),
                        self.rec(decision="fix", statement="One."), self.rec(decision="fix", statement="Two.")])
        self.assertEqual(len(out["duplicates"]), 1)
        self.assertEqual(len(out["imported"]), 2)

    def test_a_record_without_time_does_not_crash_shipped(self):
        self.dec.write_text(json.dumps({"id": "i", "run": self.run.name, "item_hash": self.h["i"],
                                        "decision": "correct", "by": "x"}) + "\n")
        self.assertEqual(review.shipped(self.run, self.dec), ["i"])


if __name__ == "__main__":
    unittest.main()
