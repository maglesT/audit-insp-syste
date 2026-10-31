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
