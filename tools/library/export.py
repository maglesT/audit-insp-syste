"""Customer export and the option-A test (plan section 1; brief "Two separate systems").

  python3 tools/library/export.py check [--library DIR] [--all-sources]    # option-A test, in CI
  python3 tools/library/export.py build --regulators "EU,PIC/S" --plant OSD [--out FILE] [--library DIR]

The customer app loads only this export. It holds, per item, exactly ITEM_FIELDS: id, item text, topic,
regulators, plant types and strength; never quotes, clause references or sources (option A).
Customers see regulator names (REGULATOR_NAMES), and a selection is made by those names, so "EU" means EU and EMA
documents. Per-regulator items (D37), for one set of regulator names and one plant type:
- an item appears when it is verified, covers the plant type, and its mapping is to a selected regulator and
  covers the plant type (for an item marked general, any plant type of the item);
- items with the same text, topic and strength (twin clauses, EU GMP and PIC/S) are shown once, tagged with every
  selected regulator that has one;
- nothing else is combined across regulators: no merging by judgement, no "strictest wins", and no grouping of
  similar items (owner, D38);
- the checklist header lists only regulators that have an item.
Unverified items are never exported (D13).

The option-A test fails when the export
- has a field other than the allowed ones, a field name about quotes, clauses or sources, or a value of the wrong
  kind (unknown regulator name, plant type, strength or topic);
- contains OVERLAP_WORDS or more consecutive words that also appear in a source text (all parsed text of the
  source in document order, numbered or not, contents entries excepted), or a whole short source segment or a
  mapping's quote of at least PHRASE_WORDS words. Text is compared after Unicode normalisation (ligatures, soft
  hyphens, full-width and look-alike letters);
- contains clause-reference or document-name wording ("§", "Annex 15", "Art. 5", "21 CFR", "211.68", "ICH Q9",
  "PE 009", "TRS", "EudraLex", "Schedule M", "10.8.2"). Ordinary wording that trips this ("Section 1 of the batch
  record") goes in library/export-allow.json after a person has looked at it.
Every text a customer could see is checked: each item text, and the export of every regulator name alone and all
together, for every plant type. The sources compared are those
the library maps to (all sources with --all-sources; too slow for CI while clauses are parsed on demand).
"""
import argparse
import csv
import itertools
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

ITEM_FIELDS = ("id", "item_text", "topic", "regulators", "plant_types", "strength")
TOP_FIELDS = ("format", "generated", "regulators", "plant_type", "disclaimer", "topics", "items")
FORBIDDEN_NAME = re.compile(r"quote|clause|source|ref|sha|mapping|addend|page|offset|citation|url", re.I)
OVERLAP_WORDS = 12
PHRASE_WORDS = 6
RANK = {"optional": 0, "recommended": 1, "mandatory": 2}
DISCLAIMER = ("Compiled from official texts with automated multi-step verification. Supports internal audits; "
              "does not replace the site's own judgement.")
# regulator code in sources/catalog.csv -> the name customers see (a regulator name only, never a document)
REGULATOR_NAMES = {"EU": "EU", "EMA": "EU", "PICS": "PIC/S", "FDA": "US FDA", "WHO": "WHO", "ICH": "ICH",
                   "INDIA": "India", "JAPAN": "Japan", "BRAZIL": "Brazil"}
NAMES = sorted(set(REGULATOR_NAMES.values()))
_KEYWORD = (r"(?i:\b(?:annex(?:es)?|appendix|appendices|chapters?|articles?|art|sections?|sect|clauses?|"
            r"paragraphs?|para|parts?|points?|schedules?)\.?\s*[-–]?\s*)")
REFERENCE = re.compile(
    r"§"
    rf"|{_KEYWORD}(?:\d|[IVXLC]+\b)"               # Roman numerals in capitals only: "Part I", not "part i"
    r"|(?i:cfr)|(?i:eudralex)|(?i:\bschedule\s+m\b)"
    r"|\b\d+(?:\.\d+){2,}\b|\b\d{3}\.\d{1,3}\b"     # 10.8.2; 211.68
    r"|\bQ\d{1,2}[A-Z]?\b|\b(?:PE|PI|PS)\s*0\d\d\b|\bTRS\b|\b[A-Z]{2,}/[A-Z0-9]{2,}/")
WORD = re.compile(r"\w+")
# look-alike letters from other scripts, folded to Latin before comparing
CONFUSABLES = str.maketrans("аеорсухіјѕԁԛԝοαεικνρτυχ", "aeopcyxijsdqwoaeikvptux")
ALLOW_FILE = "export-allow.json"
# the number or letter a segment starts with ("9.3", "(b)", "1.", "a)"): left out so a copied run can cross
# from one clause into the next
MARKER = re.compile(r"^\s*(?:\(?[0-9]{1,3}[a-z]?\)|\(?[a-z]{1,4}\)|\d+(?:\.\d+)*\.?)\s+", re.I)


