You read sections of a US regulation (21 CFR, from the official eCFR XML) and list the obligations they state. Each
section is given as its paragraphs, each with its reference from the XML structure ("211.84(c)(1)") and its exact
text. Your output is checked by software against that exact text and by independent reviewers, so precision
matters more than wording.

List each separate obligation as its own item, so that together your items cover every obligation in the section.
One obligation is one thing a manufacturer must, should or may do, with all its conditions, numbers and
qualifiers; do not split one obligation across items. For each item:
- statement: the obligation in your own plain English words, as one checklist item a site could be audited
  against. Do not copy more than a few words in a row. Keep every condition ("where", "if", "unless", "when",
  "except") and every number. Do not add anything the text does not say.
- quote: the exact span of ONE paragraph's text that states the whole obligation, copied character for character
  (matched against the XML text by software; do not fix typos or change punctuation). Leave out the paragraph's
  designation ("(c)"). A quote may continue into that paragraph's sub-paragraphs, in order.
- clause_number: the reference of the paragraph the quote comes from, exactly as given ("211.84(c)(1)").
- strength: "mandatory" for shall / must / is required / may not; "recommended" for should; "optional" for may.
  A sub-paragraph without such a word takes its parent's lead-in ("(c) Samples shall be collected in accordance
  with the following procedures:" makes (c)(1)-(c)(6) mandatory).
- plant_types: from OSD, LIQ, SEMI, INJ, API; the plant scope given unless the text narrows it.
- numbers: every number, limit, frequency or period in the quote, as written.
- condition: the condition or trigger in a few words, "" if none. A condition stated in a parent paragraph's
  lead-in belongs to every sub-paragraph under it.
- topic: the sub-topic id from TOPICS the obligation belongs to.

Sentences that state no obligation for the manufacturer (a heading, a definition, a scope statement, a statement
of purpose) go in not_applicable: the paragraph reference, the first 8 or more words copied exactly, and the
reason in a few words.

Write the answers file named in your task: {"answers": [one object per section with "section" set to the section's
"id" exactly]}.
