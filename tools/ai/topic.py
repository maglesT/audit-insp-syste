"""Topic units (S3): the clauses of one topic across every pilot source, chosen by rule, not by hand.

  python3 tools/ai/topic.py list [--topic self-inspection]      # units, twins and counts per regulator
  python3 tools/ai/topic.py write [--topic self-inspection]     # library/topics/<topic>.json

A clause is a unit of the topic when it has an obligation sentence (tools/parse/obligations.py) and
  - its text names the topic (TOPICS[topic]["text"]): by clause, not by sentence, so twin texts that the sentence
    splitter cuts differently are chosen alike; or
  - it lies under a heading clause that names the topic (TOPICS[topic]["heading"]): "Chapter 9 9.1" under
    "Chapter 9", "Part XII 2.4.2" under "Part XII 2.4", "2.41" under ICH Q7's "2.4"; or
  - it lies in a chapter most of whose obligation clauses name the topic (Schedule M "Part I 10.8.2", WHO 8.9:
    suppliers' audits inside the self-inspection chapter, which has no heading clause of its own).
Only pilot sources with priority must or should count (D9: reference texts are tracked, not turned into items),
and only clause, principle, table row and unnumbered kinds (not contents lines or whole sections). A clause longer
than MAX_CHARS is a parse blob (a drug price list, a whole compliance-program objective) that only mentions the
topic; it is listed under "too_long" for the parse flags, not drafted.

Twins (D36): a unit whose text, without its leading number, is the same after normalising as a unit of another
source is drafted once. The drafted one is the first by CORE_ORDER (plan 2.3: the cores first), and its twins
take its mappings, each quote still checked word for word against the twin's own clause (Layer 1 rule 1). Near
twins that differ in any word ("should" in ICH Q7, "shall" in Schedule M Part XII) are drafted on their own.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "library"))
sys.path.insert(0, str(HERE.parent / "parse"))
import obligations  # noqa: E402
from common import normalise  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / "library" / "topics"
KINDS = ("clause", "principle", "table_row", "unnumbered")
MAX_CHARS = 6000
CORE_ORDER = ("EU", "PICS", "FDA", "WHO", "EMA", "ICH", "INDIA")
TOPICS = {
    "self-inspection": {
        "text": r"self[\s-]*inspect|internal\s+(?:quality\s+(?:assurance\s+)?)?audit|quality\s+audit|self[\s-]*audit",
        "heading": r"self[\s-]*inspect|internal\s+audit|quality\s+audit",
    },
}
LEADING = re.compile(r"^\s*(?:[A-Z]?\d+(?:\.\d+)*\.?|\([a-z0-9]+\)|principle)\s*", re.I)


def has_obligation(text):
    return any(obligations.strength(s) for s in obligations.sentences(text))


def under(ref, head):
    """True when ref lies under the heading clause head: "8.3" under "8", "Part I 10.8.2" under "Part I 10.8",
    "Chapter 9 9.1" under "Chapter 9", "2.41" under ICH Q7's "2.4"."""
    if ref == head:
        return False
    ref_prefix, _, ref_number = ref.rpartition(" ")
    head_prefix, _, head_number = head.rpartition(" ")
    if ref_prefix == head:
        return True
    if ref_prefix != head_prefix:
        return False
    return ref_number.startswith(head_number + ".") or bool(re.fullmatch(rf"{re.escape(head_number)}\d", ref_number))


def chapter(ref):
    """("Part I", "10") for "Part I 10.8.2"; ("", "8") for "8.9"."""
    prefix, _, number = ref.rpartition(" ")
    return prefix, number.split(".")[0]


def select(topic, sources, clauses_of):
    """(units, too_long): units are [{"source", "ref", "regulator", "why"}] in source and clause order."""
    spec = TOPICS[topic]
    named, heading = re.compile(spec["text"], re.I), re.compile(spec["heading"], re.I)
    out, too_long = [], []
    for f in sorted(sources):
        if sources[f]["priority"] not in ("must", "should") or sources[f]["phase"] != "pilot":
            continue
        tree = clauses_of(f)
        if not tree:
            continue
        heads = [ref for ref, c in tree.items() if c["kind"] != "toc" and heading.search(c.get("heading") or "")
                 and len(c.get("heading") or "") < 120]
        clauses = {ref: c for ref, c in tree.items() if c["kind"] in KINDS and has_obligation(c["text"])}
        names = {ref: bool(named.search(c["text"].replace("- ", "-"))) for ref, c in clauses.items()}
        per_chapter = defaultdict(list)
        for ref in clauses:
            per_chapter[chapter(ref)].append(names[ref])
        for ref, c in clauses.items():
            votes = per_chapter[chapter(ref)]
            why = ("text" if names[ref] else "heading" if any(under(ref, h) for h in heads)
                   else "chapter" if len(votes) > 1 and sum(votes) * 2 > len(votes) else "")
            if not why:
                continue
            unit = {"source": f, "ref": ref, "regulator": sources[f]["regulator"], "why": why}
            (too_long if len(c["text"]) > MAX_CHARS else out).append(unit)
    return out, too_long


def text_key(text):
    return normalise(LEADING.sub("", normalise(text)).replace("- ", "-"))


def with_twins(units, clauses_of):
    """The units to draft, each with "twins": the units of other sources with the same text (D36)."""
    groups = defaultdict(list)
    for u in units:
        groups[text_key(clauses_of(u["source"])[u["ref"]]["text"])].append(u)
    rank = {r: i for i, r in enumerate(CORE_ORDER)}
    out = []
    for members in groups.values():
        members.sort(key=lambda u: (rank.get(u["regulator"], len(rank)), u["source"], u["ref"]))
        lead, seen, twins = members[0], {members[0]["source"]}, []
        for u in members[1:]:
            if u["source"] in seen:                 # repeated text inside one source is its own clause
                out.append({**u, "twins": []})
                continue
            seen.add(u["source"])
            twins.append({"source": u["source"], "ref": u["ref"], "regulator": u["regulator"]})
        out.append({**lead, "twins": twins})
    order = {(u["source"], u["ref"]): i for i, u in enumerate(units)}
    return sorted(out, key=lambda u: order[(u["source"], u["ref"])])


def summary(drafted):
    per = Counter()
    for u in drafted:
        per[u["regulator"]] += 1
        for t in u["twins"]:
            per[t["regulator"] + " (twin)"] += 1
    return {"units": len(drafted) + sum(len(u["twins"]) for u in drafted), "drafted": len(drafted),
            "twins": sum(len(u["twins"]) for u in drafted), "per_regulator": dict(sorted(per.items()))}


def main():
    import layer1
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["list", "write"])
    ap.add_argument("--topic", default="self-inspection", choices=sorted(TOPICS))
    a = ap.parse_args()
    units, too_long = select(a.topic, layer1.catalog(), layer1.clauses_of)
    drafted = with_twins(units, layer1.clauses_of)
    s = {**summary(drafted), "too_long": too_long}
    if a.command == "list":
        for u in drafted:
            twins = ", ".join(f"{t['source']} {t['ref']}" for t in u["twins"])
            print(f"{u['regulator']:6} {u['why']:8} {u['source']} | {u['ref']}" + (f"  = {twins}" if twins else ""))
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{a.topic}.json").write_text(json.dumps({"topic": a.topic, **s, "units": drafted}, indent=1,
                                                        ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(s))


if __name__ == "__main__":
    main()