def unify(text):
    """NFKC (ligatures, full-width letters) without soft hyphens, look-alike letters folded; case kept."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    return text.translate(CONFUSABLES).translate(str.maketrans(
        {k.upper(): v.upper() for k, v in zip("аеорсухіјѕ", "aeopcyxijs")}))


def words(text):
    return WORD.findall(unify(text).casefold())


def catalog():
    with open(model.ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def _sentence(text):
    text = text.strip()
    return text if not text or text[-1] in ".!?" else text + "."


def _key(text):
    return " ".join(words(text))


def compile_items(reqs, sources, names, plant_type):
    """The items of one compilation (regulator names, one plant type), in library order (D37). Each library item
    is one obligation of one regulator; items of selected regulators with the same text, topic and strength (EU
    and PIC/S twins) are shown once with all their regulator tags; nothing else is combined (D38)."""
    names = set(names)

    def name(m):
        return REGULATOR_NAMES[sources[m["source"]]["regulator"]]

    merged = {}
    for req in reqs:
        if req["status"] != "verified" or plant_type not in req["plant_types"]:
            continue
        chosen = [m for m in req["mappings"] if name(m) in names
                  and (plant_type in m["plant_types"] or req["general"])]
        if not chosen:
            continue
        text = _sentence(req["item_text"])
        key = (_key(text), req["topic"], req["strength"])
        if key in merged:
            merged[key]["regulators"] = sorted(set(merged[key]["regulators"]) | {name(m) for m in chosen})
            continue
        merged[key] = {"id": req["id"], "item_text": text, "topic": req["topic"],
                       "regulators": sorted({name(m) for m in chosen}), "plant_types": [plant_type],
                       "strength": req["strength"]}
    return list(merged.values())


def export(reqs, sources, names, plant_type, topic_names, now=None):
    unknown = set(names) - set(NAMES)
    if unknown:
        raise ValueError(f"unknown regulator name(s): {', '.join(sorted(unknown))}")
    items = compile_items(reqs, sources, names, plant_type)
    return {"format": 1, "generated": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            "regulators": sorted({r for it in items for r in it["regulators"]}), "plant_type": plant_type,
            "disclaimer": DISCLAIMER, "topics": {t: topic_names[t] for t in sorted({it["topic"] for it in items})},
            "items": items}


class Corpus:
    """What customer text must not copy: every OVERLAP_WORDS-word run of the source texts, and whole short
    segments and mapping quotes of PHRASE_WORDS or more words."""

    def __init__(self, texts_by_source, quotes=()):
        self.runs = set()
        self.phrases = set()
        for texts in texts_by_source.values():
            texts = [MARKER.sub("", t) for t in texts]
            w = words(" ".join(texts))                       # document order, across segment boundaries
            self.runs.update(tuple(w[i:i + OVERLAP_WORDS]) for i in range(len(w) - OVERLAP_WORDS + 1))
            for t in texts:
                tw = tuple(words(t))
                if PHRASE_WORDS <= len(tw) < OVERLAP_WORDS:
                    self.phrases.add(tw)
        for q in quotes:
            qw = tuple(words(q))
            if PHRASE_WORDS <= len(qw) < OVERLAP_WORDS:     # a longer quote is caught by the runs
                self.phrases.add(qw)
        self.lengths = sorted({len(p) for p in self.phrases})

    def copied(self, text):
        """The first copied run or phrase in a text, or None."""
        w = words(text)
        for i in range(len(w) - OVERLAP_WORDS + 1):
            if tuple(w[i:i + OVERLAP_WORDS]) in self.runs:
                return " ".join(w[i:i + OVERLAP_WORDS])
        for n in self.lengths:
            for i in range(len(w) - n + 1):
                if tuple(w[i:i + n]) in self.phrases:
                    return " ".join(w[i:i + n])
        return None


def check_text(text, corpus, allow=()):
    """Option-A findings for one piece of customer-visible text."""
    out = []
    plain = unify(text)
    for phrase in allow:
        plain = re.sub(re.escape(unify(phrase)), " ", plain, flags=re.I)
    hit = REFERENCE.search(plain)
    if hit:
        out.append(f"reads as a clause or document reference ({hit.group(0)!r})")
    copied = corpus.copied(text)
    if copied:
        out.append(f"copies source wording: {copied!r}")
    return out


def _keys(value, path):
    if isinstance(value, dict):
        for k, v in value.items():
            yield f"{path}.{k}", k
            if path != "$" or k != "topics":                # topic ids are data, not field names
                yield from _keys(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _keys(v, f"{path}[{i}]")


def _strings(value, path):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _strings(v, f"{path}[{i}]")


def check(doc, corpus, allow=()):
    """Option-A findings for one export document (an empty list means it may ship)."""
    out = [f"$: field {k!r} is not allowed" for k in sorted(set(doc) - set(TOP_FIELDS))]
    out += [f"{path}: field name speaks of sources or quotes" for path, k in _keys(doc, "$")
            if FORBIDDEN_NAME.search(k)]
    topics = doc.get("topics", {})
    if not isinstance(topics, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in topics.items()):
        out.append("$.topics: must map topic ids to names")
        topics = {}
    if not set(doc.get("regulators", [])) <= set(NAMES):
        out.append("$.regulators: unknown regulator name")
    for i, item in enumerate(doc.get("items", [])):
        where = f"$.items[{i}]"
        if not isinstance(item, dict) or set(item) != set(ITEM_FIELDS):
            out.append(f"{where}: fields must be exactly {list(ITEM_FIELDS)}")
            continue
        if not isinstance(item["regulators"], list) or not set(item["regulators"]) <= set(NAMES):
            out.append(f"{where}.regulators: unknown regulator name")
        if not isinstance(item["plant_types"], list) or not set(item["plant_types"]) <= set(model.PLANT_TYPES):
            out.append(f"{where}.plant_types: unknown plant type")
        if item["strength"] not in RANK:
            out.append(f"{where}.strength: unknown strength")
        if item["topic"] not in topics:
            out.append(f"{where}.topic: not in $.topics")
        if not isinstance(item["item_text"], str):
            out.append(f"{where}.item_text: must be text")
    for path, text in _strings(doc, "$"):
        if path != "$.generated":
            out += [f"{path}: {f}" for f in check_text(text, corpus, allow)]
    return out


def corpus_for(reqs, sources, segments_of, all_sources=False):
    files = sorted(sources) if all_sources else sorted({m["source"] for r in reqs for m in r["mappings"]})
    texts = {f: [s["text"] for s in segments_of(f) if s["kind"] != "toc"] for f in files}
    return Corpus(texts, [m["quote"] for r in reqs for m in r["mappings"]])


def visible_texts(req, sources):
    """Every text of one item a customer could see: its item text (D37: no addenda, no compiled text)."""
    return [req["item_text"]]


def load_allow(root):
    path = Path(root) / ALLOW_FILE
    return model.load_json(path)["phrases"] if path.exists() else []


def compilations():
    """All regulator names together and each alone, per plant type."""
    for plant in model.PLANT_TYPES:
        yield NAMES, plant
        for name in NAMES:
            yield [name], plant


def check_library(root=model.LIBRARY, sources=None, segments_of=None, all_sources=False, drafts=False):
    """Option-A findings over the library: the item text of every verified item (with drafts=True, of every other
    live item instead; with drafts=None, of every live item), and, unless drafts is given, the export document of
    every regulator name alone and all together, per plant type.
    Only verified items can be exported; a draft with a finding is fixed before Layer 2 can verify it (verify.py)."""
    if segments_of is None:
        import layer1
        segments_of = layer1.segments_of
    sources = sources or catalog()
    reqs, names = model.requirements(root), model.topics(root)
    corpus, allow = corpus_for(reqs, sources, segments_of, all_sources), load_allow(root)
    out = []
    for req in reqs:
        if req["status"] == "retired" or (drafts is not None and (req["status"] == "verified") == drafts):
            continue
        for text in visible_texts(req, sources):
            out += [f"{req['id']}: {f}" for f in check_text(text, corpus, allow)]
    if drafts is not False:
        return sorted(set(out))
    for names_, plant in compilations():
        doc = export(reqs, sources, names_, plant, names)
        out += [f"{'+'.join(names_)}/{plant} {f}" for f in check(doc, corpus, allow)]
    return sorted(set(out))


def selection(arg):
    """Regulator names from a comma-separated list of names or catalog codes."""
    out = []
    for part in (p.strip() for p in arg.split(",") if p.strip()):
        name = REGULATOR_NAMES.get(part.upper(), part)
        if name not in NAMES:
            raise SystemExit(f"unknown regulator {part!r}; use one of: {', '.join(NAMES)}")
        out.append(name)
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "build"])
    ap.add_argument("--regulators", help="build: regulator names or catalog codes, comma-separated")
    ap.add_argument("--plant", choices=model.PLANT_TYPES, help="build: one plant type")
    ap.add_argument("--out", help="build: output file (default: print)")
    ap.add_argument("--library", default=str(model.LIBRARY), help="library folder (default: library/)")
    ap.add_argument("--all-sources", action="store_true", help="compare with every source, not only mapped ones")
    a = ap.parse_args(argv)
    sources = catalog()
    if a.command == "check":
        findings = check_library(a.library, sources, all_sources=a.all_sources)
        for f in findings:
            print(f)
        reqs = model.requirements(a.library)
        drafts = check_library(a.library, sources, all_sources=a.all_sources, drafts=True)
        print(f"option A: {len(findings)} findings ({sum(r['status'] == 'verified' for r in reqs)} verified items "
              f"of {len(reqs)}); not yet verified items with findings, to fix before verification: "
              f"{len({f.split(':')[0] for f in drafts})}")
        sys.exit(1 if findings else 0)
    if not a.regulators or not a.plant:
        ap.error("build needs --regulators and --plant")
    names = selection(a.regulators)
    findings = check_library(a.library, sources, all_sources=a.all_sources)
    if findings:
        sys.exit("refused, option A:\n" + "\n".join(findings))
    doc = export(model.requirements(a.library), sources, names, a.plant, model.topics(a.library))
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
