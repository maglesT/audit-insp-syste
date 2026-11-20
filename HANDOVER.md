# Audit layer: build brief (lead audit-admin-63, 19 Nov 2026; owner approved "yeah")
Read CLAUDE.md (entry "OWNER 19 Nov (late) ... AUDIT LAYER") and the research summary below. Work ONLY in
/root/audit-admin/audit-layer/ (read-only elsewhere). Report to the owner (plain, short) and to the lead.

WHY: real checklists (FDA CP 7356.002 six systems; FDA ORA guides "Determine/Evaluate/Review..."; PIC/S aide-memoires
"show me / what evidence" questions with a reference column; CDSCO risk-based inspection "Specify/Describe/Verify",
rating 2/1/0/X; APIC aide-memoire questions + applicability/compliance/documentation columns) never show the raw
regulation sentence as the item. Items are actions/questions about evidence, regulation in a reference column,
principles turned into evidence questions, several clauses per line, findings graded critical/major/other.

INPUT (proven, unchanged): merged/checklist.json (4,032 items), merged/checkpoints.json (FINAL marks: 8,510 duty,
2,118 information units), audience.json, plant-types.json. NEVER use merged/sources.json WHO/PIC/S text.
OUTPUT: audit-layer/points.json: per point {id, area, system (FDA 6), plant_types (union rule: point shown if its
clauses' scope matches; never widen a narrower clause), audience, question (own words), verify (what to check),
evidence (documents/records/observation), clauses [item ids + unit n's], grade_hint (optional)}.
RULES:
- Group units only within one regulator section first (Schedule M, FDA, EU separately); a point may cover several
  units/clauses of the same section checked by the same evidence. Cross-regulator merging later, only via verified refs.
- A point must say NO MORE than its units (no added numbers, frequencies, conditions) and must not drop a condition
  or scope word; "should" stays a recommendation in wording ("Is ... (recommended)?" or "Verify ... where ...").
- Every duty unit covered by >= 1 point (code check). Information units: context only.
- Own words only; never copy PIC/S, CDSCO or APIC text.
METHOD: draft with the Claude API (Message Batches; key .secrets/anthropic.env, never print; the OWNER submits each
batch over SSH, sessions are blocked from submitting). Model: OWNER 19 Nov: "dont use sonnet for this" -> use claude-opus-5-5
for drafting and checking the audit layer (one-time build; plants don't pay per point). Calibrate on ~50 sections first.
Then independent blind checks of every point: (a) no-more/no-less vs its units, (b) coverage, (c) question is
answerable with the evidence; fix causes; then a fresh 59-point sample with 0 errors. Budget: Anthropic cap US$150,
~US$70 already used; this phase <= US$40; ask the lead before more.
DELIVER: points.json + verify.py (proof.json) + an owner sample (30 points, before/after view).

## STATE (session audit-layer-65, 19 Nov 2026; lead now audit-admin-2c)
Files: blocks.py -> blocks.json (1087 blocks; B1 one regulator/part/section path + same area/plant types/audience;
all 8510 duty units in exactly one block; <= 30 duty units per block; FDA system from area, table in blocks.py).
layer.mjs: draft-build [calib|all|ids.json] / check-build <draftDir> / submit --yes (OWNER only) / collect (OUT=<dir>).
assemble.py <draftDir>: code checks A1-A4 + coverage -> drafts.json. node_modules = symlink to api-proof/node_modules.
Done: calib-draft/ built (50 blocks, 503 duty units, est. US$1.56). Waiting: owner submits
  cd /root/audit-admin/audit-layer && OUT=calib-draft node layer.mjs submit --yes
Next: OUT=calib-draft node layer.mjs collect; python3 -I assemble.py calib-draft; OUT=calib-check node layer.mjs
check-build calib-draft (owner submits); write score.py (check results -> error classes); fix prompt causes; full
estimate to the lead; then all blocks; then fresh 59-point sample with 0 errors; points.json + verify.py + owner sample.
Spend this phase so far: US$0 (count_tokens only).
Lead 19 Nov: FDA system map APPROVED. Calib draft GO. OUTPUT CONTRACT (web-59, web/build_data.py): points.json loaded only
when proof.json has "PROVEN": true; a list (or {"points":[...]}) of {id, area, question, clauses:[{item:<checklist id>,
units:[n...]}], system, plant_types, audience (write on EVERY point), verify, evidence (string or list), grade_hint}.
Unknown item ids / unit numbers fail the site build. After calibration send the lead: code-check numbers, check-batch
command + estimate, full-run estimate.
Lead rulings 19 Nov (after calibration draft, US$1.13 actual): (1) QUESTION own words (10-word guard A4); "Verify that"
may keep exact SchM/FDA/EU terms; verify_copy_run kept. (2) modality field set by the model; code checks
"(recommended)" matches it; blind check judges it. (3) full-run check = per BLOCK (layer.mjs check-block-build).
(4) OWNER: no_point [{unit, reason}] allowed (R8); coverage = point OR no_point; blind check judges no_point; shown as
"Other requirements (check the clause)" per area -> points.json "other_requirements". Report no_point % (> 5 % = warn).
calib-check/ built (341 per-point checks, est. US$3.59): owner submit pending. Do NOT re-run assemble.py on calib-draft
(calib-check's guard holds its drafts.json hash; the calib drafts have no modality/no_point fields).
CALIB CHECK (per point, US$3.15): pass 260/341; no_more 40 (mostly evidence implying extra duties), own_words 29 (verify
copies: allowed by ruling -> checker now judges the QUESTION only), no_less 17 (dropped duty/cross-ref/scope word).
Fixes in layer.mjs: R1e, R2 (cross-refs, scope words, split), R3 inherit + R3p permission, checker reason "" on PASS.
A6 in assemble.py (point XOR no_point). calib2-draft/ built (same 50 blocks, calib-ids.json; est US$1.74) -> owner
submit; then OUT=calib2-check node layer.mjs check-block-build calib2-draft. Full draft input = 3.58M tokens (exact).
OWNER CHANGE 19 Nov: calib2-draft NOT submitted (never send it). Calibration round 2+ runs with Claude Code agents
(agentio.mjs; same prompts/schemas as layer.mjs; out.json per agent + last5 tail echo). Round 2 = rounds/r2: 33 blocks
with a round-1 fail + 10 clean (r2-ids.json), 4 draft agents -> draft-gather -> assemble.py rounds/r2/draft ->
check-inputs (4 FRESH blind agents) -> check-gather -> score.py rounds/r2/check rounds/r2/draft. Iterate until clean,
then one ~US$1 API calibration to confirm, then the full API run.
ROUND 2 (agents): points 273/296 = 92.2 % (no_more 10, no_less 10, own_words 3, answerable 0); no_point 31 = 6.5 %,
30/31 confirmed; controls 0 fails. Fixes (draft + checker, same borderline rules): never split a unit; keep pointers
"(see Section ...)" and qualifiers (preferably, as far as possible); conditional permission -> "Where X ... (recommended)";
rule (e) no content of unlisted units; R5 question rephrased; R8 authority agreement = point. agentio.mjs echo fixes
(labels stripped, raw-text tail accepted, token cap 20).
ROUND 3: rounds/r3 (r3-ids.json: 10 still-failing + 15 new seeded blocks), 3 draft agents running.
ROUND 3 (agents): 164/172 = 95.3 % (new blocks 51/53), copies 0, no_point 2.2 % (new 1.35 %), 6/6 confirmed. Lead
ACCEPTED; no 4th round. A7 code check (should-point must not use must/shall/as required/is required) - also in final
verify.py. Repair loop built + dry-run tested: layer.mjs repair-build <draftDir> <checkDir> -> merge.py <draftDir>
<repairDir> <newDir> (stable ids <block>-R<round><k>, new-ids.json) -> assemble.py <newDir> -> check-block-build
<newDir> <newDir>/new-ids.json. Per-point check-build <draftDir> <ids.json> = fresh 59-point proof sample.
API CONFIRM: api3-draft (r3-ids.json 25 blocks, est US$0.66) GO by lead; owner submit pending; then check-block-build.
OWNER 19 Nov: confirmation test with FABLE AGENTS (not API): rounds/r3f = same 25 blocks, final prompts (incl. FDA
pointer example + A7 sentence, added after Opus r3), 3 Fable draft agents -> 3 fresh Opus blind checkers. api3-draft
(Opus API) deleted unsubmitted. layer.mjs: DRAFT_MODEL env (default Opus; checks always Opus), per-model prices, refusal count.
OWNER PRIORITY 19 Nov (lead P1-P4): useless point worse than missing; weak/forced -> no_point (may exceed 5 %); P2 a
no_point whose failure would likely be a CRITICAL/MAJOR finding must be a point (checker field "major"); P3 checker
criterion "useful"; P4 final 59 sample judged no_more/useful first. In layer.mjs (R8 + checker) and score.py.
BUG FIXED: assemble.py had a comment mid-line that dropped block/regulator/part from points (since the stable-id
edit); drafts re-assembled (r2, r3, r3f, r3o); scores unaffected.
Fable test: r3f drafts (Fable agents, old R8 wording) 187 points, 0 code problems, no_point 2.2 %. Checks with the NEW
checker (useful + major) on r3f AND on the Opus r3 drafts (copy rounds/r3o) by 4 fresh Opus agents: running.
FABLE TEST RESULT (same new checker, fresh Opus agents): Fable drafts 183/187 = 97.9 % (no_more 1, answerable 2, useful 1),
Opus r3 drafts 168/172 = 97.7 % (no_more 3, no_less 1); no_point 2.2 % both, 5/6 confirmed, 0 P2 major overrides.
Checker noise ~±2 % (same Opus drafts 95.3 % -> 97.7 %). Projection: (a) Fable draft + Opus check ~US$71; (b) Opus
draft + Opus check ~US$47; spent so far ~US$77 of the 150 cap. Recommended (b). Waiting for the lead/owner choice; then
OUT=full-draft node layer.mjs draft-build all (DRAFT_MODEL=claude-fable-5-2 if Fable chosen).

## FULL RUN (owner choice C, 19 Nov): Fable 5.2 AGENTS draft all 1087 blocks; Opus API checks in parts (owner submits)
Driver: waves.mjs (state full/state.json; prompt FROZEN full/prompt.lock.json sha256 a2b9a509...; prompt-frozen.txt).
Loop per wave: `node waves.mjs plan 4` -> 4 Agent calls (model "fable", general-purpose, background; prompt: read
full/tasks/tNNN/task.md, write only out.json there) -> when all 4 finish: `node waves.mjs gather` (bad blocks back to
pending) -> `node waves.mjs build && python3 -I assemble.py full/draft` -> code-check failures: `node waves.mjs redo <ids>`.
Dead agent: `node waves.mjs release tNNN`. Max 4 agents at a time; pause and tell the lead on any usage-limit warning.
API CHECK PARTS (~300 blocks each, as drafts finish): snapshot full/draft into full/part-N/draft (drafts.json), then
OUT=full/part-N/check node layer.mjs check-block-build full/part-N/draft <ids of that part's points+no_point units>;
send the lead the estimate + owner command; collect -> score.py -> repair by Fable agents -> re-check in next part.
Report to the lead per check part only. R6 clarified before freezing (cross-refs of a unit stay in verify).
Wave 1: t001-t004 running.
Progress 19 Nov: rolling pool (a new task as each agent finishes; max 4). 53 blocks done (t001-t004, t006), 0 bad.
Code checks: 224 points, coverage 0 uncovered, 3 A4 copied questions (B0014-P04, B0040-P07, B0040-P21) -> handled
point-wise in the repair round (repair-build includes code problems), not whole-block redo. no_point 16.4 % in these
early principle blocks (Part pointers "Part I applies", lead-ins, general aims under P1); the API check judges each
(P2 major override). Running: t005, t007, t008, t009.
LEAD RULE REF1 (for the final points.json + verify.py): every point and other_requirement gets "references" = union of
its clause items' references (merged/checklist.json). EXCEPTION, 5 joined items whose refs come "via" one sub-clause:
EU C7 7.4 (7.4-7.8 -> PIC/S 7.4/7.4.1/7.4.2/7.4.3/7.5), EU A2 A8 (+A9), EU C5 5.35 (+5.36), EU C6 6.27 (+6.28),
SchM-I-19.4.1 (+19.4.2; WHO 17.4, via=None): include a ref only if the point covers units whose text lies in the
ref's "via" sub-clause (map units to sub-clauses by text span, in code). SchM-I-19.4.1: WHO 17.4 only if the point
covers ALL its duty units, else decide by text in a hand file with the reason. verify.py check: every point ref is in
its items' refs; joined-item refs pass the via/span rule. No FDA cross-refs exist.
Progress: 113 blocks done (t001-t010), 0 bad; running t011-t014.
PAUSED by lead 19 Nov (no_point 20.9 %): no new tasks until re-freeze decision; t014-t017 finishing. Check part 1 GO (full/part-1).
Paused state: 193 blocks done (t001-t017), 0 pending tasks running.

## FULL RUN v2 (owner final 19 Nov: "use what you were using before" + "just keep the checking that something major
doesn't get missed")
DRAFT prompt = the exact ROUND-3 prompt Fable used in the 25-block test (rounds/r3f task.md; copy full-r3-prompt.txt,
full-r3-schema.json; no P1 wording; includes A7 sentence + FDA pointer example). CHECKER = round-3 criteria (no_more,
no_less, answerable, own_words) + "major" on every no_point (major -> FAIL -> repaired into a point); "useful" DROPPED.
Frozen: full/prompt.lock.json draft sha256 0b832b4cfa614b01ca2d8be8f9b79a79742e589dd7323b605239ee7a2a202fee,
check sha256 708e2c8c127d49f5b756053d8eb59f081478eb8d7f0eccabf1cf1f7964061b5c (waves.mjs guards both).
Old run (P1 prompt, 193 blocks) archived in full-old-p1/ (reference only; its part-1 check build DELETED, never
submitted). The R8 P1/must-point test (rounds/r8) was stopped unfinished. All 1087 blocks re-drafted with v2.
Check part 1 = first ~300 v2 blocks (owner submits). Wave 1 v2: t001-t004 running.
OWNER RULE (lead 19 Nov): ONE repair + re-check only. Anything still failing (point or no_point), or marked
unclear/borderline by the checker -> OWNER REVIEW list: audit-layer/owner-review.json + readable .md in
/root/screenshots/audit/ (item id + ref, unit text, current point or no_point reason, checker reason). Kept OUT of
points.json until the owner decides (they stay plain clause items). Report the count with each part.
Check PART 1 built (v2): full/part-1 = B0001-B0286 snapshot (draft/raw.json + drafts.json; ids.json = 1380 clean
points + 154 no_point units; 12 code-flag points go straight to repair). 285 requests, est US$9.50 -> sent to the lead
for the owner submit. Drafting at 322 blocks (t001-t030 gathered; t030-t033 running).
PART 1 RESULT: points 1357/1380 = 98.3 % (no_less 13 mostly dropped cross-refs, no_more 9, answerable 1); no_point 154
(7.7 %), 131 confirmed, 12 MAJOR overrides + 11 point-possible; 12 code flags. Cost US$4.66 (840 out tok/block); full
check projection ~US$17.8. REPAIR (one round, Fable agents): waves.mjs repair-tasks full/part-1 -> full/part-1/repair
r01, r02 (42 blocks, 67 units) running -> repair-gather -> merge.py full/part-1/draft full/part-1/repair
full/part-1/merged -> assemble -> re-check new ids inside the part-2 batch; still failing -> owner-review.
Drafting: 412 done (t001-t038), running t039, t040.
PART 1 REPAIR done (Fable r01, r02; 42 blocks): full/part-1/merged = 1416 points, 0 code problems, 0 uncovered,
no_point 131 (6.55 %); 59 new items (full/part-1/merged/new-ids.json) -> re-check inside the part-2 batch. Merged
data written back into full/results/<id>.json (points carry stable ids; repaired ids <block>-R1NN).
Check PART 2 built: full/part-2 (scope.json: B0287-B0564 + 42 repaired part-1 blocks; ids.json 1878 items incl 59
part-1 repaired). 320 requests, est ~US$5.2 at measured rate (script says 11.42). Sent to lead for the owner submit.

## SAVE POINT (owner asked "save the work", 19 Nov)
State on disk: full/state.json (per-block status), full/results/<id>.json (every drafted block, repaired part-1 blocks
included), full/tasks/tNNN (agent tasks + outputs), full/part-1 (checked + repaired + merged), full/part-2 (built,
waiting for the owner submit; watcher writes full/part-2/collect.log). Frozen prompts: full/prompt.lock.json.
To resume in a new session: `node waves.mjs status`; gather any finished tasks (`node waves.mjs gather`); assigned
tasks whose agent is gone -> `node waves.mjs release tNNN`; then continue the plan/agent loop (max 4 Fable agents).
Part 2: when the batch has ended -> `OUT=full/part-2/check node layer.mjs collect` -> `python3 -I score.py
full/part-2/check full/part-2/draft` -> repair (waves.mjs repair-tasks full/part-2) -> merge -> write back (see part 1)
-> part-1 repaired items that fail again go to owner-review.json (not built yet).
Backup: /root/audit-admin/audit-layer-backups/audit-layer-<time>.tar.gz
GIT (owner "save the work ... in repo", 19 Nov): local repo in audit-layer/ (branch main; first commit db1c55f; author
Claude <noreply@anthropic.com>; message ends with the CLAUDE.md Co-Authored-By line; node_modules + *.log ignored).
No remote yet: asked server-lead-5a for a deploy key + the owner's PRIVATE repo (never the public audit-insp-syste).
Commit after each check part / repair round.
Remote (when the owner confirms key + private repo): git@github-audit-layer:maglesT/audit-layer.git (owner makes key + ssh alias himself; do not push anywhere else; do not generate keys).
20 Nov 10:07 UTC: weekly plan limit hit at ~935 blocks (t093, t096 stopped but had written out.json; gathered). Limit reset 10:00 UTC; resumed t097-t100. 971 done, 116 pending before this wave.
20 Nov: FULL DRAFT DONE: 1087/1087 blocks, 6400 points, no_point 545 (6.4 %), 21 code-flag points, 0 uncovered. Part-2 repair r01 done, r02 running. Next: merge part-2 repair, build part 3 = B0565-B1087 + part-2 repaired items.
Part 2 repair merged (round 2 ids <block>-R2NN; 40 new items; 2 still A4: B0488-R201, B0560-R201 -> owner-review if they stay
flagged). Check PART 3 built: full/part-3 (scope.json: B0565-B1087 + 33 repaired part-2 blocks; ids.json 3598 items),
556 requests, ~US$10 at measured rate (script 21.04). Sent to lead for the owner submit.
FINAL TOOLS (20 Nov): finalize.py -> points.json {points, other_requirements} (web-59 contract + "references" by
REF1, incl. joined-item via/span rule: sub-clause starts found from merged/sources.json source_text of EU/SchM
items; "A8" printed as "8."), owner-review.json + /root/screenshots/audit/audit-layer-owner-review.md, final-status.json
(pending items). verify.py -> proof.json (V1-V10 + pending; PROVEN only if all pass). sample.py <seed> -> sample.json
(59 points + 59 no_point from the FINAL points.json; lead: fresh seed, one item per request) -> OUT=full/proof-<seed>
node layer.mjs sample-build full/draft sample.json -> owner submits -> collect (raw.json in full/proof-<seed>) ->
verify.py. CHECK_ORDER in finalize.py: part-1, part-2, part-3, final-recheck (the re-check of part-3 repairs).
Tested on partial data: V1 V3-V9 PASS; V2/V10/pending wait for part 3.
Part-3 repair merged (round 3, 101 new items, B1029-R301 code flag). FINAL RE-CHECK built: full/final-recheck (82 requests, ~US$0.6) -> owner submit.
FINAL RE-CHECK: 95/101 pass. finalize: 6434 points + 496 other, owner review 13 (page /root/screenshots/audit/audit-layer-owner-review.md), pending 0. verify V1-V9 PASS. PROOF sample seed 20261120 built (full/proof-20261120, 118 requests) -> owner submit -> collect -> verify.py.
PROOF SAMPLE seed 20261120 (US$0.72): FAILED (points 1/59, no_point 6/59, all 6 MAJOR). Fixes: (1) A8 code rule
(question keeps softeners; assemble.py + verify V11): 138 points; 133 repaired by Fable agents in full/a8-fix/repair
(r01-r03 running), 5 already-repaired -> owner review. (2) per-item NP census of all 496 other_requirements
(full/np-census, sample-build with np-census.json; ~US$2.5) -> owner submit -> FAILs repaired into points.
(3) then per-item re-check of all repaired items, finalize, FRESH sample (new seed). verify.py now also V11.
Proof-sample custom_ids are P001/N001 (API pattern ^[a-zA-Z0-9_-]{1,64}$); key.json maps them back (verify uses it).
A8 repair merged (round 4, 133 new points, 0 code problems; written back). census2checks.py converts np-census results; finalize CHECK_ORDER += a8-fix, np-census, np-fix, recheck2. Waiting: owner submits np-census.
np-fix merged (round 5, 69 new points; B0684-R501 A8 -> owner review). recheck2 built (per item, 202 points; recheck2.json) -> owner submit -> python3 -I census2checks.py full/recheck2 -> finalize -> verify -> fresh sample.
recheck2: 186/202 pass (US$1.54); finalize: 6481 points + 425 other, owner review 35; verify V1-V9, V11 PASS. Fresh sample seed 20261121 built (full/proof-20261121).
FRESH SAMPLE seed 20261121 (US$0.74): FAILED points 2/59 (B0516-P04 evidence, B0365-P04 modality), no_point 2/59 (SchM-XIII-11.2#6, EU C5 5.21#7; both PASSED in the census an hour earlier = checker inconsistency). Proposed to lead: Part XIII 'may be divided' class (13 units) -> points; borderline rule = error only if 2 more per-item opinions also fail (majority of 3); then one fresh sample. Waiting for decision. Phase spend US$32.08.
LEAD/OWNER 20 Nov: 2-of-3 rule approved. A9 (a9.py, assemble + verify V12): 14 mechanical fixes (a9-fixes.json) + 2
repaired. Part XIII 13 room-list units -> points (fix3, round 6). 2-of-3: layer.mjs opinion-build <sampleDir> (OUT=
<sampleDir>/opinions), verify.py judge_sample() -> proof-split.json (split items -> owner review by finalize) + proof.json
(rule + all opinions). recheck3 (13 points, per item) built -> owner submit -> census2checks.py full/recheck3 -> finalize
-> verify -> sample.py <new seed> -> sample-build -> submit -> (opinions if FAILs) -> verify.
recheck3: 6/13 pass; 7 Part XIII 'may be divided' -> owner review (checker contradicts itself on this class). FINAL 6485 points + 412 other, review 42, pending 0; verify all PASS but V10. Fresh sample seed 20261122 built (full/proof-20261122).
OWNER 20 Nov: push to the EXISTING repo github.com/maglesT/audit-insp-syste ("use this repo only but add licenses"),
which CLAUDE.md lists as PUBLIC; owner informed and chose it. LICENSE (proprietary, all rights reserved) +
THIRD_PARTY_NOTICES.md (Schedule M s.52(1)(q)(i); EU CC BY 4.0 with changes note; FDA public domain; EMA / ICH "to be
confirmed by the lawyer"; WHO / PIC/S numbers only, no text; not-affiliated note) added. Push target: NEW branch
"audit-layer" (never main). This server has NO write access (https remote, no key, no gh): the owner adds a deploy key.
Sample 20261122 under 2-of-3: points 59/59 PASS; no_point 2 ERROR (EU A1 4.4#3, EMA MAH-RP 5.4 ¶9#3; both passed the 1-opinion census). Proposed: 2nd opinion for all 412 other_requirements (~US$2.5), 3rd only on disagreement; ERROR -> repair; split -> owner review; then fresh sample. Asked lead (budget ~US$37 of 40).
LEAD: 2nd-opinion route approved (full/np-op2, 412 req). GitHub push ON HOLD until the lead confirms with the owner (public repo concern), even if a key appears.
20 Nov: no_point 2-of-3 done (np-op2 403/412 agree; np-op3: 5 ERROR + 4 split -> np-2of3.json; split listed via finalize).
who-fix (21 rephrased; whoscan.py --points = 0) and np-fix2 (7 ERRORs -> points) merged; recheck4 (28 points, per item)
built -> owner submit -> census2checks full/recheck4 -> finalize -> verify -> fresh sample -> publish tree + scans -> lead go.
Deploy key made by the OWNER (~/.ssh/audit_insp_deploy, alias github-audit-insp); remote
git@github-audit-insp:maglesT/audit-insp-syste.git, branch audit-layer; push only after lead's go (clean single-commit tree).
publish.py: clean tree /root/audit-admin/audit-layer-publish (85 files, 20 MB, 1 commit, keys 0, WHO 0) -> rebuild after the proof sample, then push only on the lead's go.
Sample 20261123 (2-of-3): 3 ERROR (B0045-P01 no_less scope negation; B0321-R501 recommended on must; EU C1 QM-intro#2 no_point) -> NOT PROVEN, NO PUSH. Options A/B/C sent to the lead. Spend US$36.36.
Option A: A10/A11 (V13/V14); class3 (15 per item, 2 FAIL); fix4 merged (4 points); recheck5 built (4) -> then the LAST fresh sample; if it fails: STOP, write the option-B label in proof.json, no push.
LAST SAMPLE seed 20261124 (option A done): points 58/59 (B0824-P01 ERROR 3/3), no_point 59/59 -> NOT PROVEN. Per owner:
STOP, no push. proof-label.json (honest status, history of all samples, estimate ~1-2 %, recommendation) is written into
proof.json by verify.py. known-errors.json moves B0824-P01 to owner review. FINAL: 6491 points + 403 other, review 49.

## CURRENT STATE (20 Nov, end of session audit-layer-65) - read this first
- Result: 6491 audit points + 403 other_requirements (points.json); owner review 49 (owner-review.json; page
  /root/screenshots/audit/audit-layer-owner-review.md). Duty units 8510 = 8054 in points + 403 other + rest in owner review.
- verify.py -> proof.json: PROVEN false. All code checks PASS (V1-V9, V11 softeners, V12 (recommended) per sentence,
  V13 scope negation, V14 recommended-on-must; pending 0). V10 fails: last fresh sample (seed 20261124, 2-of-3 rule)
  had 1 confirmed point ERROR (B0824-P01, now in owner review). proof.json "label" (from proof-label.json) states the
  honest status, the 5-sample history and the ~1-2 % estimate.
- Owner decisions: option A done once, then STOP. NO push, NO web load (web/build_data.py loads points.json only when
  PROVEN true). A full per-item check of all points (~US$40, would reach the US$150 cap) was discussed with the owner
  and NOT ordered (my advice: keep the money; GMP expert review of a sample is planned anyway).
- WAITING: the owner's decisions on the 49 owner-review items (lead audit-admin-2c forwards them): keep / change wording /
  drop (= stays a plain clause or other_requirement). To apply: put decisions into a hand file (e.g. owner-decisions.json
  {id: {decision, new_question?, new_verify?}}), extend finalize.py to apply it (keep -> back into points; change ->
  edited point, which needs a per-item check; drop -> stays out), re-run finalize + verify, report to the lead.
- GitHub (owner chose the PUBLIC repo maglesT/audit-insp-syste, branch audit-layer; lead confirmed with the owner):
  publish.py builds the clean single-commit tree (/root/audit-admin/audit-layer-publish; last build 85 files, keys 0,
  WHO/PIC/S 0). Deploy key made by the owner (~/.ssh/audit_insp_deploy, alias github-audit-insp; remote
  git@github-audit-insp:maglesT/audit-insp-syste.git). Push ONLY with the lead's go (rebuild + rescan first; new
  branch only; never main; no force).
- Spend this phase: US$37.16 of US$40 (Anthropic cap US$150 overall).
- Local git: this folder (branch main), committed after every step; author Claude <noreply@anthropic.com>.
OWNER/LEAD 20 Nov: owner-review FALLBACK by code (full/fallback/drafts.json, 44 '-F' points, exact unit text, generic question/evidence); finalize uses a fallback only if its per-item check (full/recheck6) PASSes; verify skips V11 + V4 must-words for -F. recheck6 built -> owner submit -> census2checks full/recheck6 -> finalize -> verify -> report.
recheck6 (fallback, US$0.46): 4/44 PASS -> in points (6495); 40 FAIL (permissions / generic question). Proposed to lead: those 40 -> other_requirements ('owner review: shown as clause text'), by code. Waiting. Spend US$37.62.
LEAD 20 Nov: the 40 unresolved owner-review points shown as other_requirements ('owner review: shown as clause text'); records kept (resolved). FINAL: 6495 points + 450 other_requirements; 5 open owner-review no_point records (4 split, listed; EU A16 1.7#2). Publish tree rebuilt; waiting for the lead's go (web / push).
EU A16 1.7#2 also shown as other requirement: all 8510 duty units visible (points or other_requirements).
