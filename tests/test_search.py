import hashlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "search"))
import bm25  # noqa: E402
import candidates  # noqa: E402
import embed  # noqa: E402


def clause(ref, text, section=""):
    return {"ref": ref, "text": text, "section": section, "sha256": hashlib.sha256(text.encode()).hexdigest()}


SOURCES = {
    "a.pdf": {"1": clause("1", "Self inspections should be conducted regularly to monitor GMP compliance."),
              "2": clause("2", "Packaging materials should conform to established specifications."),
              "3": clause("3", "Self Inspection")},                                 # a heading: no obligation
    "b.pdf": {"1": clause("1", "Internal audits should be performed in accordance with an approved schedule."),
              "2": clause("2", "Audit findings and corrective actions should be documented."),
              "3": clause("3", "Labels must be stored securely.")},
}


class FakeEmbedder:
    """Deterministic stand-in for the model: a hashed bag of stems, so related words meet."""
    fingerprint = "fake@0"

    def __init__(self):
        self.encoded = 0

    def encode(self, texts, query=False, batch=32):
        self.encoded += len(texts)
        out = np.zeros((len(texts), 64))
        for i, t in enumerate(texts):
            for w in bm25.tokens(t):
                out[i, int(hashlib.md5(w.encode()).hexdigest(), 16) % 64] += 1
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)


