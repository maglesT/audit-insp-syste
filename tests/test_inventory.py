import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inventory  # noqa: E402


class SourcesIntact(unittest.TestCase):
    def test_all_catalogued_sources_present_and_fingerprints_match(self):
        self.assertEqual(inventory.problems(), [])


class FingerprintCheckDetectsTampering(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.official = self.tmp / "official"
        shutil.copytree(inventory.OFFICIAL, self.official)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_changed_source_is_reported(self):
        target = self.official / "ecfr-21cfr211-2026-10-27.xml"
        target.write_bytes(target.read_bytes().replace(b"shall", b"should", 1))
        found = inventory.problems(official=self.official)
        self.assertIn("sha256 changed, re-verify all items citing: ecfr-21cfr211-2026-10-27.xml", found)

    def test_uncatalogued_and_missing_files_are_reported(self):
        (self.official / "stray.pdf").write_bytes(b"x")
        (self.official / "ich-q10.pdf").unlink()
        found = inventory.problems(official=self.official)
        self.assertIn("uncatalogued file: stray.pdf", found)
        self.assertIn("catalogued file missing: ich-q10.pdf", found)


if __name__ == "__main__":
    unittest.main()
