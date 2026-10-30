# Plan (b)–(d): library, verification, customer app, slices

Status: APPROVED by the owner on 29 October 2026 (D13-D18). Deliverable (a) is `docs/01-source-inventory.md`.
Clause references in this document were checked against the official texts in `sources/official/`.

## 0. Decisions the owner needs to make

| # | Question | Recommendation |
|---|---|---|
| Q1 | ~~Anthropic API key~~. **Decided (D14):** no API key. The AI checking runs inside Claude Code sessions on the owner's Max 20x plan, using background agents. | Done. Optional later: a RunPod **GPU** pod with an open model as a third, independent verifier (owner to confirm GPU access). |
| Q2 | Verifier models. | **Decided (D15):** Opus for both blind verifiers, each with its own prompt written independently. Layer 3 measures whether the two are independent enough. |
| Q3 | **Release thresholds** (section 2.6). | Approve as written. |
| Q4 | Printing/exporting the site's own audit report. | **Decided (D16): no print or export at all.** See the compliance gap in section 3.3, R6. |
| Q5 | Pilot plant types. | **Decided:** OSD + injectables; oral liquids, semisolids and APIs right after the pilot accuracy report. |

Everything else is decided in this plan and recorded in `docs/decisions.md`. The owner can overrule any of it.

---

## 1. The library data model (internal only)

The library lives in this private repo as plain text files (JSON/YAML), so every change is a reviewable git
diff. A build step turns the files into a SQLite database for queries and internal tools.