class Bm25(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(bm25.tokens("The inspections, inspected and inspecting!"), ["inspect"] * 3)
        self.assertEqual(bm25.tokens("Facilities and supplies"), ["facility", "supply"])
        self.assertEqual(bm25.tokens("shall be in a"), [])

    def test_stem_joins_inflections(self):
        groups = [("procedure", "procedures"), ("manufacture", "manufactured", "manufacturing"),
                  ("process", "processes"), ("require", "required", "requires"), ("change", "changes"),
                  ("premise", "premises"), ("sample", "samples"), ("measure", "measures"),
                  ("validate", "validated", "validation"), ("control", "controlled", "controls"),
                  ("deviate", "deviation", "deviations"), ("operate", "operation", "operating"),
                  ("document", "documented", "documentation"), ("supply", "supplies", "supplied")]
        for group in groups:
            self.assertEqual(len({bm25.stem(w) for w in group}), 1, group)
        for word in ("status", "analysis", "process"):            # not plurals
            self.assertEqual(bm25.stem(word), word)
        self.assertNotEqual(bm25.stem("deviation"), "devi")

    def test_ranking(self):
        index = bm25.BM25(["self inspection programme", "packaging specifications", "inspection of packaging"])
        scores = index.scores("self inspection")
        self.assertGreater(scores[0], scores[2])
        self.assertGreater(scores[2], scores[1])
        self.assertEqual(scores[1], 0)
        self.assertEqual(index.scores("the of and"), [0, 0, 0])


class Search(unittest.TestCase):
    def setUp(self):
        self.cache = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.cache)

    def test_only_obligation_clauses_are_candidates(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, cache=None)
        self.assertNotIn(("a.pdf", "3"), [(s, r) for s, r, _ in index.rows])
        full = candidates.Index(list(SOURCES), SOURCES.get, cache=None, obligations_only=False)
        self.assertEqual(len(full.rows), 6)

    def test_bm25_search_and_source_filter(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, cache=None)
        top = index.search("conduct self inspections", k=2)
        self.assertEqual((top[0]["source"], top[0]["ref"], top[0]["bm25_rank"]), ("a.pdf", "1", 1))
        only_b = index.search("audit findings corrective actions", sources=["b.pdf"], k=5)
        self.assertEqual({r["source"] for r in only_b}, {"b.pdf"})
        self.assertEqual(only_b[0]["ref"], "2")
        with self.assertRaises(ValueError):
            index.search("x", method="embed")                 # no embedder
        with self.assertRaises(ValueError):
            index.search("x", method="nonsense")

    def test_fused_is_reciprocal_rank(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, FakeEmbedder(), cache=None)
        found = index.search("documented corrective actions after audits", k=5, method="fused")
        for f in found:
            self.assertAlmostEqual(f["score"], round(1 / (60 + f["bm25_rank"]) + 1 / (60 + f["embed_rank"]), 6))
        self.assertEqual([f["score"] for f in found], sorted((f["score"] for f in found), reverse=True))
        self.assertEqual(index.search("documented corrective actions", k=1, method="embed")[0]["ref"], "2")

    def test_embedding_cache(self):
        first = FakeEmbedder()
        candidates.Index(list(SOURCES), SOURCES.get, first, cache=self.cache)
        self.assertEqual(first.encoded, 5)
        again = FakeEmbedder()
        candidates.Index(list(SOURCES), SOURCES.get, again, cache=self.cache)
        self.assertEqual(again.encoded, 0)                    # all from the cache
        changed = {**SOURCES, "b.pdf": {**SOURCES["b.pdf"], "3": clause("3", "Labels must be locked away.")}}
        third = FakeEmbedder()
        candidates.Index(list(changed), changed.get, third, cache=self.cache)
        self.assertEqual(third.encoded, 1)                    # only the changed clause
        other = FakeEmbedder()
        other.fingerprint = "fake@1"                          # another model or setting: nothing reused
        candidates.Index(list(SOURCES), SOURCES.get, other, cache=self.cache)
        self.assertEqual(other.encoded, 5)
        broken = self.cache / "fake@0-w250-50.npz"
        broken.write_bytes(b"not a zip")                      # an unreadable cache is rebuilt, not fatal
        fresh = FakeEmbedder()
        candidates.Index(list(SOURCES), SOURCES.get, fresh, cache=self.cache)
        self.assertEqual(fresh.encoded, 5)

    def test_long_clauses_are_windowed(self):
        long_text = "Records should be kept. " + " ".join(f"filler{i}" for i in range(400)) + \
            " Self inspections must be conducted."
        self.assertEqual(len(candidates.windows(long_text)), 2)
        self.assertEqual(candidates.windows("short text"), ["short text"])
        sources = {"x.pdf": {"1": clause("1", long_text), "2": clause("2", "Labels must be stored securely.")}}
        index = candidates.Index(["x.pdf"], sources.get, FakeEmbedder(), cache=None)
        self.assertEqual(len(index.owner), 3)                 # two windows for clause 1, one for clause 2
        self.assertEqual(index.search("conduct self inspections", k=1, method="embed")[0]["ref"], "1")

    def test_empty_index(self):
        index = candidates.Index(["x"], {"x": {}}.get, FakeEmbedder(), cache=None)
        for method in candidates.METHODS:
            self.assertEqual(index.search("anything", method=method), [])

    def test_bm25_search_does_not_embed_the_query(self):
        e = FakeEmbedder()
        index = candidates.Index(list(SOURCES), SOURCES.get, e, cache=None)
        before = e.encoded
        found = index.search("self inspections", k=1)
        self.assertEqual(e.encoded, before)
        self.assertNotIn("embed_rank", found[0])

    def test_evaluate(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, FakeEmbedder(), cache=None)
        mappings = [{"source": "a.pdf", "ref": "1", "statement": "Carry out self inspections."},
                    {"source": "b.pdf", "ref": "2", "statement": "Document audit findings and corrective actions."}]
        pilot = {"a.pdf": ["1"], "b.pdf": ["1", "2"]}
        out = candidates.evaluate(index, mappings, pilot, k=1)
        self.assertEqual(set(out), {"bm25", "embed", "fused"})
        b = out["bm25"]
        self.assertEqual(b["own_clause"], {"queries": 2, "not_indexed": 0, "hit@1": 1.0, "mrr": 1.0})
        k2 = candidates.evaluate(index, mappings, pilot, k=2)["bm25"]["own_clause"]
        self.assertEqual((k2["hit@1"], k2["hit@2"]), (1.0, 1.0))
        self.assertEqual(b["topic"]["all"]["queries"], 2)
        self.assertEqual(set(b["topic"]["by_target"]), {"a.pdf", "b.pdf"})
        self.assertEqual(b["topic"]["by_target"]["a.pdf"]["hit@1"], 1.0)
        bm_only = candidates.evaluate(candidates.Index(list(SOURCES), SOURCES.get, cache=None), mappings, pilot)
        self.assertEqual(set(bm_only), {"bm25"})

    def test_evaluate_flags_uninformative_targets(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, cache=None)
        mappings = [{"source": "b.pdf", "ref": "2", "statement": "Document audit findings."}]
        out = candidates.evaluate(index, mappings, {"a.pdf": ["1"], "b.pdf": ["2"]}, k=10)["bm25"]["topic"]
        self.assertFalse(out["by_target"]["a.pdf"]["informative"])        # 2 candidates <= k
        self.assertEqual(out["informative"]["queries"], 0)
        self.assertIsNone(out["informative"]["hit@10"])
        out = candidates.evaluate(index, mappings, {"a.pdf": ["1"], "b.pdf": ["2"]}, k=1)["bm25"]["topic"]
        self.assertTrue(out["by_target"]["a.pdf"]["informative"])

    def test_evaluate_edge_cases(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, cache=None)
        heading = [{"source": "a.pdf", "ref": "3", "statement": "Self inspection"}]   # not a candidate
        own = candidates.evaluate(index, heading, {"a.pdf": ["1"]})["bm25"]["own_clause"]
        self.assertEqual((own["queries"], own["not_indexed"], own["hit@1"]), (1, 1, 0.0))
        empty = candidates.evaluate(index, [], {"a.pdf": ["1"]})["bm25"]
        self.assertEqual((empty["own_clause"]["mrr"], empty["topic"]["all"]["mrr"]), (None, None))

    def test_cli_needs_query_text(self):
        import unittest.mock
        with self.assertRaises(SystemExit), unittest.mock.patch.object(sys, "argv", ["candidates.py", "query"]), \
                unittest.mock.patch("sys.stderr"):
            candidates.main()


