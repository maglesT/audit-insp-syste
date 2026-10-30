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

    def test_evaluate(self):
        index = candidates.Index(list(SOURCES), SOURCES.get, FakeEmbedder(), cache=None)
        mappings = [{"source": "a.pdf", "ref": "1", "statement": "Carry out self inspections."},
                    {"source": "b.pdf", "ref": "2", "statement": "Document audit findings and corrective actions."}]
        pilot = {"a.pdf": ["1"], "b.pdf": ["1", "2"]}
        out = candidates.evaluate(index, mappings, pilot, k=1)
        self.assertEqual(set(out), {"bm25", "embed", "fused"})
        b = out["bm25"]
        self.assertEqual(b["own_clause"], {"queries": 2, "hit@1": 1.0, "mrr": 1.0})      # k=1: one key, no double count
        k2 = candidates.evaluate(index, mappings, pilot, k=2)["bm25"]["own_clause"]
        self.assertEqual((k2["hit@1"], k2["hit@2"]), (1.0, 1.0))
        self.assertEqual(b["topic"]["all"]["queries"], 2)
        self.assertEqual(set(b["topic"]["by_target"]), {"a.pdf", "b.pdf"})
        self.assertEqual(b["topic"]["by_target"]["a.pdf"]["hit@1"], 1.0)
        bm_only = candidates.evaluate(candidates.Index(list(SOURCES), SOURCES.get, cache=None), mappings, pilot)
        self.assertEqual(set(bm_only), {"bm25"})


class Model(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.files = {"onnx/model.onnx": b"weights", "tokenizer.json": b"{}"}
        self.pin = {**embed.MODEL, "name": "test", "files": {n: hashlib.sha256(b).hexdigest()
                                                           for n, b in self.files.items()}}

    def opener(self, payloads):
        def open_(url):
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
