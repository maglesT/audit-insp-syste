# Product brief (owner decisions of 29 October 2026)

This is a condensed copy of the brief the owner agreed with the lead session. It is the source of truth for scope;
change it only on an owner decision.

## Idea
Sites fail international inspections because their self-inspection checklists miss what inspectors look for.
Product: a GMP audit checklist library, as strict as possible, compiled from the official GMP texts of many
regulators, for five plant types: OSD, oral liquids, gels/semisolids, sterile injectables, and APIs. The user picks
any combination of regulators plus a plant type and gets one checklist. Where texts overlap, the strictest
requirement wins. Users can build their own checklists from the library, add their own items, and run internal
audits with them.

## Two separate systems
1. **Internal library** (the owner's asset; never deployed to customers): every requirement with its clause
   references, exact quotes, cross-regulator links and verification evidence.
2. **Customer app**: only the compiled items in plain words, tagged with regulators and plant types. Option A:
   no clause numbers, quotes or source mapping in the app's database or API. A regulator-name-only or per-finding
   citation may be added later without changing the library.
   - Protection: the server sends only the items on screen; rate limits against bulk scraping; no print, export
     or copy; a watermark with the viewer's name and the time on every screen. Optional canary items or
     per-customer wording to trace leaks.
   - Because printing is off, auditors run the audit in the app (tablet/browser) and record findings per item.
   - Findings are GMP records (self-inspection), so the app applies MINIMUM compliance only: unique accounts and
     roles, an audit trail, no deletion (corrections carry a reason), and e-signature only where a clause
     requires one. Each rule is mapped to its binding clause and must pass the test "which clause breaks if we
     drop it?".

## Regulators (official texts in English only)
- **Pilot:** US FDA (21 CFR 210/211 plus relevant guidance), EU GMP (EudraLex Vol 4) + PIC/S PE 009, WHO GMP (TRS
  annexes: main, sterile, APIs), India Revised Schedule M, and ICH (Q7, Q9, Q10).
- **Phase 2:** UK MHRA, EDQM, Health Canada (GUI-0001), TGA (PIC/S plus TGA specifics), SAHPRA (formerly MCC).
- **Phase 3, on demand:** Saudi SFDA/GCC, Kenya PPB, Nigeria NAFDAC, Singapore HSA, Malaysia NPRA.
- **Dropped** (their official texts are not in English): Anvisa, Invima, Russia/EAEU, Japan PMDA/MHLW, Turkey,
  COFEPRIS, Ukraine, Vietnam, Indonesia. Never label a checklist "Anvisa" or "PMDA" unless their own texts are
  mapped.
- **Library structure:** three deep cores (EU GMP/PIC/S, US FDA, WHO GMP). Each topic has ONE requirement, mapped
  to every regulator's clause, with a flag wherever a regulator adds or tightens something. Every further
  regulator is a mapping onto a core plus its own additions.

## Verification (no human experts; software and AI only)
- **Layer 1, deterministic (no AI):**
  - each quote exists word for word at the cited clause;
  - each clause number exists in the parsed structure (`pdftotext -layout`);
  - every number in an item appears in its quote;
  - requirement strength (shall/must vs should/may) comes from the quote's words;
  - completeness: every clause is mapped to an item, or marked not applicable with a reason;
  - every source file is fingerprinted by sha256.
- **Layer 2, AI review of meaning:**
  - two blind verifiers (different prompts, ideally different models) see only the item and its clause and answer
    fixed structured questions;
  - they must agree unanimously; otherwise a third adjudicates; otherwise the item is NOT shipped (marked
    unverified);
  - reverse test: an agent reads only the plain item, writes the requirement it implies, and that is compared
    with the source;
  - cross-regulator consistency: texts shared by EU, PIC/S, TGA and MHRA must get mappings that agree.
- **Layer 3, measure the checking:** seed known errors (wrong clause, changed number, should→shall, wrong scope)
  and measure the detection rate per regulator. A regulator goes live only above set thresholds. Affected items
  are re-verified when a source changes.
- **Honesty:** this gives high accuracy, not a guarantee; the weakest spot is subtle meaning and scope. Product
  wording: "compiled from official texts with automated multi-step verification", never "expert-verified", with a
  disclaimer that the checklist supports internal audits and does not replace the site's judgement. A paid
  spot-check of about 100 items by a freelance consultant can be suggested later.

## Style
- Functionality first, user-friendly, NOT over-engineered: one app with a simple data model. The hard work is the
  library pipeline.
- Plan first and get the owner's approval:
  - (a) source inventory;
  - (b) library data model and verification pipeline with release thresholds;
  - (c) app scope and its minimum compliance rules;
  - (d) slices.
- Pilot: FDA + EU/PIC/S + WHO + Schedule M + ICH for OSD and injectables. Report the measured accuracy, then
  expand.
- Small decisions go in `docs/decisions.md`; ask the owner only for genuinely owner-level ones.
- Way of working:
  - branches, tests with every feature, CI on GitHub Actions, merge when green, one review pass per feature;
  - commit trailers carry no model name;
  - email the owner in the "Audit:" Gmail thread after each merge and whenever a decision is needed.
- Token economy:
  - at most 2–3 agents at a time, with short briefs;
  - verifiers return structured results;
  - a fresh session after each big milestone, with a handover note in the repo;
  - estimate the token and time cost per regulator.
