# Handover: read this first in every new session

Last updated: 31 October 2026, session 7 (FDA build, D47: 21 CFR 211 built and verified; next: 210, Part 11, 314.81).

## START HERE (session 8)
- **FDA build (D46/D47), owned by session 7 (session_01PybpFspEA75VUpLPy2kLTG) and its successors.** FDA first,
  document by document; nothing ships unless proven (automatic route, or the owner's review queue). The paid API
  build is NOT started and needs direct owner confirmation. Report after each document to the coordinator
  (session_01PybpFuvG6mX9B3zK3YZjZ1, send_message): items, automatic-route pass rate, review-queue size, usage.
- **Done in session 7:** PR #36 merged. PR #38 (branch `fda-build`: D47, `tools/fda/xmlprofile.py`, prompts,
  `tools/fda/review.py`, `tools/fda/status.py`, tests `tests/test_fda_xml.py`, runs) open; two independent review
  passes, all findings fixed; merge on green CI. XML profile tuned (lead-in qualifiers over all lead-in ancestors,
  sterile plant scope, lead-in coverage, cross-references are not numbers). **21 CFR 211 full build: 399 items
  (60 sections; not 107), 399 quotes exact, 0 coverage gaps, automatic route 359 (90.0 %), review queue 40**
  (`docs/fda-211-trial.md`, run `library/ai-runs/20261031T100541.543518Z-xml-draft`).
- **Branches:** PR #38 = `fda-build` (group 1 tooling + 211, 210, Part 11, 314.81, 314.70, 200, 207; main merged in
  so it is mergeable again; CI had created no runs while it conflicted with main). Merge on green CI; four
  independent review passes done, all findings fixed. Part 4 is on **`fda-part4`** (stacked): open its PR after #38.
- **Group 1 done** (`library/fda-status.json`, `docs/fda-worklist.md`), items / automatic / review: 211 399/365/34;
  210 1/0/1; Part 11 48/45/3; 314.81 104/91/13; 314.70 78/53/25; Part 200 24/18/6; Part 207 149/115/34;
  Part 4 64/16/48. Total 867 items, 704 automatic (81.2 %), 163 in the owner's review queue.
- **Owner review page (coordinator, 31 Oct):** private claude.ai artifact, slug
  f1a4b335-e5ec-4d90-993a-02abf9913cbe, with the group 1 review queue (164 items, exported with review.load /
  fingerprint / source_text; the superseded 211 trial run left out). Decisions are saved in its db collection
  `decisions`, one doc per run+id: {id, run, item_hash, decision: correct|fix|reject, by, note, at (UTC),
  statement for fix}. **To build:** `tools/fda/review.py import-artifact FILE` reads the db export (pulled with
  the artifact db tools), appends the records to `library/review/decisions.jsonl` keeping their original `at`;
  the existing rules apply (a decision counts only for a matching run and item_hash).
- **Tune next (profile only):** the lead-in check (`vision.lead_in_missing`) compares 4+ letter words exactly, so
  "If you manufacture ..." vs "When manufacturing ..." is flagged (Part 4: 32 items); allow word forms (a light
  stemmer) and re-run `xmlprofile.py recheck` on all runs. `recheck` refuses a changed source file.
- **Next after group 1:** group 2 (FDA HTML, 25 documents) needs an HTML profile (D47 D: text read directly, exact
  quote, Q&A or paragraph number): reuse xmlprofile's checks with units = Q&A entries / headed sections from the
  HTML; trial on about 20 units, tune, then document by document. Then group 3 (guidance PDFs, text first) and
  group 4 (compliance programs).
- **Status files:** `library/fda-status.json` + `docs/fda-worklist.md` (the coordinator's file; only the Status /
  Items / Auto / Review cells change, via `tools/fda/status.py`). Owner review queue: CLI `review.py next|decide|
  status RUN`; an owner-friendly page is still to build.

## Session 7 start notes (kept for reference)
- **Plan since 31 Oct (D45, D46): checklist items are drafted from PDF PAGES with vision** (page image + text layer),
  checked on page text; the parsed clause store, parser and fidelity work are FROZEN (kept for search/cross-checks).
  Read D43-D46 in `docs/decisions.md` and `docs/vision-trial.md`. CLAUDE.md lets drafting/verifier agents get images.
- **Merged this session:** PR #33 (D43 Table Transformer trial, 2 of 34 pages adopted), PR #34 (D45: quote check in
  two readings `tools/library/quotes.py`; page pipeline `tools/pages/vision.py` + `tools/pages/prompts/`; first
  trial), PR #35 (D46 fixes + re-run). PR #36 (pre-scaling fixes, owner "yes do the fixes before scaling") merges
  on green CI. Per-cell fidelity parked on branch `fidelity-per-cell`.
- **Trial results** (`docs/vision-trial.md`): re-run 522 items / 50 pages; 84 % of quotes in both readings (strict
  whole-token matching, table rows as whole rows with their whole header); verifiers both-correct 93.9 % of 246;
  the Q3C lead-in errors are gone; coverage gaps NOT yet clean (descriptive "may" sentences, table captions, a few
  real gaps). Usage about 17 k tokens per page drafting, 3 k per item verifying (two verifiers).
