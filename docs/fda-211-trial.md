# 21 CFR 211 trial, XML profile (D47), 31 October 2026

Run folder: `library/ai-runs/20261031T095248.400139Z-xml-draft/` (`items.jsonl`, `report.json`, `verify-report.json`,
`route.json`, `agents.json`). Tool: `tools/fda/xmlprofile.py`, prompts `tools/fda/prompts/`. Sections: 211.22, 211.25,
211.42, 211.67, 211.84, 211.100, 211.113, 211.166, 211.180, 211.192 (the trial unit is a section; about 20 pages of
printed text).

| Measure | Result |
|---|---|
| Items | 97 from 10 sections; 17 not-applicable sentences with reasons |
| Quote confirmed (exact XML text, cited paragraph) | **97 / 97** |
| Deterministic findings | 6 condition-wording findings |
| Coverage gaps | 2: 211.42(c) lead-in sentence; 211.166(a) "The written program shall be followed and shall include:" (the "shall be followed" duty has no item) |
| Verifiers | both correct 81, both incorrect 0, disagree 16 |
| **Automatic route (D47)** | **77 of 97 (79 %)**; review queue 20 |
| Usage | drafting about 120 k tokens (1.2 k per item); two verifiers about 265 k (2.7 k per item) |

**What the disagreements are:** 15 of 16 are the 211.42(c)(1)-(10) items: the lead-in "separate or defined areas
or such other control systems ... as are necessary to prevent contamination or mixups" was written into each item's
condition field but not its statement; verifier B rejects that, verifier A accepted it as part of the item. The
16th is 211.113(a) (scope "drug products" vs the listed plant types).

**Tuning before the full 211 build (profile only, F2):** (1) the prompt says the statement itself carries a parent
lead-in's qualifier (the condition field only repeats it), and both verifier prompts say the condition field is not
part of the statement; (2) the lead-in check also covers qualifiers such as "as are necessary to ..." in an XML
parent paragraph ending ":" (today only if / where / when / unless / only); (3) the two coverage gaps get items
(211.166(a) "shall be followed"). Then the full 211 build, section by section, and the review queue for what is not
proven.

## Tuning done (31 October 2026, session 7)

Code: `xmlprofile.qualifier_missing` (lead-in qualifiers "as are necessary to ...", "as appropriate"),
`lead_in_text` (all lead-in ancestors ending ":", so 211.42(c)(10)(i) carries both (c)(10) and (c)),
`plants_finding` (a text limited to products not required to be sterile excludes INJ; one limited to sterile
products lists only INJ/API), `lead_in_covered` (a lead-in sentence with one obligation word is covered by its
sub-paragraphs' items when each has one and all carry the lead-in; a lead-in with its own duty needs its own item).
Prompts: the statement carries every lead-in qualifier (the condition field only repeats it; verifiers treat it
as a label); INJ = sterile injectables; no paragraph references in statements (customer-facing, option A).

- On the trial's own drafts the new checks flag exactly the 16 verifier disagreements (15 lead-in, 1 plants) and
  nothing else.
- Redraft of 211.42, 211.113, 211.166 (`20261031T100331.802997Z-xml-draft`): 37 items, 37 quotes exact, **0
  coverage gaps**, 211.113(a) now OSD/LIQ/SEMI; both verifiers 37/37 correct; **automatic route 36 of 37**. The one
  in review cited "211.166(a)(1)-(5)" in its statement (numbers check), which the prompt now forbids.
- Part 211 has **60 sections** in the eCFR XML (324 paragraphs), not 107: the full build is 12 batches of 5.

## Full 21 CFR 211 build (31 October 2026, session 7)

Run `library/ai-runs/20261031T100541.543518Z-xml-draft` (60 sections, 12 drafting agents, 24 verifier agents, at
most 3 at a time, each saw only its batch); 211.1 redrafted in `20261031T101348.722968Z-xml-draft` (0 items, 6
not-applicable sentences, 0 gaps).

| Measure | Result |
|---|---|
| Items | **399** from 60 sections; 67 + 6 not-applicable sentences with reasons |
| Quote confirmed (exact XML text, starting in the cited paragraph) | **399 / 399** |
| Coverage gaps | 0 (after the 211.1 redraft) |
| Items with deterministic findings | 30: conditions 19, lead-in 9, numbers 4, strength 2 (an item can have several) |
| Verifiers | both correct 385, both incorrect 7, disagree 7 |
| **Automatic route** | **365 of 399 (91.5 %)** after `recheck` with the corrected lead-in check (first routing: 359, 90.0 %); **review queue 34** |
| Usage (session agents, Max plan) | drafting about 700 k tokens (1.8 k per item), verifying about 1,520 k (3.8 k per item, both verifiers), 211.1 redraft 50 k |

What the verifiers rejected (examples): 211.50 refuse "in and from" the building narrowed to "from"; 211.52
"washing facilities" narrowed to hand-washing; 211.68(c) closed list of sections made open ("such as"); 211.105(b)
exception (name when only one of a type) dropped; 211.125(c) "in accordance with 211.122(g)(2)" dropped; 211.132
statement adds "and confirm it does"; 211.142/211.150/211.166(a) summary items over lead-ins that lose the
sub-paragraphs' qualifiers. All 40 wait in the owner's review queue (`python3 tools/fda/review.py next
library/ai-runs/20261031T100541.543518Z-xml-draft`); nothing of them ships until decided.

Prompt lessons for the next XML documents (210, Part 11, 314.81): a summary item over a lead-in ("shall include:")
loses the sub-paragraph qualifiers, so the lead-in's own duty is quoted alone ("shall be established and
followed") and the contents stay with the sub-paragraph items; closed lists of cross-referenced sections stay
closed without naming the references.
