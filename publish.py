"""Build the CLEAN PUBLISH TREE (lead 20 Nov) for github.com/maglesT/audit-insp-syste, branch audit-layer.
Usage: python3 -I publish.py   -> /root/audit-admin/audit-layer-publish (fresh git repo, ONE commit, no history)
Included: code, docs, LICENSE + THIRD_PARTY_NOTICES.md, blocks.json (shown regulation text: Schedule M / FDA / EU only),
final drafts, points.json, owner-review.json, proof.json, sample / census id lists, frozen prompts, and the check
results (check/checks.json, build-report.json, batches.json) of every check folder.
Excluded (stay local): agent task files and outputs (full/tasks, full/results, */repair, */draft, */merged, rounds/,
full-old-p1/, calibration folders), request batches (batch-*.jsonl), node_modules, __pycache__, .git history.
Then scans the tree: keys (sk-ant-, AIza, ghp_, xox, private keys) and WHO / PIC/S-only 10-word runs (whoscan.py).
Writes publish-report.json. It does NOT push."""
import os, re, json, shutil, subprocess, glob, sys

SRC = "/root/audit-admin/audit-layer"
DST = "/root/audit-admin/audit-layer-publish"
TOP = ["LICENSE", "THIRD_PARTY_NOTICES.md", "HANDOVER.md", "PIPELINE-NOTES.md", ".gitignore", "blocks.json",
       "points.json", "owner-review.json", "proof.json", "sample.json", "final-status.json", "a9-fixes.json",
       "np-2of3.json", "proof-split.json", "who-hits.json", "np-census.json", "np-op2.json", "np-op3.json",
       "recheck2.json", "recheck3.json", "recheck4.json", "calib-ids.json", "r2-ids.json", "r3-ids.json",
       "known-errors.json", "proof-label.json", "recheck5.json", "recheck6.json", "np-class3.json", "beta-approved.json", "full-r3-prompt.txt", "full-r3-schema.json"]
FULL = ["full/fallback/drafts.json", "full/prompt.lock.json", "full/prompt-frozen.txt", "full/check-prompt-frozen.txt", "full/state.json",
        "full/draft/drafts.json"]
KEY = re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}|AIza[0-9A-Za-z_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}|xox[bp]-")
README = """# GMP audit layer (Medhanta Audit Checklist)

**Status: BETA - independently checked, not yet expert-certified.** Last fresh proof sample (seed 20261124, 2-of-3
opinions per fail): 117/118 correct (audit points 58/59, other requirements 59/59). All 8510 duty units of the clause
library are shown, as an audit point or as an "Other requirement (check the clause)". Code checks V1-V9 and V11-V14
pass (see proof.json and beta-approved.json). A GMP expert reviews a sample before any certified release.

Audit points (question, what to verify, evidence, grade hint, the exact regulation clauses behind each point and the
other regulators' references) built over the proven GMP clause library (Schedule M, US FDA 21 CFR, EU GMP).

- `points.json`: the audit points and the "Other requirements (check the clause)" list.
- `owner-review.json`: items kept out of the points until the owner decides.
- `proof.json`: code checks (verify.py V1-V12) and the independent proof sample with all opinions (2-of-3 rule).
- `blocks.json`: the regulation clauses the points were drafted from (Schedule M / FDA / EU text only).
- Code: blocks.py, layer.mjs (API batches), waves.mjs (agent drafting), assemble.py, merge.py, finalize.py, verify.py.
- HANDOVER.md: the full method, decisions and numbers.

See LICENSE (proprietary) and THIRD_PARTY_NOTICES.md (regulation texts; WHO / PIC/S are cited by number only).
"""


def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)
    os.makedirs(DST)
    files = [f for f in TOP if os.path.exists(f"{SRC}/{f}")]
    files += [os.path.basename(f) for f in glob.glob(f"{SRC}/*.py") + glob.glob(f"{SRC}/*.mjs")]
    files += [f for f in FULL if os.path.exists(f"{SRC}/{f}")]
    for d in sorted(glob.glob(f"{SRC}/full/*/")):
        rel = os.path.relpath(d, SRC)
        for name in ("check/checks.json", "build-report.json", "batches.json", "scope.json", "ids.json"):
            if os.path.exists(f"{d}{name}"):
                files.append(f"{rel}/{name}")
    files = sorted(set(files))
    for f in files:
        os.makedirs(os.path.dirname(f"{DST}/{f}") or DST, exist_ok=True)
        shutil.copy2(f"{SRC}/{f}", f"{DST}/{f}")
    open(f"{DST}/README.md", "w").write(README)
    files.append("README.md")
    sys.path.insert(0, SRC)
    import whoscan
    only = whoscan.only_set()
    keys, who = [], []
    for f in files:
        t = open(f"{DST}/{f}", encoding="utf-8", errors="ignore").read()
        keys += [f"{f}: {m.group(0)[:10]}..." for m in KEY.finditer(t)]
        if whoscan.hit(t, only):
            who.append(f)
    env = dict(os.environ, GIT_AUTHOR_NAME="Claude", GIT_AUTHOR_EMAIL="noreply@anthropic.com",
               GIT_COMMITTER_NAME="Claude", GIT_COMMITTER_EMAIL="noreply@anthropic.com")
    run = lambda *a: subprocess.run(a, cwd=DST, env=env, check=True, capture_output=True, text=True)
    run("git", "init", "-q", "-b", "audit-layer")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "GMP audit layer: audit points, checks and proof (clean publish tree)\n\n"
        "Co-Authored-By: Claude <noreply@anthropic.com>")
    size = subprocess.run(["du", "-sh", "--exclude=.git", DST], capture_output=True, text=True).stdout.split()[0]
    rep = {"tree": DST, "files": len(files), "size": size, "key_hits": keys, "who_pics_hit_files": who,
           "commit": run("git", "rev-parse", "--short", "HEAD").stdout.strip()}
    json.dump(rep, open(f"{SRC}/publish-report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    os.chdir(SRC)
    main()
