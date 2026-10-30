"""Sentence embeddings for candidate search (D21): a small model, pinned and fingerprinted, run locally on CPU.

  python3 tools/search/embed.py fetch      # download the pinned files into models/ (not in git) and verify them
  python3 tools/search/embed.py check      # verify the local files against their sha256

The model is BAAI/bge-small-en-v1.5 (MIT licence) at a fixed revision, run as ONNX with onnxruntime; nothing leaves
the environment once the files are here. A file whose sha256 does not match the pin is refused, so a run can
only use exactly the model that was measured.
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"
MODEL = {
    "name": "bge-small-en-v1.5",
    "repo": "BAAI/bge-small-en-v1.5",
    "revision": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
    "files": {
        "onnx/model.onnx": "828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35",
        "tokenizer.json": "d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66",
        "config.json": "094f8e891b932f2000c92cfc663bac4c62069f5d8af5b5278c4306aef3084750",
    },
    # bge v1.5: a short instruction before queries (not passages) for retrieval
    "query_prefix": "Represent this sentence for searching relevant passages: ",
    "max_tokens": 512,
}


POOLING = "cls-l2"                                     # what encode() does; part of the cache fingerprint


def model_dir(model=MODEL):
    return MODELS / model["name"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(model=MODEL, directory=None):
    """Problems with the local model files (missing or wrong sha256); empty when the model is ready."""
    directory = Path(directory or model_dir(model))
    out = []
    for name, want in model["files"].items():
        path = directory / Path(name).name
        if not path.exists():
            out.append(f"{path.name}: missing")
        elif sha256(path) != want:
            out.append(f"{path.name}: sha256 does not match the pin")
    return out


def available(model=MODEL):
    return not check(model)


def fetch(model=MODEL, directory=None, opener=urllib.request.urlopen):
    """Download the pinned revision's files and verify each; a mismatch is deleted and refused."""
    directory = Path(directory or model_dir(model))
    directory.mkdir(parents=True, exist_ok=True)
    for name, want in model["files"].items():
        path = directory / Path(name).name
        if path.exists() and sha256(path) == want:
            continue
        url = f"https://huggingface.co/{model['repo']}/resolve/{model['revision']}/{name}"
        tmp = path.with_suffix(path.suffix + ".part")
        try:
            with opener(url, timeout=120) as response, open(tmp, "wb") as f:
                while block := response.read(1 << 20):
                    f.write(block)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        if sha256(tmp) != want:
            tmp.unlink()
            raise SystemExit(f"{name}: downloaded file does not match the pinned sha256; refused")
        tmp.replace(path)
    return directory


class Embedder:
    """Unit-length CLS embeddings from the pinned ONNX model."""

    def __init__(self, model=MODEL, threads=None):
        problems = check(model)
        if problems:
            raise SystemExit("embedding model not ready (python3 tools/search/embed.py fetch): " + "; ".join(problems))
        import onnxruntime
        from tokenizers import Tokenizer
        self.model = model
        directory = model_dir(model)
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.enable_truncation(model["max_tokens"])
        self.tokenizer.enable_padding()
        options = onnxruntime.SessionOptions()
        if threads:
            options.intra_op_num_threads = threads
        self.session = onnxruntime.InferenceSession(str(directory / "model.onnx"), options,
                                                    providers=["CPUExecutionProvider"])
        self.inputs = {i.name for i in self.session.get_inputs()}

    @property
    def fingerprint(self):
        """Name, revision and a hash of everything that shapes a vector (files, prefix, truncation, pooling), so
        cached vectors are reused only for exactly the same encoding."""
        settings = json.dumps({k: self.model[k] for k in ("files", "query_prefix", "max_tokens")}, sort_keys=True)
        digest = hashlib.sha256((settings + "|" + POOLING).encode()).hexdigest()[:12]
        return f"{self.model['name']}@{self.model['revision'][:12]}-{digest}"

    def encode(self, texts, query=False, batch=32):
        import numpy as np
        prefix = self.model["query_prefix"] if query else ""
        out = []
        for i in range(0, len(texts), batch):
            enc = self.tokenizer.encode_batch([prefix + t for t in texts[i:i + batch]])
            feed = {"input_ids": np.array([e.ids for e in enc], dtype=np.int64),
                    "attention_mask": np.array([e.attention_mask for e in enc], dtype=np.int64)}
            if "token_type_ids" in self.inputs:
                feed["token_type_ids"] = np.array([e.type_ids for e in enc], dtype=np.int64)
            hidden = self.session.run(None, feed)[0]
            cls = hidden[:, 0, :]
            out.append(cls / np.linalg.norm(cls, axis=1, keepdims=True))
        return np.vstack(out) if out else np.zeros((0, 384), dtype=np.float32)


if __name__ == "__main__":
    if sys.argv[1:] == ["fetch"]:
        print(fetch())
    elif sys.argv[1:] == ["check"]:
        problems = check()
        print(json.dumps(problems or "ok"))
        sys.exit(1 if problems else 0)
    else:
        sys.exit("usage: python3 tools/search/embed.py fetch|check")
