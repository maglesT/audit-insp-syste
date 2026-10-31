"""Table Transformer trial (D41): table grids from a layout model, cell text from the PDF's own text layer.

  python3 tools/parse/tatr.py fetch                 # download the pinned model files into models/ (not in git)
  python3 tools/parse/tatr.py run [SOURCE:PAGE ...] # detect tables and their grids on rendered pages (offline)
  python3 tools/parse/tatr.py compare               # grids of the model vs tables.py on the trial pages

Microsoft's Table Transformer (DETR models trained on PubTables-1M; MIT licence) finds tables on a page image
(the detection model) and, on each table's crop, its rows, columns, column-header rows and spanning cells (the
structure model). The page is rendered with pypdfium2; the model returns boxes only. No word is read from the
image: every cell's text is the poppler words whose centre lies in the cell, as in tables.py. Both models are
pinned to a revision and their files to sha256 (a mismatch is refused). `run` needs torch, transformers and timm
(CPU) and is not part of CI: it writes library/tables-tatr/grids.json with the pins, and the rest of the code
(compare, and tables.py where a grid is adopted) reads only that file, so CI and parsing never run the model.

Post-processing (deterministic, after the reference code's idea, simplified): a row or column is kept at score
>= KEEP; of two rows (columns) that overlap by more than half of the smaller, the lower score is dropped, and neighbours
that still overlap are cut in the middle of the overlap (a word belongs to one row); rows
are stretched to the table's width and columns to its height; a cell is the intersection of a row and a column.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import OFFICIAL  # noqa: E402

MODELS = ROOT / "models"
GRIDS = ROOT / "library" / "tables-tatr" / "grids.json"
SCALE = 2.0                 # render at 144 dpi
DETECT_MIN = 0.7            # a detected table
KEEP = 0.5                  # a row, column, header or spanning cell
PAD = 12                    # points of margin around a table crop (the structure model was trained with margin)
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)

PINS = {
    "detection": {
        "repo": "microsoft/table-transformer-detection",
        "revision": "2357cbe2b5a5d1c03e54f32764f06058933b65ab",
        "max_size": 800,
        "files": {
            "config.json": "ed5b93df2c3a59d473ddea853553a6d545d52bd4e9f8f72bf40b8a974aba4c1d",
            "model.safetensors": "8f1aa73170102c038d40155e2734b343bf07e0fe12594228a8590943b01dccf7",
        },
    },
    "structure": {
        "repo": "microsoft/table-transformer-structure-recognition-v1.1-all",
        "revision": "7587a7ef111d9dcbf8ac695f1376ab7014340a0c",
        "max_size": 1000,
        "files": {
            "config.json": "17a8a6edfb9e394263fa6ba9b82176ebccdfcc5d6cd29121ec91572c7d6be22c",
            "model.safetensors": "9df416575a3a36ebd0129342d4f597f14d6e5170268f3d52d28584ab4466a501",
        },
    },
}

# The D41 trial pages (1-based page numbers in the PDF), with why each is there.
TRIAL = {
    "who-trs1044-a2-sterile.pdf": [17, 19],                         # cleanroom grade tables
    "eu-20220825_gmp-an1_en_0.pdf": [13, 14, 22, 23, 45, 47],       # idem, and the other EU Annex 1 tables
    "pics-pe009-18-annexes.pdf": [20, 21],                          # idem (PE 009 Annex 1)
    "india-cdsco-circ-2024-03-risk-based-inspection.pdf":           # section-heading rows merged into the row
        [45, 48, 49, 52, 53, 54, 57, 66, 116, 119, 120],            # above; p116 the former TEXT LOST row 27.4
    "ich-q3c-r9.pdf": [11, 12, 13, 17, 18],                         # unruled solvent tables (stored as text)
    "who-trs1010-a8-hvac-nonsterile.pdf": [15, 16, 17],             # Table A8.1, landscape (read upright)
    "fda-cp-7346-832-preapproval-inspections.pdf": [44, 53, 54],    # former TEXT LOST p44; p53-54 row not found
    "fda-cp-7356-002-drug-manufacturing-inspections.pdf": [41],     # former TEXT LOST page
    "fda-guidance-nitrosamine-control-2024.pdf": [41],              # former TEXT LOST page
}

# Pages where the model's grid replaces pdfplumber's (tables.read), after review of trial.md and the fidelity check
# (D43). Everywhere else tables.py's own grid stays.
ADOPTED = {
    "who-trs1044-a2-sterile.pdf:19": "Table 2 microbial limits: pdfplumber finds the header row only (no rules "
                                     "below it), so the grade rows A-D were stored inside 4.31 without columns",
    "ich-q3c-r9.pdf:11": "Table 1 Class 1 solvents: unruled, pdfplumber finds no table; the whole table is on "
                         "this page and the model's grid holds every word once",
}


def adopted_grids(source, path=GRIDS):
    """{page: [grid, ...]} of the adopted pages of one source, from the committed grids. A grid whose PDF sha256
    differs from the PDF's is refused (the boxes belong to that exact file)."""
    out = {}
    keys = [k for k in ADOPTED if k.rsplit(":", 1)[0] == source]
    if not keys:
        return out
    doc = json.loads(Path(path).read_text())["pages"]
    for k in keys:
        if doc[k]["sha256"] != sha256(OFFICIAL / source):
            raise SystemExit(f"{k}: the PDF differs from the one the grid was made on; re-run tatr.py run")
        out[int(k.rsplit(":", 1)[1])] = doc[k]["tables"]
    return out