class Model(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.files = {"onnx/model.onnx": b"weights", "tokenizer.json": b"{}"}
        self.pin = {**embed.MODEL, "name": "test", "files": {n: hashlib.sha256(b).hexdigest()
                                                           for n, b in self.files.items()}}

    def opener(self, payloads):
        def open_(url, timeout=None):
            self.assertIsNotNone(timeout)
            name = url.split(f"/resolve/{self.pin['revision']}/", 1)[1]
            return io.BytesIO(payloads[name])
        return open_

    def test_pins_are_exact(self):
        self.assertRegex(embed.MODEL["revision"], r"^[0-9a-f]{40}$")
        for digest in embed.MODEL["files"].values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_fetch_verifies_and_refuses_a_mismatch(self):
        self.assertEqual(len(embed.check(self.pin, self.dir)), 2)
        embed.fetch(self.pin, self.dir, opener=self.opener(self.files))
        self.assertEqual(embed.check(self.pin, self.dir), [])
        (self.dir / "tokenizer.json").write_bytes(b"tampered")
        self.assertEqual(embed.check(self.pin, self.dir), ["tokenizer.json: sha256 does not match the pin"])
        bad = {**self.files, "tokenizer.json": b"not the pinned file"}
        with self.assertRaises(SystemExit):
            embed.fetch(self.pin, self.dir, opener=self.opener(bad))
        self.assertFalse((self.dir / "tokenizer.json.part").exists())

    def test_interrupted_download_leaves_nothing(self):
        class Broken(io.BytesIO):
            def read(self, n=-1):
                raise ConnectionError("dropped")

        with self.assertRaises(ConnectionError):
            embed.fetch(self.pin, self.dir, opener=lambda url, timeout=None: Broken())
        self.assertEqual(list(self.dir.iterdir()), [])

    def test_fingerprint_covers_settings(self):
        a = object.__new__(embed.Embedder)
        a.model = embed.MODEL
        b = object.__new__(embed.Embedder)
        b.model = {**embed.MODEL, "max_tokens": 256}
        self.assertNotEqual(a.fingerprint, b.fingerprint)
        self.assertTrue(a.fingerprint.startswith("bge-small-en-v1.5@5c38ec7c405e-"))

    def test_embedder_needs_the_model(self):
        with self.assertRaises(SystemExit):
            embed.Embedder({**self.pin, "name": "absent"})

    @unittest.skipUnless(embed.available(), "embedding model not fetched (python3 tools/search/embed.py fetch)")
    def test_real_model(self):
        e = embed.Embedder()
        q = e.encode(["Carry out self inspections regularly."], query=True)
        p = e.encode(["Self inspections should be conducted to monitor GMP.", "Labels must be stored securely."])
        self.assertEqual(p.shape, (2, 384))
        self.assertAlmostEqual(float(np.linalg.norm(p[0])), 1.0, places=5)
        scores = (p @ q.T).ravel()
        self.assertGreater(scores[0], scores[1])


if __name__ == "__main__":
    unittest.main()
