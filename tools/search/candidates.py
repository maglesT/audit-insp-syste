"""Candidate search (D21): shortlist the clauses of other sources that may map to an obligation or requirement.

  python3 tools/search/candidates.py query "<text>" [--source FILE ...] [-k 10] [--method bm25|embed|fused]
  python3 tools/search/candidates.py evaluate [--draft <session-draft dir>] [--no-embed]

Stage 2 (plan 2.3) matches each obligation of one regulator against the others. Candidate search only proposes
clauses; it decides nothing: every shortlisted pairing is still drafted and verified like any other mapping.
Two rankers are fused by reciprocal rank (RRF_K): BM25 over the clause words (bm25.py) and cosine similarity of
the pinned embedding model (embed.py). A clause longer than one model window is embedded in overlapping word
windows and scores by its best window. Embeddings are cached in library/search/ (not in git), keyed by the
model fingerprint (which covers the encoding settings), the window size and each window's text and clause sha256,
so a changed clause, model or setting is re-embedded. Only clauses with an obligation sentence
(tools/parse/obligations.py) are candidates: a heading or a descriptive clause cannot be mapped.

The default ranker is BM25 alone (D32): on the pilot evaluation the embeddings did not measurably help, so by
D21 they stay available (pinned, tested) but are not used unless asked for with --method embed or fused.

`evaluate` measures whether each ranker helps (D21: a model is kept only if it measurably helps), using the
session-pilot mappings: each drafted item is a query against every other pilot source, and that source's pilot
clauses (the same topic, self-inspection) are the relevant ones. A target with no more candidates than k, or
whose candidates are all relevant, cannot tell rankers apart; it is reported but left out of "informative".
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
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
WINDOW, OVERLAP = 250, 50                   # words per embedding window: well inside the model's 512 tokens


def has_obligation(clause):
    """True when the clause states at least one obligation sentence (shall/should/may ...): only those can be
    mapped, so headings and purely descriptive clauses are left out of the candidate pool."""
    return any(obligations.strength(s) for s in obligations.sentences(clause["text"]))


def passage(clause):
    """What is indexed for a clause: its text. The section field holds structural labels ("Part I", "Chapter 9")
    and the text already starts with the clause number, so neither is added."""
    return clause["text"]


def windows(text, size=WINDOW, overlap=OVERLAP):
    """Overlapping word windows of a passage; one window when it is short."""
    words = text.split()
    if len(words) <= size:
        return [text]
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words) - overlap, step)]


class Index:
    """The citable clauses of some sources, searchable by BM25 and (with an embedder) by meaning."""

    def __init__(self, sources, clauses_of, embedder=None, cache=CACHE, obligations_only=True):
        self.rows = [(s, ref, c) for s in sources for ref, c in clauses_of(s).items()
                     if not obligations_only or has_obligation(c)]
        self.texts = [passage(c) for _, _, c in self.rows]
        self.bm25 = bm25.BM25(self.texts)
        self.embedder = embedder
        self.vectors, self.owner = self._vectors(cache) if embedder else (None, None)

    def _vectors(self, cache):
        """(window vectors, row number of each window)."""
        import numpy as np
        chunks, owner, keys = [], [], []
        for n, ((_, _, c), text) in enumerate(zip(self.rows, self.texts)):
            for w in windows(text):
                chunks.append(w)
                owner.append(n)
                keys.append(hashlib.sha256((c["sha256"] + "|" + w).encode()).hexdigest())
        known, path = {}, None
        if cache:
            path = Path(cache) / f"{self.embedder.fingerprint}-w{WINDOW}-{OVERLAP}.npz"
            try:
                with np.load(path) as data:
                    known = dict(zip(data["keys"].tolist(), data["vectors"]))
            except (OSError, ValueError, KeyError):
                known = {}                          # missing or unreadable cache: start again
        todo = [i for i, k in enumerate(keys) if k not in known]
        if todo:
            for i, v in zip(todo, self.embedder.encode([chunks[i] for i in todo])):
                known[keys[i]] = v
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                fd, tmp = tempfile.mkstemp(suffix=".npz", dir=path.parent)
                os.close(fd)
                np.savez(tmp, keys=np.array(list(known)), vectors=np.array(list(known.values())))
                os.replace(tmp, path)
        if not keys:
            return np.zeros((0, 0)), np.zeros(0, dtype=int)
        return np.array([known[k] for k in keys]), np.array(owner)

    def _semantic(self, query):
        """One cosine score per row: the best of its windows."""
        import numpy as np
        if not self.rows:
            return []
        q = self.embedder.encode([query], query=True)[0]
        per_window = self.vectors @ q
        best = np.full(len(self.rows), -np.inf)
        np.maximum.at(best, self.owner, per_window)
        return best.tolist()

    def search(self, query, sources=None, k=10, method="bm25"):
        """Top-k clauses as dicts: source, ref, score and the rank under each ranker used (1 = best)."""
        if method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        if method != "bm25" and self.embedder is None:
            raise ValueError("this index has no embedder")
        keep = [i for i, (s, _, _) in enumerate(self.rows) if not sources or s in sources]
        lexical = self.bm25.scores(query)
        ranks = {"bm25": _ranks(keep, lexical)}
        if method != "bm25":
            semantic = self._semantic(query)
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


def _share(x, n):
    return round(x / n, 3) if n else None


def evaluate(index, mappings, pilot, k=10):
    """Per ranker, two measures over the pilot items:
    - topic: each item queries every other pilot source; relevant are that source's pilot clauses (same topic).
      Reported per target, over all targets, and over the informative targets only (more candidates than k, not
      all of them relevant): hit@k, recall@k, MRR.
    - own clause: each item queries its own whole source; the one relevant clause is the clause it was drafted
      from (hit@1, hit@k, MRR). The item reuses its clause's words, so this measure favours BM25 by design.
    An item whose clause is not a candidate (no obligation sentence detected) counts as a miss."""
    out = {}
    methods = METHODS if index.embedder is not None else ("bm25",)
    candidates = {}
    for s, ref, _ in index.rows:
        candidates.setdefault(s, set()).add(ref)
    for method in methods:
        per = {}
        own = {"queries": 0, "top1": 0, "topk": 0, "rr": 0.0, "not_indexed": 0}
        for m in mappings:
            for target, relevant in pilot.items():
                pool = candidates.get(target, set())
                found = [f["ref"] for f in index.search(m["statement"], [target], k=len(index.rows), method=method)]
                if target == m["source"]:
                    own["queries"] += 1
                    if m["ref"] not in found:
                        own["not_indexed"] += 1
                        continue
                    rank = found.index(m["ref"]) + 1
                    own["top1"] += rank == 1
                    own["topk"] += rank <= k
                    own["rr"] += 1 / rank
                    continue
                relevant = set(relevant) & pool
                if not relevant:                    # nothing to find in this target
                    continue
                row = per.setdefault(target, {"queries": 0, "hits": 0, "recall": 0.0, "rr": 0.0,
                                              "clauses": len(pool),
                                              "informative": len(pool) > k and bool(pool - relevant)})
                row["queries"] += 1
                first = next((r for r, ref in enumerate(found, start=1) if ref in relevant), None)
                row["hits"] += first is not None and first <= k
                row["recall"] += len(set(found[:k]) & relevant) / len(relevant)
                row["rr"] += 1 / first if first else 0

        def summary(rows):
            n = sum(r["queries"] for r in rows)
            return {"queries": n, f"hit@{k}": _share(sum(r["hits"] for r in rows), n),
                    f"recall@{k}": _share(sum(r["recall"] for r in rows), n),
                    "mrr": _share(sum(r["rr"] for r in rows), n)}
        n = own["queries"]
        out[method] = {
            "topic": {"all": summary(per.values()),
                      "informative": summary([r for r in per.values() if r["informative"]]),
                      "by_target": {t: {"clauses": r["clauses"], "informative": r["informative"], **summary([r])}
                                    for t, r in sorted(per.items())}},
            "own_clause": {"queries": n, "not_indexed": own["not_indexed"], "hit@1": _share(own["top1"], n),
                           **({f"hit@{k}": _share(own["topk"], n)} if k != 1 else {}),
                           "mrr": _share(own["rr"], n)}}
    return out


def _default_draft():
    runs = sorted((ROOT / "library" / "ai-runs").glob("*-session-draft"))
    if not runs:
        raise SystemExit("no session-draft run in library/ai-runs")
    if len(runs) > 1:
        raise SystemExit("several session-draft runs: name one with --draft")
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
    if a.command == "query" and not a.text:
        ap.error("query needs the text")
    embedder = None
    if (a.command == "query" and a.method != "bm25") or (a.command == "evaluate" and not a.no_embed):
        import embed
        embedder = embed.Embedder()
    if a.command == "query":
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