def model_dir(name):
    return MODELS / PINS[name]["repo"].split("/")[1]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(name):
    """Problems with one model's local files; empty when they match the pins."""
    out = []
    for fname, want in PINS[name]["files"].items():
        path = model_dir(name) / fname
        if not path.exists():
            out.append(f"{name}/{fname}: missing")
        elif sha256(path) != want:
            out.append(f"{name}/{fname}: sha256 does not match the pin")
    return out


def fetch():
    for name, pin in PINS.items():
        model_dir(name).mkdir(parents=True, exist_ok=True)
        for fname, want in pin["files"].items():
            path = model_dir(name) / fname
            if path.exists() and sha256(path) == want:
                continue
            url = f"https://huggingface.co/{pin['repo']}/resolve/{pin['revision']}/{fname}"
            with urllib.request.urlopen(url, timeout=300) as r, open(path, "wb") as f:
                while block := r.read(1 << 20):
                    f.write(block)
            if sha256(path) != want:
                path.unlink()
                raise SystemExit(f"{name}/{fname}: sha256 does not match the pin; deleted")
    print("models ready")


def load(name):
    """The pinned model, in eval mode. transformers 5 rejects null fields of these older configs, so they are
    left out (the class defaults apply, as they did when the models were published)."""
    problems = check(name)
    if problems:
        raise SystemExit("; ".join(problems) + " (run: python3 tools/parse/tatr.py fetch)")
    from transformers import TableTransformerConfig, TableTransformerForObjectDetection
    cfg = json.loads((model_dir(name) / "config.json").read_text())
    cfg = TableTransformerConfig.from_dict({k: v for k, v in cfg.items() if v is not None})
    model = TableTransformerForObjectDetection.from_pretrained(str(model_dir(name)), config=cfg)
    return model.eval()


