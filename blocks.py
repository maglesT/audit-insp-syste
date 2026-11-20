"""AUDIT LAYER step 1: cut the proven clause library into BLOCKS (one API request each). Session audit-layer-65, 19 Nov 2026.

Reads (read-only): merged/checklist.json, merged/checkpoints.json (final marks), merged/audience.json.
Writes: blocks.json (this folder).

Rules
B1 a block = items of ONE regulator, ONE part, ONE section path, with the SAME area, plant_types and audience, in
   checklist order. So every point drafted inside a block has exactly its clauses' area / plant types / audience
   (never widened; owner/lead "union rule" holds trivially).
B2 a block is sent only if it has >= 1 DUTY unit; items whose units are all INFORMATION stay in the block as context.
B3 a block with more than MAX_DUTY duty units is cut at item boundaries into chunks of <= MAX_DUTY duty units
   (an item with more duty units than that stays whole).
B4 FDA system (CP 7356.002 six systems) comes from the area by the fixed table SYSTEM below (lead may rule otherwise).
Unit ids: "<item id>#<n>" (n = checkpoints unit n). Text sent: Schedule M / FDA / EU text only (never WHO / PIC/S text).
"""
import json, hashlib, collections, os

ROOT = "/root/audit-admin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_DUTY = 30
SYSTEM = {
    "QS": "Quality", "DOC": "Quality", "REL": "Quality", "CMP": "Quality", "PER": "Quality",
    "SUP": "Materials", "WH": "Materials",
    "PREM": "Facilities and Equipment", "UTIL": "Facilities and Equipment", "EQ": "Facilities and Equipment",
    "CSV": "Facilities and Equipment",
    "PROD": "Production", "STER": "Production", "VAL": "Production",
    "PACK": "Packaging and Labeling",
    "QC": "Laboratory Control",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ck = json.load(open(f"{ROOT}/merged/checklist.json"))
    cp = {x["id"]: x for x in json.load(open(f"{ROOT}/merged/checkpoints.json"))}
    au = json.load(open(f"{ROOT}/merged/audience.json"))["items"]
    groups = collections.OrderedDict()
    for it in ck:
        aud = au.get(it["id"], {}).get("audience", "manufacturer")
        k = (it["regulator"], it["part"], tuple(it["path"]), it["area"], tuple(it["plant_types"]), aud)
        groups.setdefault(k, []).append(it)
    blocks = []
    for k, items in groups.items():
        reg, part, path, area, pts, aud = k
        nd = lambda it: sum(1 for u in cp[it["id"]]["units"] if u["mark"] == "duty")
        if not sum(nd(it) for it in items):
            continue
        chunks, cur, c = [], [], 0
        for it in items:
            if cur and c + nd(it) > MAX_DUTY:
                chunks.append(cur); cur, c = [], 0
            cur.append(it); c += nd(it)
        if cur:
            chunks.append(cur)
        for ci, ch in enumerate(chunks):
            if not sum(nd(it) for it in ch):      # a trailing chunk of context only joins the previous chunk
                chunks[ci - 1].extend(ch); continue
        chunks = [ch for ch in chunks if sum(nd(it) for it in ch)]
        for ci, ch in enumerate(chunks):
            bid = f"B{len(blocks) + 1:04d}"
            blocks.append({
                "id": bid, "regulator": reg, "part": part, "path": list(path), "area": area,
                "system": SYSTEM[area], "plant_types": list(pts), "audience": aud,
                "chunk": f"{ci + 1}/{len(chunks)}",
                "items": [{
                    "id": it["id"], "ref": it["ref"], "title": it.get("title"), "lead": it.get("lead"),
                    "tables": it.get("tables") or [],
                    "units": [{"uid": f'{it["id"]}#{u["n"]}', "n": u["n"], "mark": u["mark"], "text": u["text"]}
                              for u in cp[it["id"]]["units"]],
                } for it in ch],
            })
    duty = [u["uid"] for b in blocks for it in b["items"] for u in it["units"] if u["mark"] == "duty"]
    all_duty = [f'{i}#{u["n"]}' for i, x in cp.items() for u in x["units"] if u["mark"] == "duty"]
    assert len(duty) == len(set(duty)) and set(duty) == set(all_duty), "duty unit coverage of blocks broken"
    out = {
        "_doc": __doc__,
        "inputs_sha256": {f: sha(f"{ROOT}/merged/{f}") for f in ("checklist.json", "checkpoints.json", "audience.json")},
        "counts": {"blocks": len(blocks), "duty_units": len(duty),
                   "by_regulator": collections.Counter(b["regulator"] for b in blocks)},
        "blocks": blocks,
    }
    json.dump(out, open(f"{HERE}/blocks.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(out["counts"]))


if __name__ == "__main__":
    main()
