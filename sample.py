"""AUDIT LAYER final proof sample (lead 20 Nov). Usage: python3 -I sample.py <seed>
Draws 59 random points and 59 random other_requirements (no_point units) from the FINAL points.json with the given
seed; writes sample.json {seed, points:[ids], no_point:[unit ids], points_sha256}. Then:
  OUT=full/proof-<seed> node layer.mjs sample-build full/draft sample.json  (owner submits; collect; python3 -I verify.py)
n = 59: P(0 errors in 59 | error rate >= 5 %) < 5 %  (ln 0.05 / ln 0.95 = 58.4).
"""
import json, random, sys, hashlib

HERE = "/root/audit-admin/audit-layer"


def main(seed):
    raw = open(f"{HERE}/points.json", "rb").read()
    P = json.loads(raw)
    r = random.Random(seed)
    pts = r.sample([p["id"] for p in P["points"]], 59)
    nps = r.sample([f'{o["item"]}#{o["unit"]}' for o in P["other_requirements"]], 59)
    json.dump({"seed": seed, "points": pts, "no_point": nps, "points_sha256": hashlib.sha256(raw).hexdigest()},
              open(f"{HERE}/sample.json", "w"), indent=1)
    print(f"sample.json: seed {seed}, 59 points + 59 no_point")


if __name__ == "__main__":
    main(int(sys.argv[1]))