def infer(model, image, max_size, threshold):
    """[(label, score, (x0, y0, x1, y1) in image pixels)] of one image: resized so its longer side is max_size,
    normalised with the ImageNet mean and deviation, boxes decoded from (cx, cy, w, h) fractions."""
    import torch
    w, h = image.size
    k = max_size / max(w, h)
    img = image.resize((round(w * k), round(h * k)))
    import numpy as np
    x = torch.from_numpy(np.asarray(img, dtype=np.float32) / 255.0)
    x = ((x - torch.tensor(MEAN)) / torch.tensor(STD)).permute(2, 0, 1).unsqueeze(0)
    with torch.no_grad():
        out = model(pixel_values=x)
    probs = out.logits.softmax(-1)[0, :, :-1]                # the last class is "no object"
    scores, labels = probs.max(-1)
    found = []
    for s, lab, (cx, cy, bw, bh) in zip(scores.tolist(), labels.tolist(), out.pred_boxes[0].tolist()):
        if s >= threshold:
            found.append((model.config.id2label[lab], round(s, 4),
                          ((cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h)))
    return found


def _dedupe(boxes, axis):
    """Of boxes [(score, box)] overlapping by more than half of the smaller along axis (1 rows, 0 columns), the
    higher score stays; sorted along the axis."""
    keep = []
    for s, b in sorted(boxes, key=lambda x: -x[0]):
        lo, hi = b[axis], b[axis + 2]
        if all(min(hi, k[axis + 2]) - max(lo, k[axis]) <= 0.5 * min(hi - lo, k[axis + 2] - k[axis]) for _, k in keep):
            keep.append((s, b))
    out = [list(b) for _, b in sorted(keep, key=lambda x: x[1][axis])]
    for a, b in zip(out, out[1:]):                       # neighbours that still overlap: cut in the middle
        if a[axis + 2] > b[axis]:
            a[axis + 2] = b[axis] = (a[axis + 2] + b[axis]) / 2
    return [tuple(b) for b in out]


def structure(found, table):
    """Grid of one table from the structure model's boxes (PDF points): rows stretched to the table's width,
    columns to its height, column-header rows and spanning cells as boxes."""
    x0, y0, x1, y1 = table
    rows = _dedupe([(s, b) for lab, s, b in found if lab == "table row"], 1)
    cols = _dedupe([(s, b) for lab, s, b in found if lab == "table column"], 0)
    r4 = lambda b: [round(v, 2) for v in b]                  # noqa: E731
    return {
        "bbox": r4(table),
        "rows": [r4((x0, b[1], x1, b[3])) for b in rows],
        "columns": [r4((b[0], y0, b[2], y1)) for b in cols],
        "headers": [r4(b) for lab, s, b in found if lab == "table column header"],
        "spanning": [r4(b) for lab, s, b in found if lab == "table spanning cell"],
    }


def page_grids(det, struct, path, pno):
    """Tables and their grids on one page (PDF points, origin top left) of the PDF the parsers read (the upright
    copy when the page is turned, so the boxes match tables.py's)."""
    import tempfile
    import pypdfium2 as pdfium
    import common
    with tempfile.TemporaryDirectory() as tmp:
        doc = pdfium.PdfDocument(str(common.upright_copy(path, tmp)))
        try:
            image = doc[pno - 1].render(scale=SCALE).to_pil().convert("RGB")
        finally:
            doc.close()
    out = []
    for lab, score, box in infer(det, image, PINS["detection"]["max_size"], DETECT_MIN):
        if lab not in ("table", "table rotated"):
            continue
        t = tuple(v / SCALE for v in box)
        cx0, cy0 = max(t[0] - PAD, 0), max(t[1] - PAD, 0)
        crop = image.crop((cx0 * SCALE, cy0 * SCALE, (t[2] + PAD) * SCALE, (t[3] + PAD) * SCALE))
        found = [(lb, s, (b[0] / SCALE + cx0, b[1] / SCALE + cy0, b[2] / SCALE + cx0, b[3] / SCALE + cy0))
                 for lb, s, b in infer(struct, crop, PINS["structure"]["max_size"], KEEP)]
        grid = structure(found, t)
        grid["score"], grid["label"] = score, lab
        out.append(grid)
    return sorted(out, key=lambda g: (round(g["bbox"][1]), g["bbox"][0]))


def run(targets):
    """Runs both models on the pages and writes GRIDS (merging with grids already there)."""
    import torch
    torch.manual_seed(0)
    torch.set_num_threads(4)
    det, struct = load("detection"), load("structure")
    doc = json.loads(GRIDS.read_text()) if GRIDS.exists() else {"pages": {}}
    import transformers
    doc["models"] = {k: {"repo": v["repo"], "revision": v["revision"], "files": v["files"]} for k, v in PINS.items()}
    doc["settings"] = {"scale": SCALE, "detect_min": DETECT_MIN, "keep": KEEP, "pad": PAD,
                       "torch": torch.__version__, "transformers": transformers.__version__,
                       "code_sha256": sha256(Path(__file__))}
    for source, pno in targets:
        path = OFFICIAL / source
        key = f"{source}:{pno}"
        doc["pages"][key] = {"sha256": sha256(path), "tables": page_grids(det, struct, path, pno)}
        print(key, len(doc["pages"][key]["tables"]), "table(s)", flush=True)
    doc["pages"] = dict(sorted(doc["pages"].items()))
    GRIDS.parent.mkdir(parents=True, exist_ok=True)
    GRIDS.write_text(json.dumps(doc, indent=1) + "\n")


def grids(path=GRIDS):
    """The committed grids: {"source:page": [table, ...]}; {} when none."""
    if not Path(path).exists():
        return {}
    return {k: v["tables"] for k, v in json.loads(Path(path).read_text())["pages"].items()}


def _grid_stats(table, words):
    """(rows of cell texts, words in the table's outline in no cell, words in two or more cells)."""
    import tables
    rows = [r for r in tables._drop_empty_columns(tables._cells(table, words)) if any(r)]
    boxes = [b for r in tables._row_boxes(table) for b in r if b]
    inside = [w for w in words if tables._centre_in(w, table.bbox)]
    lost = [w[4] for w in inside if not any(tables._centre_in(w, b) for b in boxes)]
    twice = [w[4] for w in inside if sum(tables._centre_in(w, b) for b in boxes) > 1]
    return rows, lost, twice


def compare(path_md=GRIDS.with_name("trial.md"), width=150):
    """Side by side, per trial page: the tables pdfplumber finds (tables.py, without the ones it rejects for stray
    words) and the model's, each filled with the same poppler words; writes trial.md for review."""
    import tempfile
    import pdfplumber
    import common
    import tables
    out = ["# Table Transformer trial: grids side by side (D41)", "",
           "Generated by `python3 tools/parse/tatr.py compare` from `grids.json`. Cell text is poppler's words in "
           "both columns; only the grid differs. lost = words inside the table outline in no cell; twice = words "
           "in two or more cells.", ""]
    for key, found in grids().items():
        source, pno = key.rsplit(":", 1)[0], int(key.rsplit(":", 1)[1])
        with tempfile.TemporaryDirectory() as tmp:
            copy = common.upright_copy(OFFICIAL / source, tmp)
            words = tables._words(copy, int(pno))
            with pdfplumber.open(str(copy)) as pdf:
                plumber = tables.page_tables(pdf.pages[int(pno) - 1])
                rejected = [t for t in plumber if tables.stray_words(t, words)]
                plumber = [t for t in plumber if t not in rejected]
                sides = {"tables.py": plumber, "model": [tables.Grid(g) for g in found]}
                out.append(f"## {key}")
                out.append(f"tables.py: {len(plumber)} table(s) ({len(rejected)} rejected for stray words); "
                           f"model: {len(found)} table(s)")
                for name, ts in sides.items():
                    for i, t in enumerate(ts):
                        rows, lost, twice = _grid_stats(t, words)
                        out.append(f"### {name} table {i + 1}: bbox {[round(v) for v in t.bbox]}, {len(rows)} rows "
                                   f"x {max((len(r) for r in rows), default=0)} columns, lost {len(lost)}, twice "
                                   f"{len(twice)}")
                        if lost:
                            out.append("lost: " + " ".join(lost)[:width])
                        out.append("```")
                        out += [(" | ".join(r))[:width] for r in rows]
                        out.append("```")
                out.append("")
    Path(path_md).write_text("\n".join(out) + "\n")
    print(path_md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    r = sub.add_parser("run")
    r.add_argument("pages", nargs="*", help="SOURCE:PAGE (default: the trial pages)")
    sub.add_parser("compare")
    args = ap.parse_args()
    if args.cmd == "fetch":
        fetch()
    elif args.cmd == "run":
        targets = [(p.rsplit(":", 1)[0], int(p.rsplit(":", 1)[1])) for p in args.pages] or \
                  [(s, p) for s, pages in TRIAL.items() for p in pages]
        run(targets)
    elif args.cmd == "compare":
        compare()


if __name__ == "__main__":
    main()