- **Session 7 (session_01PybpFspEA75VUpLPy2kLTG) owns the FDA build and the work list from 31 Oct 10:00.**
- **D47 (owner, 31 Oct) sets the build: FDA first, document by document, "nothing ships unless proven"** (automatic
  route = quote confirmed + all Layer 1 checks + both verifiers correct; else the owner's review queue). Work list:
  `docs/fda-worklist.md` (the coordinator's file on main: do not regenerate; update each document's status row). **Start with 21 CFR 211**
  (XML profile: text read directly, exact-text quote check, clause number from the XML structure, no vision).
  Per group report to the coordinator: items, automatic-route pass rate, review-queue size, usage. Steps for the
  XML group: (a) XML profile in the page pipeline (units = eCFR sections/paragraphs from `tools/parse/ecfr.py`'s
  reading of the XML, not PDF pages); (b) review queue tool (one item at a time beside its source text; correct /
  fix / reject, name + time, attributable); (c) 20-unit trial of 211, tune; (d) full 211, then 210, Part 11, ...
- **211 trial DONE (`docs/fda-211-trial.md`):** XML profile `tools/fda/xmlprofile.py` + review queue
  `tools/fda/review.py` (branch `fda-build`, stacked on PR #36). 97 items from 10 sections, all quotes exact,
  automatic route 77 (79 %), review queue 20; next: the three tuning steps listed there, then the full 211 build
  (107 sections; `xmlprofile.py prepare-draft ecfr-21cfr211-2026-10-27.xml` = all sections, 22 batches of 5;
  drafting agents max 3 at a time; then prepare-verify / ingest-verify; update the 211 row of
  `docs/fda-worklist.md` on main: trial = 97 items, auto 77, review 20). Review queue UI for the owner: CLI now (`review.py next|decide|status`);
  an owner-friendly page is still to build.
- **Earlier plan, still valid where it does not conflict with D47 (one PR each, independent review, merge on green CI):**
  1. (Done in PR #36: coverage measure, continued-table headers, whole next page; coverage gaps 39 -> 13, about 9
     to look at by hand, listed in `docs/vision-trial.md`.)
  2. Layer 1 on page items (no library/clauses dependency; reuse `vision.check_item`, `quotes.findings`).
  3. 0c version currency (`tools/currency.py`, not started).
  4. 0d spot-check sheet by page (50 pages with their items, for the owner to check quotes against the PDF).
  5. A scaling plan for the owner (pages, agents, usage forecast from the trial).
  Reply to the coordinator (session_01PybpFuvG6mX9B3zK3YZjZ1, send_message) with results.
- **Run a trial:** `python3 tools/pages/vision.py prepare-draft [SRC:PAGE ...]`; agents answer `batches/` ->
  `answers/` (max 3 at a time, each sees only its batch); `ingest-draft RUN`; `prepare-verify RUN [SRC ...]`;
  verifier agents answer `verify/batches` -> `verify/answers`; `ingest-verify RUN`; `record-model RUN ROLE MODEL`.
  Page images go to `work/vision-pages/` (not in git; sha256 in the run's `pages.json`).
- Paid EU + PIC/S API build: needs direct owner confirmation before the first paid call.
- Open owner question: gold set needs a person to verify it (small 50-100 items, or skip); asked 31 Oct.

## Mutation test results (30 Oct 2026, plan 2.6 / Layer 3, pilot scale)
`tools/ai/mutate.py` planted errors in the 56 session-pilot mappings and mixed the mutants, shuffled, with the 56
untouched mappings as controls. Originals were limited to mappings that are Layer 1 clean and that both pilot
verifiers accepted (all 56). The verifiers used the pilot prompts and inputs unchanged. No batch held two variants
of one original, so no verifier saw an item next to its own mutant. The key is in `mutation-key.jsonl`.

Run folders in `library/ai-runs/`:
- `20261030T083158.816182Z-mutator/`: the text mutants; 85 of 92 requested changes were possible.
- **`20261030T084816.917722Z-mutation-verify/`: the result** (`mutation-report.json`, `agents.json`). Ten verifier
  agents, at most 3 at a time, each saw only its own batch file. One B agent left 2 of 30 items unanswered; they were
  recorded as failed calls, then answered by a fresh agent (the first pass is kept as `batch_009.first-pass-28.json`).
  A transcript scan confirmed that no verifier opened the key, the link files, the mutator run or another batch.
- `20261030T083519.725130Z-mutation-verify/`: a **superseded** first run. Its batches let an original and its mutants
  sit together (37 of 92 mutants did); the review pass found this. Its numbers were almost the same (91 of 92
  caught; mutants alone in a batch were caught 54 of 55).

| Error type | n | Layer 1 | A | B | at least one | 95 % lower bound |
|---|---|---|---|---|---|---|
| changed number | 2 | 2 | 2 | 2 | 2 (100 %) | 0.34 |
| should/shall (strength) | 15 | 15 | 15 | 15 | 15 (100 %) | 0.80 |
| wrong plant type | 15 | 15 | 15 | 15 | 15 (100 %) | 0.80 |
| wrong clause | 15 | 15 | 15 | 15 | 15 (100 %) | 0.80 |
| dropped condition | 15 | 0 | 15 | **14** | 15 (100 %) | 0.80 |
| added condition | 15 | 6 | 15 | 15 | 15 (100 %) | 0.80 |
| looser wording | 15 | 0 | 15 | 15 | 15 (100 %) | 0.80 |
| **controls: false alarms** | 56 | 0 | 0 | 0 | **0 %** | |

- **Misses: every mutant was caught by at least one check.**
  - B's one miss is *WHO TRS 986 8.9*: "Evaluate suppliers and add them to the approved supplier list or
    specifications." This drops "before approval". B read the condition back into the item ("evaluated before being
    approved and included"); A caught it.
  - In the superseded run, both verifiers missed *Schedule M 10.8.2* with "where an audit is required" dropped. Here
    both caught it.
  - So the weak spot is the same in both runs: a verifier silently restores a dropped condition from the clause.
    Which mutant trips it changes from run to run.
- **WHO 8.9 with its criteria dropped is caught** by both verifiers ("Supplier evaluation considers the supplier's
  history." without the nature of the materials). So the session pilot's 56/56 was not just leniency: the verifiers
  check whole obligations when part of one is cut.
- **Layer 1** caught every wrong clause, changed number, strength and plant-type mutant, as the plan expects. It
  also caught 6 added conditions that brought in a number ("within 30 days", "every six months"). It raised no false
  alarm.
- **Against the plan 2.6 thresholds:**
  - **Met:** Layer 1 error types detected 100 %; meaning types detected 100 % by at least one check; false alarms 0 %
    (limit 10 %).
  - **Not shown yet:** the 95 % lower bound of ≥ 90 %. With 15 mutants per type it cannot pass 0.80 even at 100 %; the
    plan's 100 per type per regulator is needed. Changed number has only 2 mutants, because only 2 pilot items carry
    a number.
- **Prompts tightened since (D31, owner):** both verifiers now judge only what the item's own words say and must
  not read the clause back into it. The numbers above were measured with the earlier prompts.
- **Re-run with the D31 prompts** (`20261030T101130.341864Z-mutation-verify/`):
  - Same set-up as before: the same key, inputs and batches (checked identical); only the prompts changed. Ten agents;
    the transcript scan was clean and no call failed.
  - Result: **both verifiers caught all 92 mutants**, and there were still **0 false alarms** on the 56 controls.
  - The only verdict that changed: B now rejects the WHO 8.9 "before approval" mutant ("The item drops the 'before
    approval' timing"). The Schedule M 10.8.2 mutant that both missed in the superseded run is caught by both.
  - Detection no longer depends on having two verifiers for these mutants, but single verdicts varied from run to
    run before, so both verifiers stay.
  - The 95 % lower bound is still capped at 0.80 by n = 15; the full-scale run is still needed. A condition that is in the clause but missing from the item is an omission, even if it
  seems implied. A trigger such as "if / where ... required / before" is part of the obligation. Both misses across
  the two runs are of this kind, and both came from a verifier reading the clause into the item.
- **Limits of this test:**
  - The mutants are single, fairly visible edits.
  - Drafting, mutating and verifying all use the same model.
  - The controls are the items the session pilot already accepted.

  Next: the full-scale Layer 3 (100 per type per regulator, subtler and combined mutants).

## Session pilot results (30 Oct 2026, D30)
Same 24 clauses, run in this session with the D30 prompts. Run folders: `library/ai-runs/20261030T081253.980447Z-session-draft/`
and `.../20261030T081601.385233Z-session-verify/` (`pilot-report.json` in the verify folder). One agent answered the draft batch.
Four verifier agents, two at a time, each answered one batch (A: 40 + 16 items, B: 40 + 16) and saw only its own batch file.

| | API pilot (D29, old prompts) | Session pilot (D30 prompts) |
|---|---|---|
| Mappings | 58 | 56 |
| Rejected quotes / failed calls | 0 / 0 | 0 / 0 |
| Both correct | 43 | **56** |
| Both incorrect | 5 | 0 |
| Disagree | 10 | 0 |
| Uncovered obligation sentences (80 % rule) | 6 | 3 |
| Cost | US$0.73 | none (Max plan) |

- **Uncovered sentences: all 3 are covered in substance.** Each is a short sentence where text outside the quote
  pushes it under 80 %: the clause number in "9.3 All self inspections should be recorded." (EU Ch 9 9.3, 0.75), the
  cross-reference "(see section 7, ...)" in WHO 8.7 (0.59), and the heading "Follow-up action-" in Schedule M 10.6
  (0.73). Possible refinement: drop a leading clause number, heading or cross-reference before measuring.
- **Examples (the clauses the API verifiers disputed):**
  1. *EU Ch 9 9.3*: the drafter now gives three items (record every self inspection; reports hold all observations and,
     where applicable, corrective proposals; record the actions taken afterwards). The API pilot gave two of these,
     and verifier A rejected both as "looser". Now both verifiers accept all three, each against its own COVERS span.
  2. *Schedule M Part I 10.4*: two items (frequency by company needs but at least once a year; frequency stated in
     the procedure). The annual minimum now stays with the frequency item, which was the API pilot's both-incorrect
     and disagreement case. Both verifiers accept both items.
  3. *WHO TRS 986 8.5 and 8.9*: the report duty and the report contents are still two items, and so are the supplier
     evaluation and its criteria (history, nature of materials). In the API pilot both verifiers rejected those
     splits. Now both accept them, because each part is a separate COVERS span.
- **Caution, for the owner: zero rejections may be too good.** The prompts say a condition or qualifier of the same
  obligation must not be split off (example 3 is arguably such a split), and still nobody objected. Possible causes:
  - the COVERS framing makes each part look whole;
  - an agent answering 40 items in one pass may be less strict than one call per item;
  - session agents are less independent than separate API calls.

  Before the full run, seed a few known-bad items (a mutation test: dropped number, dropped condition, wrong
  strength, a split obligation) into a verify batch and check that both verifiers reject them.

## Pilot results (30 Oct 2026, D29)
Run folders: `library/ai-runs/20261030T074231.724549Z-pilot-draft/` and `.../20261030T074433.157454Z-pilot-verify/`
(the report is `pilot-report.json` in the verify folder). Prompts and budget unchanged (`--budget 15`). Both batches
finished in about 4 minutes in total.
- **Cost:** US$0.73 in total (drafting US$0.14, verification US$0.59), **US$0.0125 per mapping** (drafting plus both
  verifiers). Output tokens dominate: 38,305 output tokens against 157,659 input tokens (cached and uncached).
- **Counts:** 24 clauses -> **58 mappings**; **0 rejected quotes**; **0 failed calls** (24 + 116 requests, all
  `end_turn`); 0 mappings left unverified for budget.
- **Verifiers:** both correct **43**; both incorrect **5**; disagree **10** (A incorrect / B correct 9, the reverse 1).
  The 5 both-incorrect are all items that keep one half of a clause and drop the half that the clause treats as one
  requirement (WHO 8.5 and Schedule M 10.5: report on completion vs report contents; WHO 8.9 and Schedule M 10.8.2:
  supplier evaluation without its criteria; Schedule M 10.4: annual minimum without "stated in the procedure").
- **Pattern in the disagreements:** nearly all are the same split question. When the drafter splits a clause into
  several items, verifier A judges each item against the whole clause and calls it "looser". Verifier B accepts it
  because the other parts are "separate obligations" for other items. This is a granularity rule the prompts leave
  open, not a factual error. It belongs to adjudication or a prompt decision for the owner. Examples:
  1. *EU Ch 9 9.3*, item "Keep a record of every self inspection performed." A: incorrect, it leaves out what the
     record should contain (observations, corrective proposals, follow-up), so it is looser. B: correct, it reflects
     the first sentence, and report content and follow-up are separate obligations for their own items.
  2. *Schedule M Part I 10.4*, item "The self-inspection procedure must state how often self-inspections are carried
     out." A: incorrect, it drops the at-least-once-a-year minimum, so the stated frequency could be less than annual.
     B: correct, the clause's "stated in the procedure" is captured exactly, and the annual minimum is a distinct
     obligation for another item.
  3. *WHO TRS 986 8.5* (the one reverse case), item "The self-inspection report should include the results ... and
     the recommended corrective actions." A: correct, it matches the three report contents, strength and plant types.
     B: incorrect, it presupposes a report and drops the duty to make one at the completion of each self-inspection.
     Note that verifier A treated the same split in Schedule M 10.5 as incorrect, so A is not fully consistent either.
- **For pricing the full run:** at about 2.4 mappings per clause and US$0.0125 per mapping, that is about US$0.03 per
  clause, before adjudication of disagreements (17 % here).
- **Model names in the run folders:** `requests.jsonl`, `batch.json` and `summary.json` record the model ID that was
  sent to the API. The owner confirmed that the model ID stays in audit-trail files (D30).

## Where we are
- **Latest (30 Oct 2026), read first:**
  - S1 done (PRs #11-#15). S2 part 1 merged (PR #16): library format (`tools/library/model.py`,
    `library/topics.json`), SQLite build, and the Layer 1 checker (`tools/library/layer1.py`, in CI; D28).
  - **AI checking runs in Claude Code sessions again (D30, revises D29): no API credits.** `tools/ai/sessions.py`
    turns requests into batch files of at most 40 (one system prompt per batch, so verifier A and B never mix) that
    agents answer in the session; `ingest` validates the answers against the schema and keeps the same audit trail.
    Session pilot: `pilot.py prepare-draft`, `ingest-draft <d>`, `prepare-verify <d>`, `ingest-verify <v> <d>`.
    Clauses are split into one item per obligation; the verifiers judge each item against its `COVERS:` quote, and a
    coverage check reports obligation sentences with less than 80 % of their words in a quote. The API runner
    below stays, unused; `AUDIT_ANTHROPIC_KEY` can be deleted from the environment.
  - Before D30, AI checking ran through the Claude API (D29). `tools/ai/runner.py` (Batch API, cached
    instructions, JSON-schema answers, audit trail in `library/ai-runs/`) and `tools/ai/pilot.py` (paid pilot,
    24 self-inspection clauses, hard budget US$15). The key is the environment variable `AUDIT_ANTHROPIC_KEY`, set in the
    cloud environment's settings (Claude Code strips `ANTHROPIC_API_KEY` from sessions), never in the repo or the chat. The paid pilot has run (see "Pilot results"
    below); it is kept as a reference measurement.
  - **Candidate search done (D32):** `tools/search/candidates.py query "<text>" --source <file>` shortlists the
    obligation clauses of other sources (BM25 by default). The embedding model (`python3 tools/search/embed.py
    fetch`, pinned and sha256-checked) was not measurably better than BM25 on the pilot evaluation (it helps a
    little only where the wording differs, as in ICH Q7 "internal audits"), so it is off by default.
    Re-measure it with `candidates.py evaluate` once Stage 2 has real cross-regulator pairings.
  - Mutation harness done at pilot scale (`tools/ai/mutate.py`, PRs #22, #24).
  - **Customer export done (D33):** `python3 tools/library/export.py check` (in CI) runs the option-A test on every
    compilation; `export.py build --regulators EU,PICS --plant OSD` writes one export. **S2 is complete.**
  - **Clause graph done (D34):** `python3 tools/library/graph.py report|context <file> <ref>|impact <file>`
    (needs the parsed clause store: `python3 tools/parse/run.py`, about 9 minutes, not in git). Drafter and
    verifier context is opt-in (`pilot.py prepare-draft --context`) until measured.
  - **Layer 1 condition-word check done (D35):** check 9, revised after an independent review; 0 false alarms on 114
    pilot items, 56 controls and 82 human-style paraphrases; catches the dropped conditions the verifiers missed so
    far (3 of 15 dropped-condition mutants). One-way: added conditions are left to the verifiers.
  - **No cross-regulator links (D38):** the export's similarity grouping is removed; only word-for-word twins are
    drafted once and shown once.
  - **S3 rehearsal, first pass (D36, D37):** 142 self-inspection clause units by rule (`tools/ai/topic.py`,
    `library/topics/self-inspection.json`), 116 drafted, 26 reuse identical clauses; 610 obligations.
    Consolidation into cross-regulator requirements was built, run and measured (237 requirements; both verifiers
    passed 66 %; merged relations 0-36 %), then **dropped by the owner (D37)**: the library now holds **716
    per-regulator items** (`tools/ai/items.py`), one per obligation per regulator, each with one source link.
    Layer 1: 101 findings on drafts (71 strength, mostly present-tense duties such as "ensures" or "is responsible
    for"; 23 conditions; 7 numbers); option A: 48 draft items with copied wording or a document name. All items are
    "draft"; draft findings are listed, not failed, and block verification. Usage measured: plan section 4.
  - **Next:** S3 per-item pass: repair round for the 101 Layer 1 and 48 option-A findings and the 6 rejected list
    quotes; Layer 2 on the items (`tools/ai/verify.py prepare|ingest|apply`; try one call per clause for all its
    items, the main saving); adjudication of disagreements; reverse test (numbers, conditions, frequencies + 20 %);
    mutation test on the items; then the go/no-go and forecast. The drafter now assigns each obligation's
    sub-topic (S3 took it from the dropped consolidation).
  - **START HERE (session 6): 0b is in progress.** First 0b PR (D42, PR #32) is merged to main; continue on
    branch `parser-fixes-0b-2` (from main; `parser-fixes-0b` is merged, do not reuse it). It fixed the 4
    TEXT LOST cases, WHO TRS 981 glyph text, landscape pages read upright, turned side titles, superscripts
    (10^-6), PE 009 / EMA running footers, FDA margin numbers, CDSCO header band, grade tables one row per grade.
    Fidelity: 1,210 flags, all explained; 232 "Parser defect (0b)" rows left (`grep "Parser defect"
    library/fidelity-explanations.csv`). Tests: `tests/test_parse_0b.py`.
    - **Session 6: the D41 trial is done (D43, branch `parser-fixes-0b-2`).** `tools/parse/tatr.py` (pinned
      models; `run` needs torch CPU + `tools/parse/requirements-tatr.txt`, offline, never in CI); grids in
      `library/tables-tatr/grids.json`, side by side in `trial.md`, verdicts in `verdicts.md`. Adopted on 2 of 34
      pages only (WHO 1044 A2 p19, Q3C p11; `tatr.ADOPTED`). Next: the per-cell fidelity comparison (third PR).
    - *(Was:)* **Next in 0b (second PR): the D41 trial.** Table Transformer (HF `microsoft/table-transformer-structure-
      recognition-v1.1-all`, reachable through the proxy; needs torch + transformers + timm, or an ONNX export run
      with the pinned onnxruntime) on rendered table pages (pypdfium2 is pinned); cell text from poppler words as
      now. Trial pages: grade tables (WHO 1044 A2 p17/19, EU Annex 1, PE 009 Annex 1), CDSCO checklist, ICH Q3C,
      WHO HVAC A8.1 (pages 15-17, use the upright copy), the 4 former TEXT LOST pages (now correct by rule: the
      model must not regress them). Adopt per page only where its grid beats `tables.py` under the fidelity
      check; commit the grids (JSON) with the model version and sha256, CI does not run the model. Then the
      per-cell fidelity comparison (closes the D40 table-row residual).
    - **Then the rest of the 0b list** (largest groups): CDSCO rows merged with the section-heading row below
      (18), CP 7346.832 page 53-54 row not found (pdfplumber finds the full grid with snap/join tolerance 6;
      measure corpus-wide before changing the default), FDA footnote text inside
      clauses (container closure 24, CP 7346 23), WHO 929 A4 contents as clauses (19), Q3C equations and solvent
      table (20), Drugs Rules lists/boundaries (18), OJ C 95 header (even/odd pages differ, 4-page document).
    - Then 0c (version currency, `tools/currency.py`) and 0d (50-clause spot-check sheet), one PR each.
    - Dev loop: a one-source parse is `run.parser_for(row)(path)` + `common.write_clauses` (about seconds);
      `fidelity.py run FILE...` rewrites the report with only those files, so always finish with the full run.
  - **Session 5 start note (kept): 0a (source fidelity check, D39/D40) is done** (PR from branch `fidelity-check`).
    Next: **0b parser fixes**, then 0c version currency (`tools/currency.py`, not started), then 0d a 50-clause
    human spot-check sheet; one PR each, each with an independent review pass, merged on green CI. When 0a-0d are
    done, reply to the coordinating session (session_01PybpFuvG6mX9B3zK3YZjZ1, send_message) with a short summary.
    - **Queued after 0a-0d (coordinating session, relayed owner decision "use api credits for eu and pics"):**
      the EU GMP + PIC/S build on the Claude API (Message Batches via `tools/ai/runner.py` BatchRunner, key from
      `AUDIT_ANTHROPIC_KEY`, never printed, hard budget US$150, a ~50-clause paid calibration batch first with
      the cost projection, PIC/S reuses EU items for identical clauses). Record it as the next D-number when
      started; it spends the owner's money, so confirm with the owner directly before the first paid call.
    - **0a state:** `python3 tools/parse/fidelity.py check` passes (CI step): 146 PDF sources, 20,562 clauses,
      1,374 flags, all explained in `library/fidelity-explanations.csv`, which `tools/parse/fidelity_rules.py`
      writes (mechanical verdicts, then categorised rules; ~3 min). Workflow after a parser change:
      `python3 tools/parse/run.py` (~9 min), `python3 tools/parse/fidelity.py run --jobs 3` (~15 min),
      `python3 tools/parse/fidelity_rules.py` (prints any unmatched flag: fix or add a rule), commit report + CSV.
      When 0b fixes a defect, delete its rule from `fidelity_rules.py` (rules that no longer match are harmless
      but stale; prune them).
    - **Planted-error review (D40):** 1,328 mutations over 23 sources: 69.6 % caught before the review fixes,
      91.4 % after the first round, about 94 % after the second (measured by the reviewer on its variants).
      Residual: table rows are compared as a bag, so a value dropped from or moved within a row is often missed;
      per-cell comparison belongs with the 0b table work. Harness: the reviewer's scripts were in the session
      scratchpad (gone); rebuild from D40's description if needed.
    - **0b also includes the table-transformer trial (D41, owner-approved, rendering pages is fine):** Table
      Transformer or TableFormer/Docling for table grids, text from the PDF text layer; trial on the worst tables
      first, adopt only where better, then per-cell fidelity comparison.
    - **0b work list** = every explanation starting "Parser defect (0b)" (396 rows; `grep "Parser defect" library/fidelity-explanations.csv`), plus the 10 known parser limits below. Most important first:
      1. **TEXT LOST (4):** FDA CP 7346.832 and CP 7356.002 Attachment A (first sentence stored as bogus
         "Table 3" rows, "its inspectional authority" in no clause); FDA nitrosamine guidance 2024 Appendix A
         bullet (five lines as bogus Table 1 rows, "Preliminary findings from FDA stabil-" lost); CDSCO circular
         example row 27.4 last column (page 116). Cause in common: the table extractor takes boxed or ruled text
         that is not a table as table rows and the text around it is lost.
      2. **Unreadable or misplaced values:** WHO TRS 981 QRM tables stored letter-shifted ("ufdiojrvf");
         WHO HVAC Annex 8 Table A8.1 on landscape pages stored backwards in 7.11; WHO TRS 1044 A2 / EU Annex 1 /
         PE 009 Annex 1 cleanroom grade tables stored as one merged row without grades A-D; superscripts lost
         (10^7 as "107", 10^-5 as "105"); footnote marks glued into numbers ("73.297", "1.896"); equations
         flattened (Q3C, Q2, Q3D); tables or forms stored as interleaved running text (WHO 1010 A10, 992 A4,
         1019 A2, 996 model report, 961 A2, PI 030 5).
      3. **Noise inside clauses:** PIC/S PE 009 page footers ("PE 009-18 (Part I) -1- ..."), EMA nitrosamines
         running header, FDA analytical-procedures and Part 11 margin line numbers, Schedule M signature stamp and
         HVAC figure labels, gazette page references, OJ C 95 headers, WHO 1052/1033 footers (stored backwards),
         CDSCO rotated "Quality Rating" header and merged section-heading rows, footnote text mid-sentence (FDA
         container closure).
      4. **Wrong reference / boundaries:** Drugs Rules "Part IV 99" holds Schedules I-M; CDSCO "3 #2" spans
         pages 16-143; Q3D body clauses carry an "Appendix 5" prefix; footnote or equation numbers start clauses
         (Q3A "3 #2", Q3C Appendix 1); two-column lists read across columns (Drugs Rules lists, Schedule J);
         contents entries stored as clauses (WHO TRS 929 A4).
  - **Owner priority from the coordinating session (first, after D37):** source fidelity: 0a second-engine
    re-extraction check (`tools/parse/fidelity.py`), 0b the 10 known parser limits, 0c version currency
    (`tools/currency.py`), 0d a 50-clause human spot-check sheet; one PR each. Then structured obligations and the gold set (coordinator items
    4-5), then S4 EU GMP with PIC/S reuse, OSD + INJ first.
- Brief: `docs/00-brief.md` (the owner's decisions). Small decisions: `docs/decisions.md`.
- **Deliverable (a), source inventory: done as a draft.** It is in `docs/01-source-inventory.md` and waits for
  owner review.
  - 247 English files are in `sources/official/` (about 87 MB), fingerprinted in `sources/inventory.csv`. What
    could not be fetched is in `sources/missing.tsv`.
  - Collected by three agents (FDA, EU/PIC/S, WHO/ICH/India). Their staging folders were in `work/` (not
    committed).
  - CI runs `python3 tools/inventory.py check` and the unit tests.
- **Plan (b)-(d): APPROVED** (`docs/02-plan.md`; owner decisions D13-D18). There is no API key: AI checking runs as
  Claude Code agents, with Opus for every role (D14, D15). No print or export at all (D16); the R6 compliance gap
  is recorded. NLP is used for deterministic checks and candidate search (D19).
- **S1 (parsers + clause store): in progress.** Branch work merged so far:
  - `tools/parse/numbered.py` handles EudraLex, PIC/S, WHO, ICH and Schedule M: successor-number rule, contents
    detection, section resets, English-page filter.
  - `tools/parse/ecfr.py` handles 21 CFR XML, with paragraph nesting like 211.42(c)(10)(vi).
  - `tools/parse/run.py` writes `library/clauses/*.jsonl` (not committed, D20) and `library/parse-report.md`.
  - `tests/test_parse.py` pins clauses the plan cites.
  - Current result: 120 sources, about 15,900 clauses, **94 flagged** for review. 60 FDA guidance and web files
    are pending.
  - **NLP safety net (owner request, D19), so a requirement cannot go missing even when the structure is misread:**
    - `tools/parse/obligations.py` lists every obligation sentence (shall/must/should/may, plus the numbers in
      it): about 27,400 across 120 sources.
    - `tools/parse/crosscheck.py` re-reads each PDF independently (`pdftotext -raw`) and reports obligation
      sentences missing from the parsed clauses. Today there are 211 possible misses (0.8 %). Most are tables
      (PIC/S PI 058 interpretation table, Q&A tables, aide-memoires, CDSCO checklists), where layout and raw
      extraction order the columns differently. Next step: table-aware extraction for those documents, e.g. one
      clause per table row with pdfplumber or pdftotext -bbox.
    - S2/S3 rule: every obligation sentence must end up covered by a mapping or marked not applicable. This is
      the completeness check that does not rely on the numbering.
  - One review pass is done (5 defects, all fixed with tests): contents detection, decimal rule, leading zeros,
    header/footer removal (now page edges only, with dropped text counted), and eCFR inline paragraphs plus
    roman-vs-letter (i).
- **Session 2, done: table-aware extraction (D22, D23).** `tools/parse/tables.py` (pdfplumber cell boxes + poppler
  words) gives one clause per table row (`Table <k> <label>`, kind `table_row`, `parent` = enclosing clause) for every
  non-FDA PDF; text around tables is still `pdftotext -layout`. Cross-check fallback: on table pages a sentence counts
  as found when all its words are in one row. Also fixed: WHO side header and India gazette header inside clause text;
  mixed Hindi/English gazette pages. Result: 19,465 clauses, possible misses **211 -> 19** (remaining: figure and
  flowchart text in PE 009 annexes, Q1E, Q9, WHO TRS 957/1044; Drugs Rules footnotes; one PI 030 row without a bottom
  rule; PI 041 8.8 and PI 038 3.3, to look at in the flags step). Full run takes about 9 minutes.
- **Session 2, done: FDA parsers (D24).** `tools/parse/headings.py` parses FDA guidance and compliance-program PDFs by
  section, guided by each document's own contents list ("IV.B.2", "Part III 3.A"); `tools/parse/fdahtml.py` parses
  fda.gov pages (Q&A pages -> "Q7"; other pages -> "¶12"). All 59 FDA files parse; 179 sources in the report, only
  `ema-gmp-gdp-qa.html` pending (Q&A parser).
- **Session 2, done: article, Q&A and EMA-page parsers (D25).** `articles.py` (EU Directive 2017/1572, Regulation
  1252/2014: "Recital (7)", "Article 4(2)(a)"; OJ footnotes and the annex kept out), `qa.py` ("Q7" per question),
  `emahtml.py` (EMA GMP/GDP Q&A page: "<topic> Q<n>", 129 questions). `run.text_parser` picks the numbered parser
  unless Q&A/articles fit clearly better (usable share: unique refs, clauses <= 4,000 characters); today it switches
  exactly 6 documents (EMA HBEL Q&A, EMA microbial Q&A, PIC/S PI 053, EMA nitrosamines Q&A, the two EU acts).
  No source is pending any more.
- **Session 2, done: parse-report flags (D26). S1 exit criterion met:** every flagged source has a written explanation
  in `library/parse-explanations.csv` (`run.py --report` re-renders the report without parsing). 180 sources, 22,831
  clauses, 59 flagged, 0 unexplained, 20 possible misses (figure text). Fixed in general: unique references
  (`common.resolve_duplicates`: contents copies -> toc, real restarts "#2" + note), contents lines no longer open
  appendix sections, stray numbers (footnotes, list items, running headers, wrapped lines) are taken back when the old
  numbering resumes, title-case chapters after subsections, glossaries and annex/appendix intro text are citable
  sections, cover dates, eCFR deep levels and italic definitions, FDA appendices/attachments.
- **Session 2, done: S1 tail (D27).** Known parser limitations 22 -> 10: chapters without sub-numbers (WHO HVAC,
  QRM, EU MAH paper, EU Annex 11), unnumbered trailing annexes and back matter, prefixed numbering ("B 1.1", "I.1",
  "A.1"), margin line numbers (EU Annex 17), wrapped lower-case lines, a heading that replaces a list item with its
  number (Q1B), table rows sharing one ruled cell (PI 038), an FDA level below the contents list (III.B.1) and appendix
  sections. 180 sources, 22,783 clauses (reference-list entries are no longer clauses), 51 flagged (all explained).
- **Remaining limitations (10, text kept, reference coarse):** WFI Q&A Part II list, PI 011 sections 27-29, PI 041
  numbered table rows, PI 030 open table row, PE 009 Annex 2A B 3.3 tail and Annex 3 typo "14..", Drugs Rules form
  items, WHO AMR quoted clauses, CP 7356.002a Attachment A in the page header, WHO TTSP bibliography. They can be
  fixed alongside S2 if mapping needs them.
- **Then S2:** library schema, Layer 1 checker with the NLP pieces (D19), BM25 plus a pinned embedding model for
  candidate search (D21), mutation harness, customer export and the option-A test.

## Open with the owner
1. Anvisa RDC 654/2022 (APIs) and the English IN annexes are still wanted (phase 2; captcha, so the owner
   downloads them). The owner uploads files on a branch; we catalogue them and delete the upload branch (D11).

## Facts a new session needs
- Repo: `maglesT/audit-insp-syste` (private). Owner decision D7: regulator-published English translations are allowed.
- The owner's email is triplerascals03@gmail.com. Updates go in Gmail thread id 1a1888c48a563240 (reply with replyThreadId), whose subject starts with
  "Audit:".
- eBMR repo (read-only context): `maglesT/ebmr`. It is not this product. Do not copy its controls blindly.
- Downloads: EC, FDA, eCFR (send `Accept-Encoding`, i.e. `curl --compressed`), ICH, PIC/S (`/docview/<id>`) and
  the WHO CDN all work through the proxy. Three EC files return a bot check; leave those to the owner.
- Commands: `python3 tools/inventory.py write|check`, `python3 -m unittest discover -s tests`.
- Commit trailer: `Co-Authored-By: Claude <noreply@anthropic.com>` plus the session's Claude-Session line. No
  model names.
