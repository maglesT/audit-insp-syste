# GMP audit layer (Medhanta Audit Checklist)

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