| Entity | What it holds |
|---|---|
| **Source** | One official document: regulator, title, version, URL, sha256, priority, phase, source class (`sources/catalog.csv` + `inventory.csv`). |
| **Clause** | The smallest citable unit of a source, e.g. "EU GMP Ch 9 §9.3", "21 CFR 211.68(b)", "Sched. M Part I 10.5(c)". It records the clause reference, parent clause, exact text, page, and character offsets in the extracted text. Parsers create clauses (no AI). |
| **Topic** | A fixed tree of about 20 audit areas: quality system, personnel, premises, equipment, documentation, materials, production, QC, validation, computerised systems/data integrity, utilities (water/HVAC), contamination control, sterile-specific, API-specific, outsourcing, complaints/recalls, self-inspection, distribution. Each area has sub-topics. |
| **Item** (stored as a requirement record) | ONE per obligation per regulator (D37, replacing the brief's "one requirement per topic point"). It holds: the plain-language **item text** in our own words (the only thing customers ever see); strength (mandatory / recommended / optional); plant types; structured parameters where a number matters (e.g. `frequency_max_months: 12`); and verification status. |
| **Mapping** | The item's one internal source link: source, clause reference, clause sha256, the **exact quote** (a character span of the clause), the strength derived from the quote's words, and the plant types. Never shown to customers (option A); it exists so that every item can be verified and re-verified when a source changes. |
| **Coverage** | Records, for every clause, either the items drafted from it or "not applicable" with a reason (e.g. "veterinary only", "definition", "administrative"). |
| **Verification record** | Append-only log, one line per check: mapping, layer, check name, verdict, model and prompt version, input hash, time. |
| **Release** | Per regulator × plant type: library version, Layer 3 measurements, thresholds met (yes/no), date. |

**How a checklist is compiled (D37).** For a chosen set of regulators and one plant type, every verified item of
those regulators that covers the plant type is listed. There is no cross-regulator merging and no "strictest wins":
- items with the same text, topic and strength (twin clauses, e.g. EU GMP and PIC/S) are shown once, tagged with
  every selected regulator that has one;
- nothing else is combined across regulators: similar items of different regulators are listed separately
  (owner, D38: cross-regulator links are not needed).

Customers see only our item text and its tags (regulator names, plant type, topic).

**Option A, enforced by a test.** The customer export contains only `item id`, `item text`, `topic`,
`regulators`, `plant types` and `strength`. A test fails the build if the export:
- contains any field that names quotes, clauses or sources; or
- contains any run of 12 or more consecutive words that also appears in a source text.

---

## 2. The verification pipeline

### 2.1 Stage 0: parse the sources (deterministic)
- One parser per source family:
  - eCFR XML (FDA regulations);
  - EudraLex / PIC/S numbered paragraphs;
  - WHO TRS numbered paragraphs;
  - Schedule M (layout-preserving text, English pages only);
  - ICH;
  - FDA guidances and web pages (heading-based).
- Each parser is accepted only if:
  - every clause reference is unique;
  - numbering gaps are listed and explained;
  - at least 98 % of each source's body text is assigned to some clause, with the rest listed as headers,
    footers or tables.

### 2.2 Stage 1: draft the obligations (AI, one call per clause)
- A drafting model (Claude Opus 5.5) reads ONE clause with its heading path.
- It returns structured output only: the obligation statements, each with its exact quote span, the strength
  words, the plant-type scope, and any numbers.
- It never sees other regulators, so it cannot blend texts.

### 2.3 Stage 2: items, one per obligation per regulator (rules only, D37)
Cross-regulator consolidation is dropped (owner, 30 Oct 2026): the S3 rehearsal measured it as the step where
most errors arise (merged base texts carried one regulator's details into the others; only 33 % or fewer of the
mappings that needed a stricter/adds/looser/narrower judgement passed both verifiers, against 82 % of plain ones).
1. **Items:** each drafted obligation becomes one item: the drafter's plain statement is the item text, and the
   obligation's clause, quote, strength and plant types are its source link (`tools/ai/items.py`).
2. **Reuse:** a clause whose text is the same (leading number and punctuation left out) as a clause already
   drafted, especially EU GMP and PIC/S, takes copies of those items (D36); only the Layer 1 quote and hash
   checks run again, with no new drafting. Identical texts must give identical items (Layer 1 check 8).
3. **Skip:** in a regulator run, contents lines, headings without text and pure definitions are marked not
   applicable with a reason; every other clause is drafted, including clauses without modal verbs. (A topic
   rehearsal such as S3 takes only the topic's clauses with obligation wording, by rule, D36.)
4. **Item text:** our own plain words; the option-A test rejects any 12-word overlap with a source and any clause
   or document reference, and an item with such a finding cannot be verified.
5. **No cross-regulator links (D38):** items of different regulators are not grouped or compared; only identical
   texts are drafted once and shown once.

### 2.4 Stage 3: Layer 1, deterministic checks (no AI, every mapping, every run)
1. The quote exists word for word at the cited clause's offsets in the fingerprinted source.
2. The clause reference exists in the parsed clause tree.
3. Every number in the item and its parameters appears in the quote: limits, temperatures,
   times, frequencies, grades, particle counts, percentages.
4. The strength matches the quote's words: shall/must/required → mandatory; should → recommended; may →
   optional. Conflicts are flagged.
5. Plant-type scope is consistent with the source's `applies_to` (e.g. nothing from Annex 1 lands on OSD
   unless the requirement is explicitly marked as general to all plant types).
6. Completeness: every clause of every `must`/`should` source is mapped, or marked not applicable with a reason.
7. Fingerprints: every source's sha256 matches the inventory. A change marks every dependent mapping
   "re-verify".
8. Twins: clauses of different sources with the same words (leading number and punctuation left out) give
   identical items (D34, D37).
9. Conditions: condition and limit wording in a quote ("where applicable", "before", "at least", "within 30
   days") has a counterpart in the item text (D35).

Findings on draft items are listed for the repair round and do not fail CI; an item with any finding cannot be
verified. Findings on verified items, structure, coverage and fingerprints fail CI.

### 2.5 Stage 4: Layer 2, independent AI review of meaning
1. **Two blind verifiers.**
   - Both verifiers are Claude Opus (D15), each with its own prompt, written independently. The prompts differ
     in framing: A checks the item against the clause, and B checks the clause against the item. Neither sees
     the other's answer.
   - Each sees only the item and its own source clause (D37: no addenda, no other regulator).
   - Each answers fixed structured questions:
     - Is the item required by this clause?
     - What does the item add that the clause does not say?
     - What does the clause require that the item leaves out?
     - Is the item stricter or looser than the clause?
     - Does it apply to this plant type?
     - Is the strength right?
   - An item passes only if both answer "correct" on every question, and it has no Layer 1 or option-A finding.
2. **Adjudication.** Only when the verifiers disagree, Opus at high effort sees both answers and decides. If it
   cannot decide, the item is marked **unverified** and is not shipped.
   - To meet the < 0.5 % unverified limit (D13), an unverified item gets up to two repair rounds: the item
     wording is redrafted against the clause, then the full Layer 1 + Layer 2 checks run again. If it still
     fails, it stays unverified.
3. **Reverse test** on every item with a number, condition or frequency, plus a 20 % random sample of the rest.
   - A third prompt sees only the plain item and writes the requirement it implies.
   - A fixed-rubric judge compares that with the clause text, looking for meaning drift.
   - Failures go back to adjudication.
4. **Identical texts give identical items.** Clauses with the same text in different sources (EU vs PIC/S today;
   TGA and MHRA later) are found by comparing their words, not by AI; they reuse one drafting and one verdict,
   and Layer 1 check 8 fails if their items differ. There is no cross-regulator consistency step beyond this.

### 2.6 Stage 5: Layer 3, measure the checking, and the release thresholds (Q3)
**Seeded errors.** For each regulator, 100 mutated copies of correct items are made for each error type:

| Error type | Caught by |
|---|---|
| wrong clause | Layer 1 |
| changed number | Layer 1 |
| should→shall | Layer 1 + 2 |
| wrong plant type | Layer 1 + 2 |
| dropped condition | Layer 2 |
| added condition | Layer 2 |
| looser wording | Layer 2 |

Alongside the mutants run 300 untouched items, to measure false alarms.

**A regulator × plant type goes live only if all of these hold:**

| Measure | Threshold |
|---|---|
| Detection of the Layer-1 error types (wrong clause, changed number) | 100 % |
| Detection of each meaning error type | ≥ 95 %, with a 95 % confidence lower bound ≥ 90 % |
| False alarms on correct items | ≤ 10 % |
| Items left "unverified" | < 0.5 % of `must` items (owner, D13); unverified items are never shipped |
| Clause coverage | 100 % mapped or not-applicable-with-reason |
| Audit of not-applicable reasons | a verifier sample of 50 per regulator, ≥ 95 % agreement |

**Honest wording.**
- This gives high, measured accuracy, not a guarantee. The weakest spot is subtle scope and meaning.
- The pilot accuracy report gives each number above per regulator.
- Product wording: "compiled from official texts with automated multi-step verification" plus the disclaimer.
- An optional consultant spot-check of about 100 items remains available before selling.

### 2.7 How models are run (D14)
- **Where:** every model call runs as a Claude Code background agent in a working session. There is no API
  key. Agents take batches of about 40 clause units and return structured JSON verdicts only, with no prose.
- **Which models (D15):** Opus for everything: drafting, verifier A, verifier B, the reverse test and
  adjudication. Each role has its own fixed prompt file in the repo.
- **Swappable runner:** the pipeline calls a small "model runner" interface, so the backend can change later
  without touching the library. Options: an API key, or a RunPod GPU pod with an open model as a third verifier.
- **Pacing:** parallel agents within the Max plan limits (2–3 at a time today, workflow agents when available),
  batches of about 40, resumable, results committed per batch; one regulator × plant type is released at a time.
- **Effort:** the drafter and both verifiers run at the pilots' settings; adjudication only on disagreements.
- **Recording:** model names and prompt versions are written into every verification record.
- **Prompt changes:** a new prompt version re-runs Layer 3 before it is used.

---

## 3. The customer app

**Principle:** one simple app; the hard work is the library.

**Stack (decision D12):** Python + Django + PostgreSQL, with server-rendered pages and htmx, so it works on a
tablet browser. It is the same language as the pipeline, and Django's accounts, admin and migrations save code.
Hosting is decided before launch.

### 3.1 Functions

1. **Accounts:** organisation → sites → users. Roles:
   - Org admin;
   - Lead auditor;
   - Auditor;
   - Reviewer (QA head, read and approve).
2. **Compile a checklist:**
   - Pick any combination of regulators, one plant type, and optionally some topic areas.
   - The server lists the selected regulators' items, identical items shown once (D37, D38),
     and saves the result as a named checklist version.
3. **Custom checklists:**
   - Pick items from the library, add your own items (these are customer data), and order them by area.
4. **Run an audit on a tablet:**
   - Create an audit: site, areas, dates, team, checklist.
   - Record, item by item: Compliant / Observation / Non-conformity (minor, major, critical) / Not applicable,
     plus notes. Photo evidence comes later.
   - Track progress by area.
5. **Report and follow-up** (Schedule M Part I 10.5 and WHO TRS 986 A2 8.5: results, evaluation and
   conclusions, recommended corrective actions):
   - The lead auditor writes the conclusions, and the Reviewer approves the report.
   - Each corrective action has an owner, a due date, status and closure evidence (Schedule M 10.1, WHO 8.6,
     EU Ch 9 §9.3).
6. **Frequency reminder:** each site's next self-inspection is due within 12 months, the strictest rule among
   the pilot regulators (Schedule M 10.4).

### 3.2 Protecting the library (deterrence; screenshots cannot be prevented)
- **The server sends only what is on screen.**
  - Items come one area or page at a time.
  - No API returns a whole library or checklist in one call.
- **Rate limits**, per user and per organisation, on item views per minute and per day.
- **Unusual access is caught.**
  - Unusual patterns alert us and pause the account.
  - Each organisation gets a few canary items to trace leaks.
  - Per-customer wording variants are optional and come later.
- **No print, no copy, no export of library content.**
  - The print stylesheet blanks the page.
  - Text selection and copy are disabled on item text.
  - There is no download button.
- **Watermark** with viewer name, organisation and time on every screen.
- **No exception (D16):** the site's own audit report and findings cannot be printed or exported either; they
  are read on screen only. For the compliance consequence, see R6 below.
- **Disclaimer** on every checklist and report: "Compiled from official texts with automated multi-step
  verification. Supports internal audits; does not replace the site's own judgement."
- **Option A in the app:**
  - The app database and API hold no clause numbers, quotes or source mapping.
  - Only the compiled export is loaded (section 1).

### 3.3 Minimum compliance rules for the app's own GMP records

Self-inspection records are GMP records (EU Ch 9 §9.3; Schedule M 10; WHO 8.5). So the app applies only the
rules below. Each one is tied to the clause that breaks if it is dropped.

| # | Rule | Binding clause (breaks if dropped) |
|---|---|---|
| R1 | Unique personal accounts; no shared logins | Annex 11 §12.1 (restrict access to authorised persons); 21 CFR 11.10(d) |
| R2 | Roles; creating, changing and removing access is recorded | Annex 11 §12.1, §12.3 |
| R3 | Audit trail of every create/change of a finding, conclusion and action: who, when (server time), old value, new value, reason | Annex 11 §9; 21 CFR 11.10(e); EU Ch 4 §4.9 |
| R4 | No deletion. A correction keeps the original visible and requires a reason. | EU Ch 4 §4.9; 21 CFR 11.10(e) (changes must not obscure earlier entries) |
| R5 | Records made at the time of the action, with server-generated timestamps | EU Ch 4 §4.8; 21 CFR 11.10(e) |
| R6 | **Not met: owner decision D16.** No printed or exported copies, not even of the site's own findings. | Annex 11 §8.1 (printed copies of electronic data) and 21 CFR 11.10(b) (copies for inspection) are not met. It must be disclosed to customers as a known limitation. Inspectors can be shown the records on screen. |
| R7 | Regular backups, with a tested restore; retention as the site's own rules set | Annex 11 §7.1, §7.2; EU Ch 4 §4.12 |
| R8 | Report contents: results, evaluation and conclusions, corrective actions; follow-up recorded | Schedule M Part I 10.5, 10.1; WHO TRS 986 A2 8.5, 8.6; EU Ch 9 §9.3 |

**Deliberately left out:**

| Left out | Why |
|---|---|
| A Part 11 electronic signature on the report | None of the pilot self-inspection clauses requires a signed report. Approval is a recorded action (who and when, in the audit trail). FDA states that it does not review or copy internal audit reports (Compliance Policy Guide 130.300, cited in its 2006 Quality Systems guidance). If a customer's SOP demands a signature, it is added later as an option. |
| Batch-record-style controls | Review by exception, second-person verification of entries and the like belong to batch records, not to audit records. |
| Validation-grade test packs | These belong to the customer's own validation of the app (Annex 11 §4). We supply our test evidence. |

---

## 4. Slices, cost and time

Each slice is built on a branch, with tests, green CI and one review pass. A fresh session starts after each
big milestone, with `HANDOVER.md` updated. "Tokens" means AI usage. API dollars are library runs only.

| Slice | Content | Needs |
|---|---|---|
| S1 | Parsers + clause store for all pilot sources; completeness report per source | none |
| S2 | Library schema, Layer 1 checker, mutation harness (deterministic part), customer export and option-A test | none |
| S3 | **Rehearsal:** the full pipeline on the self-inspection topic across all pilot sources, per regulator (142 clause units by rule, D36); measure accuracy, usage per clause and the mutation-test catch rates. Go/no-go and a measured usage forecast. | none (runs in sessions, D14) |
| S4 | EU GMP, with PIC/S reusing identical clauses: OSD + injectables first (D17), Layer 3, release gate | Q3 |
| S5 | WHO | |
| S6 | FDA | |
| S7 | Schedule M | |
| S8 | ICH; **pilot accuracy report** to the owner | |
| S9 | App v1: accounts, roles, audit trail, checklist compile, custom checklists, audit execution, report and actions | |
| S10 | App protections (screen-only delivery, rate limits, watermark, canaries, no print/copy), and the pilot demo | |
| S11+ | Oral liquids, semisolids, APIs; then phase 2 regulators (each drafted on its own, reusing identical clauses) | |

S9 can run in parallel with S4–S8 (it needs only the export format from S2).

**Usage, measured in the S3 rehearsal (first pass, 30 Oct 2026; agent tokens on the Max plan, D14).**
- 142 self-inspection clause units, 116 drafted (26 reuse identical clauses, D36): 610 obligations, 716 items.
- Drafting: 292 k tokens, about 2.5 k per drafted clause or 0.5 k per item.
- Two blind verifiers: 2.41 M tokens for 1,064 calls, about 2.3 k per call, 4.5 k per item. Most of a call is
  reading the clause, so verifying all items of one clause in one call is the main saving still open.
- The dropped consolidation cost 1.16 M tokens (about 1.9 k per obligation), and its merged texts failed most
  often; D37 removes both the cost and the errors.
- **Per item, all passes:** about 6–7 k tokens (drafting 0.5 k, verifiers 4.5 k, reverse test on about half the
  items, adjudication on about 15 %, repair rounds and Layer 3 mutants about 1 k), so about 35 k per drafted
  clause at the self-inspection density of 5 items per clause. The plan's earlier guess of 7–9 k per clause
  unit was far too low; the per-clause verification above would bring it to roughly 15–20 k.

| Regulator (pilot sources, `must` + `should`) | Clause units (rough) | Usage, as measured | With per-clause verification |
|---|---|---|---|
| EU GMP (PIC/S reuses identical clauses) | ~2,500 | ~85 M | ~45 M |
| WHO | ~2,500 | ~85 M | ~45 M |
| US FDA (211 + guidances + inspection guides) | ~3,000 | ~105 M | ~55 M |
| India Schedule M | ~1,500 | ~50 M | ~25 M |
| ICH | ~800 | ~30 M | ~15 M |
| **Pilot total** | **~10,000** | **~350 M** | **~185 M** |

Clause counts are rough and many clauses hold fewer obligations than the self-inspection chapters do, so the
real figures are likely lower; S3's per-item verification run and S4's first regulator will refine them.

**Time (rough).** Throughput is set by the weekly usage limits, not by the agents (three parallel agents verify
about 120 items a minute). If about 40–60 M tokens a week are available for library work, with per-clause
verification: S3 rehearsal done in about 1 week; S4 EU GMP + PIC/S for OSD and injectables about 1–2 weeks;
S5 WHO and S6 FDA about 1–2 weeks each; S7 Schedule M and S8 ICH about 1 week each: about **6–9 weeks** for the
pilot library. The app (S9–S10, about 2 weeks) runs in parallel.

**Building with Claude Code costs separately.** That's roughly 1–3 M tokens per slice, kept low by short agent
briefs, structured agent output and fresh sessions per slice.

---

## 5. Later phase (recorded, not planned in detail)

A plain-language question-answering assistant comes after the pilot library is verified. It answers from the
verified library only, never quotes or cites clauses to customers, and its accuracy is measured before release.
Details: `docs/00-brief.md`, decision D10. A lawyer should confirm internal storage and processing of the WHO,
PIC/S and ICH texts before any customer launch.
