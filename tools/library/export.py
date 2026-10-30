"""Customer export and the option-A test (plan section 1; brief "Two separate systems").

  python3 tools/library/export.py check                                   # option-A test on every compilation
  python3 tools/library/export.py build --regulators EU,PICS --plant OSD [--out FILE]

The customer app loads only this export. It holds, per item, exactly ITEM_FIELDS: id, item text, topic,
regulators, plant types and strength; never quotes, clause references or sources (option A). "Strictest wins"
for one set of regulators and one plant type:
- a requirement applies when it is verified, covers the plant type, and has a mapping to a selected regulator
  that covers the plant type (or the requirement is marked general);
- the item text is the base text plus the addenda of the selected regulators' mappings whose relation is
  "stricter" or "adds";
- the strength is the strictest of the selected mappings.
Unverified requirements are never exported (D13).

The option-A test fails when the export
- has a field other than the allowed ones, or any field whose name speaks of quotes, clauses or sources;
- contains a run of OVERLAP_WORDS or more consecutive words that also appears in a source text;
- contains something that reads as a clause reference ("§", "Annex 15", "Chapter 4", "21 CFR", "10.8.2").
The source texts are every citable clause of every source the library maps to (all sources with --all-sources).
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

ITEM_FIELDS = ("id", "item_text", "topic", "regulators", "plant_types", "strength")
TOP_FIELDS = ("format", "generated", "regulators", "plant_type", "disclaimer", "topics", "items")
FORBIDDEN_NAME = re.compile(r"quote|clause|source|ref|sha|mapping|addend|page|offset|citation|url", re.I)
OVERLAP_WORDS = 12
RANK = {"optional": 0, "recommended": 1, "mandatory": 2}
ADDS = ("stricter", "adds")
DISCLAIMER = ("Compiled from official texts with automated multi-step verification. Supports internal audits; "
              "does not replace the site's own judgement.")
# regulator code in sources/catalog.csv -> the name customers see (a regulator name only, never a document)
REGULATOR_NAMES = {"EU": "EU", "EMA": "EU", "PICS": "PIC/S", "FDA": "US FDA", "WHO": "WHO", "ICH": "ICH",
                   "INDIA": "India", "JAPAN": "Japan", "BRAZIL": "Brazil"}
REFERENCE = re.compile(
    r"§|\b(?:annex|appendix|chapter|article|section|clause|paragraph|part|schedule)\s+[0-9IVXLC]+\b"
    r"|\bschedule\s+m\b|\bCFR\b|\b\d+(?:\.\d+){2,}\b|\b\d{3}\.\d{1,3}\s*\([a-z0-9]+\)", re.I)
WORD = re.compile(r"[a-z0-9]+")


def catalog():
    with open(model.ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def compile_items(reqs, sources, regulators, plant_type):
    """The items of one compilation (regulator codes, one plant type), in library order."""
    regulators = set(regulators)
    items = []
    for req in reqs:
        if req["status"] != "verified" or plant_type not in req["plant_types"]:
            continue
        chosen = [m for m in req["mappings"] if sources[m["source"]]["regulator"] in regulators
                  and (plant_type in m["plant_types"] or req["general"])]
        if not chosen:
            continue
        addenda = []
        for m in chosen:
            text = m["addendum"].strip()
            if m["relation"] in ADDS and text and text not in addenda:
                addenda.append(text)
        items.append({
            "id": req["id"],
            "item_text": " ".join([req["item_text"].strip()] + addenda),
            "topic": req["topic"],
            "regulators": sorted({REGULATOR_NAMES[sources[m["source"]]["regulator"]] for m in chosen}),
            "plant_types": [plant_type],
            "strength": max((m["strength"] for m in chosen), key=RANK.get),
        })
    return items


def export(reqs, sources, regulators, plant_type, topic_names, now=None):
    items = compile_items(reqs, sources, regulators, plant_type)
    used = {it["topic"] for it in items}
    return {"format": 1, "generated": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            "regulators": sorted({REGULATOR_NAMES[r] for r in regulators}), "plant_type": plant_type,
            "disclaimer": DISCLAIMER, "topics": {t: topic_names[t] for t in sorted(used)}, "items": items}


def words(text):
    return WORD.findall(text.lower())


def shingles(texts, n=OVERLAP_WORDS):
    """Every run of n consecutive words in the texts (as hashes)."""
    out = set()
    for text in texts:
        w = words(text)
        out.update(hash(tuple(w[i:i + n])) for i in range(len(w) - n + 1))
    return out


def _strings(value, path):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _strings(v, f"{path}[{i}]")


def _keys(value, path):
    if isinstance(value, dict):
        if path == "$.topics":                      # {topic id: name}: the keys are data, not field names
            return
        for k, v in value.items():
            yield f"{path}.{k}", k
            yield from _keys(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _keys(v, f"{path}[{i}]")


def check(doc, source_shingles, n=OVERLAP_WORDS):
    """Option-A findings for one export document (an empty list means it may ship)."""
    out = []
    extra = set(doc) - set(TOP_FIELDS)
    out += [f"$: field {k!r} is not allowed" for k in sorted(extra)]
    for i, item in enumerate(doc.get("items", [])):
        if set(item) != set(ITEM_FIELDS):
            out.append(f"$.items[{i}]: fields must be exactly {list(ITEM_FIELDS)}, got {sorted(item)}")
    out += [f"{path}: field name speaks of sources or quotes" for path, k in _keys(doc, "$")
            if FORBIDDEN_NAME.search(k)]
    for path, text in _strings(doc, "$"):
        if path in ("$.generated",):
            continue
        if REFERENCE.search(text):
            out.append(f"{path}: reads as a clause reference ({REFERENCE.search(text).group(0)!r})")
        w = words(text)
        for j in range(len(w) - n + 1):
            if hash(tuple(w[j:j + n])) in source_shingles:
                out.append(f"{path}: {n} consecutive words also appear in a source: {' '.join(w[j:j + n])!r}")
                break
    return out


def source_texts(reqs, sources, clauses_of, all_sources=False):
    files = sorted(sources) if all_sources else sorted({m["source"] for r in reqs for m in r["mappings"]})
    return [c["text"] for f in files for c in clauses_of(f).values()]


def compilations(sources):
    """Every compilation the app can ask for: all regulators together, and each regulator alone, per plant type."""
    codes = sorted({r["regulator"] for r in sources.values()})
    for plant in model.PLANT_TYPES:
        yield codes, plant
        for code in codes:
            yield [code], plant


def check_library(root=model.LIBRARY, sources=None, clauses_of=None, all_sources=False):
    """Option-A findings over every compilation of the library."""
    if clauses_of is None:
        import layer1
        clauses_of = layer1.clauses_of
    sources = sources or catalog()
    reqs, names = model.requirements(root), model.topics(root)
    known = shingles(source_texts(reqs, sources, clauses_of, all_sources))
    out = []
    for regulators, plant in compilations(sources):
        doc = export(reqs, sources, regulators, plant, names)
        out += [f"{'+'.join(regulators)}/{plant} {f}" for f in check(doc, known)]
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "build"])
    ap.add_argument("--regulators", help="build: regulator codes from sources/catalog.csv, comma-separated")
    ap.add_argument("--plant", choices=model.PLANT_TYPES, help="build: one plant type")
    ap.add_argument("--out", help="build: output file (default: print)")
    ap.add_argument("--all-sources", action="store_true", help="compare with every source, not only mapped ones")
    a = ap.parse_args()
    sources = catalog()
    if a.command == "check":
        findings = check_library(sources=sources, all_sources=a.all_sources)
        for f in findings:
            print(f)
        n = len(model.requirements())
        print(f"option A: {len(findings)} findings ({n} requirements)")
        sys.exit(1 if findings else 0)
    if not a.regulators or not a.plant:
        ap.error("build needs --regulators and --plant")
    codes = a.regulators.split(",")
    unknown = set(codes) - {r["regulator"] for r in sources.values()}
    if unknown:
        ap.error(f"unknown regulator code(s): {', '.join(sorted(unknown))}")
    import layer1
    reqs = model.requirements()
    doc = export(reqs, sources, codes, a.plant, model.topics())
    findings = check(doc, shingles(source_texts(reqs, sources, layer1.clauses_of, a.all_sources)))
    if findings:
        sys.exit("refused, option A:\n" + "\n".join(findings))
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
