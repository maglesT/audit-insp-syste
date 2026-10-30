"""The internal library: topics, checklist items with their source clause, coverage (plan section 1, D37).

Plain JSON files in git, so every change is a reviewable diff (D12):
- library/topics.json                      the fixed topic tree (about 20 audit areas with sub-topics)
- library/requirements/<TOPIC>.json        {"requirements": [Requirement, ...]} for one topic
- library/coverage/<source stem>.json      {"clauses": {clause ref: {"requirements": [...]} | {"na": reason}}}

Per-regulator items (D37): a requirement record is one checklist item for one obligation of one regulator. It holds
the plain-language item text (the only text customers ever see) and exactly one mapping, its internal source link:
source, clause reference, clause sha256, exact quote, strength and plant types (never exported, option A). There is
no cross-regulator merging or grouping (D37, D38); only identical items are shown once by the export.
Standard library only.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "library"

PLANT_TYPES = ("OSD", "LIQ", "SEMI", "INJ", "API")          # D6; "ALL" in sources means every type
STRENGTHS = ("mandatory", "recommended", "optional")
STATUSES = ("draft", "verified", "unverified", "retired")
ID = re.compile(r"^[A-Z]{2,5}-\d{3,4}$")                       # "SI-001": topic + running number
SHA256 = re.compile(r"^[0-9a-f]{64}$")

REQUIREMENT_FIELDS = {"id": str, "topic": str, "item_text": str, "strength": str, "plant_types": list,
                      "parameters": dict, "general": bool, "status": str, "mappings": list}
MAPPING_FIELDS = {"source": str, "clause_ref": str, "clause_sha256": str, "quote": str, "strength": str,
                  "plant_types": list}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def topics(root=LIBRARY):
    """{topic or sub-topic id: name}."""
    out = {}
    for t in load_json(Path(root) / "topics.json")["topics"]:
        out[t["id"]] = t["name"]
        for sub in t["sub"]:
            out[sub] = t["name"]
    return out


def requirements(root=LIBRARY):
    """All requirements, in file and list order."""
    out = []
    for path in sorted((Path(root) / "requirements").glob("*.json")):
        out += load_json(path)["requirements"]
    return out


def coverage(root=LIBRARY):
    """{source file stem: {clause ref: entry}}."""
    return {p.stem: load_json(p)["clauses"] for p in sorted((Path(root) / "coverage").glob("*.json"))}


def _fields(obj, spec, where):
    errors = []
    for name, kind in spec.items():
        if name not in obj:
            errors.append(f"{where}: missing field '{name}'")
        elif not isinstance(obj[name], kind):
            errors.append(f"{where}: '{name}' must be {kind.__name__}")
    errors += [f"{where}: unknown field '{name}'" for name in obj if name not in spec]
    return errors


def validate(root=LIBRARY, sources=None):
    """Structural errors in the library (an empty list means valid). Checks shapes, ids and vocabularies only;
    whether quotes and numbers match the sources is Layer 1 (tools/library/layer1.py).

    sources: {file name: catalog row}; defaults to sources/catalog.csv.
    """
    if sources is None:
        import csv
        with open(ROOT / "sources" / "catalog.csv", encoding="utf-8") as f:
            sources = {r["file"]: r for r in csv.DictReader(f)}
    known_topics = topics(root)
    errors, seen = [], set()
    for req in requirements(root):
        where = f"requirement {req.get('id', '?')}"
        errors += _fields(req, REQUIREMENT_FIELDS, where)
        if not isinstance(req.get("id"), str) or not ID.match(req["id"]):
            errors.append(f"{where}: id must look like 'SI-001'")
        elif req["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(req.get("id"))
        if req.get("topic") not in known_topics:
            errors.append(f"{where}: unknown topic {req.get('topic')!r}")
        if req.get("strength") not in STRENGTHS:
            errors.append(f"{where}: strength must be one of {STRENGTHS}")
        if req.get("status") not in STATUSES:
            errors.append(f"{where}: status must be one of {STATUSES}")
        if not isinstance(req.get("plant_types"), list) or not req["plant_types"] \
                or any(p not in PLANT_TYPES for p in req["plant_types"]):
            errors.append(f"{where}: plant_types must be a non-empty subset of {PLANT_TYPES}")
        if not str(req.get("item_text", "")).strip():
            errors.append(f"{where}: empty item_text")
        for k, v in (req.get("parameters") or {}).items():
            if not isinstance(v, (int, float, str)):
                errors.append(f"{where}: parameter {k!r} must be a number or a short string")
        if len(req.get("mappings") or []) != 1 and req.get("status") != "retired":
            errors.append(f"{where}: an item has exactly one mapping (D37)")
        for n, m in enumerate(req.get("mappings") or [], start=1):
            mw = f"{where} mapping {n}"
            if not isinstance(m, dict):
                errors.append(f"{mw}: must be an object")
                continue
            errors += _fields(m, MAPPING_FIELDS, mw)
            if m.get("source") not in sources:
                errors.append(f"{mw}: unknown source {m.get('source')!r}")
            if not SHA256.match(str(m.get("clause_sha256", ""))):
                errors.append(f"{mw}: clause_sha256 must be a sha256 hex digest")
            if m.get("strength") not in STRENGTHS:
                errors.append(f"{mw}: strength must be one of {STRENGTHS}")
            if not isinstance(m.get("plant_types"), list) or not m["plant_types"] \
                    or any(p not in PLANT_TYPES for p in m["plant_types"]):
                errors.append(f"{mw}: plant_types must be a non-empty subset of {PLANT_TYPES}")
            if not str(m.get("quote", "")).strip():
                errors.append(f"{mw}: empty quote")
    for stem, clauses in coverage(root).items():
        for ref, entry in clauses.items():
            where = f"coverage {stem} {ref}"
            if set(entry) == {"requirements"}:
                if not isinstance(entry["requirements"], list) or not entry["requirements"]:
                    errors.append(f"{where}: 'requirements' must be a non-empty list")
                    continue
                errors += [f"{where}: unknown requirement {r}" for r in entry["requirements"] if r not in seen]
            elif set(entry) == {"na"}:
                if not str(entry["na"]).strip():
                    errors.append(f"{where}: 'na' needs a reason")
            else:
                errors.append(f"{where}: entry must be {{'requirements': [...]}} or {{'na': reason}}")
    return errors
