"""Candidate search (D21): shortlist the clauses of other sources that may map to an obligation or requirement.

  python3 tools/search/candidates.py query "<text>" [--source FILE ...] [-k 10] [--method bm25|embed|fused]
  python3 tools/search/candidates.py evaluate [--draft <session-draft dir>] [--no-embed]

Stage 2 (plan 2.3) matches each obligation of one regulator against the others. Candidate search only proposes
clauses; it decides nothing: every shortlisted pairing is still drafted and verified like any other mapping.
Two rankers are fused by reciprocal rank (RRF_K): BM25 over the clause words (bm25.py) and cosine similarity of
the pinned embedding model (embed.py). Clause embeddings are cached in library/search/ (not in git), keyed by the
model fingerprint and each clause's sha256, so a changed clause or model is re-embedded. Only clauses with an
obligation sentence (tools/parse/obligations.py) are candidates: a heading or a descriptive clause cannot be mapped.

The default ranker is BM25 alone (D32): on the pilot evaluation the embeddings did not measurably help, so by
D21 they stay available (pinned, tested) but are not used unless asked for with --method embed or fused.

`evaluate` measures whether each ranker helps (D21: a model is kept only if it measurably helps), using the
session-pilot mappings: each drafted item is a query against every other pilot source, and that source's pilot
clauses (the same topic, self-inspection) are the relevant ones.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "ai"))
sys.path.insert(0, str(HERE.parent / "parse"))
import bm25  # noqa: E402
import obligations  # noqa: E402

ROOT = HERE.parents[1]
CACHE = ROOT / "library" / "search"
RRF_K = 60
METHODS = ("bm25", "embed", "fused")


def has_obligation(clause):
    """True when the clause states at least one obligation sentence (shall/should/may ...): only those can be
    mapped, so headings and purely descriptive clauses are left out of the candidate pool."""
    return any(obligations.strength(s) for s in obligations.sentences(clause["text"]))


def passage(clause):
    """What is indexed for a clause: its heading path and text."""
    return f"{clause['section']} {clause['ref']}: {clause['text']}" if clause.get("section") else \
        f"{clause['ref']}: {clause['text']}"


class Index:
    """The citable clauses of some sources, searchable by BM25 and (with an embedder) by meaning."""

    def __init__(self, sources, clauses_of, embedder=None, cache=CACHE, obligations_only=True):
        self.rows = [(s, ref, c) for s in sources for ref, c in clauses_of(s).items()
                     if not obligations_only or has_obligation(c)]
        self.texts = [passage(c) for _, _, c in self.rows]
        self.bm25 = bm25.BM25(self.texts)
        self.embedder = embedder
        self.vectors = self._vectors(cache) if embedder else None

    def _vectors(self, cache):
        import numpy as np
        keys = [hashlib.sha256((c["sha256"] + "|" + text).encode()).hexdigest()
                for (_, _, c), text in zip(self.rows, self.texts)]
        known = {}
        path = None
        if cache:
            path = Path(cache) / f"{self.embedder.fingerprint}.npz"
            if path.exists():
                data = np.load(path)
                known = dict(zip(data["keys"].tolist(), data["vectors"]))
        todo = [i for i, k in enumerate(keys) if k not in known]
        if todo:
            fresh = self.embedder.encode([self.texts[i] for i in todo])
            for i, v in zip(todo, fresh):
                known[keys[i]] = v
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                np.savez(path, keys=np.array(list(known)), vectors=np.array(list(known.values())))
        return np.array([known[k] for k in keys])

    def search(self, query, sources=None, k=10, method="bm25"):
        """Top-k clauses as dicts: source, ref, score and the rank under each ranker (1 = best)."""
        if method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        if method != "bm25" and self.embedder is None:
            raise ValueError("this index has no embedder")
        keep = [i for i, (s, _, _) in enumerate(self.rows) if not sources or s in sources]
        ranks = {}
        lexical = self.bm25.scores(query)
        ranks["bm25"] = _ranks(keep, lexical)
        if self.embedder is not None:
            q = self.embedder.encode([query], query=True)[0]
            semantic = (self.vectors @ q).tolist()
            ranks["embed"] = _ranks(keep, semantic)
        if method == "fused":
            score = {i: sum(1 / (RRF_K + r[i]) for r in ranks.values()) for i in keep}
        elif method == "bm25":
            score = {i: lexical[i] for i in keep}
        else:
            score = {i: semantic[i] for i in keep}
        best = sorted(keep, key=lambda i: (-score[i], i))[:k]
        return [{"source": self.rows[i][0], "ref": self.rows[i][1], "score": round(score[i], 6),
                 **{f"{m}_rank": r[i] for m, r in ranks.items()}} for i in best]


def _ranks(keep, scores):
    """Rank (1 = best) of each kept document; ties broken by document order."""
    order = sorted(keep, key=lambda i: (-scores[i], i))
    return {i: n for n, i in enumerate(order, start=1)}


def evaluate(index, mappings, pilot, k=10):
    """Per ranker, two measures over the pilot items:
    - topic: each item queries every other pilot source; relevant are that source's pilot clauses (same topic).
      Reported per target source and overall: hit@k, recall@k, MRR.
    - own clause: each item, a paraphrase, queries its own whole source; the one relevant clause is the clause it
      was drafted from. Reported as hit@1, hit@k and MRR."""
    out = {}
    methods = METHODS if index.embedder is not None else ("bm25",)
    for method in methods:
        per = {}
        own = {"queries": 0, "top1": 0, "topk": 0, "rr": 0.0}
        for m in mappings:
            for target, relevant in pilot.items():
                found = [f["ref"] for f in index.search(m["statement"], [target], k=len(index.rows), method=method)]
                if target == m["source"]:
                    rank = found.index(m["ref"]) + 1
                    own["queries"] += 1
                    own["top1"] += rank == 1
                    own["topk"] += rank <= k
                    own["rr"] += 1 / rank
                    continue
                first = next((r for r, ref in enumerate(found, start=1) if ref in relevant), None)
                row = per.setdefault(target, {"queries": 0, "hits": 0, "recall": 0.0, "rr": 0.0,
                                              "clauses": sum(1 for s, _, _ in index.rows if s == target)})
                row["queries"] += 1
                row["hits"] += first is not None and first <= k
                row["recall"] += len(set(found[:k]) & set(relevant)) / len(relevant)
                row["rr"] += 1 / first if first else 0
        def summary(rows):
            n = sum(r["queries"] for r in rows)
            return {"queries": n, f"hit@{k}": round(sum(r["hits"] for r in rows) / n, 3),
                    f"recall@{k}": round(sum(r["recall"] for r in rows) / n, 3),
                    "mrr": round(sum(r["rr"] for r in rows) / n, 3)}
        out[method] = {
            "topic": {"all": summary(per.values()),
                      "by_target": {t: {"clauses": r["clauses"], **summary([r])} for t, r in sorted(per.items())}},
            "own_clause": {"queries": own["queries"], "hit@1": round(own["top1"] / own["queries"], 3),
                           f"hit@{k}": round(own["topk"] / own["queries"], 3),
                           "mrr": round(own["rr"] / own["queries"], 3)}}
    return out


def _default_draft():
    runs = sorted((ROOT / "library" / "ai-runs").glob("*-session-draft"))
    if not runs:
        raise SystemExit("no session-draft run in library/ai-runs")
    return runs[0]


def main():
    import layer1
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["query", "evaluate"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--source", action="append", help="limit to these source files (repeatable)")
    ap.add_argument("-k", type=int, default=10)
    ap.add_argument("--method", choices=METHODS, default="bm25")
    ap.add_argument("--draft", help="evaluate: session-draft run whose mappings are the queries")
    ap.add_argument("--no-embed", action="store_true", help="evaluate: BM25 only (no model needed)")
    a = ap.parse_args()
    embedder = None
    if (a.command == "query" and a.method != "bm25") or (a.command == "evaluate" and not a.no_embed):
        import embed
        embedder = embed.Embedder()
    if a.command == "query":
        if not a.text:
            ap.error("query needs the text")
        sources = a.source or sorted(layer1.catalog())
        index = Index(sources, layer1.clauses_of, embedder)
        print(json.dumps(index.search(a.text, a.source, a.k, a.method), indent=1))
    else:
        import pilot
        import runner
        mappings = runner.read_jsonl(Path(a.draft or _default_draft()) / "mappings.jsonl")
        index = Index(list(pilot.PILOT), layer1.clauses_of, embedder)
        print(json.dumps(evaluate(index, mappings, pilot.PILOT, a.k), indent=1))


if __name__ == "__main__":
    main()
