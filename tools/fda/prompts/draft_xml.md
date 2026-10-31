You read sections of a US regulation (21 CFR, from the official eCFR XML) and list the obligations they state. Each
section is given as its paragraphs, each with its reference from the XML structure ("211.84(c)(1)") and its exact
text. Your output is checked by software against that exact text and by independent reviewers, so precision
matters more than wording.

List each separate obligation as its own item, so that together your items cover every obligation in the section.
One obligation is one thing a manufacturer must, should or may do, with all its conditions, numbers and
qualifiers; do not split one obligation across items. For each item:
- statement: the obligation in your own plain English words, as one checklist item a site could be audited
  against. Do not copy more than a few words in a row. Keep every condition ("where", "if", "unless", "when",
  "except") and every number. Do not add anything the text does not say. The statement itself must carry every
  condition or qualifier of the lead-ins above its paragraph (a parent paragraph ending in ":", and its parent if
  that also ends in ":"): for 211.42(c)(1) under "... such other control systems ... as are necessary to prevent
  contamination or mixups during the course of the following procedures:", write e.g. "Provide separate or defined
  areas, or other control systems as necessary to prevent contamination or mixups, for receipt ...". Putting the
  qualifier only in the condition field is not enough. The statement is shown to customers: never cite a
  paragraph or section reference in it ("211.166(a)(1)-(5)", "this section"); say what is required instead
  ("contains the elements listed below" is not enough: name them, or let each sub-paragraph's own item carry it).
- quote: the exact span of ONE paragraph's text that states the whole obligation, copied character for character
  (matched against the XML text by software; do not fix typos or change punctuation). Leave out the paragraph's
  designation ("(c)"). A quote may continue into that paragraph's sub-paragraphs, in order.
- clause_number: the reference of the paragraph the quote comes from, exactly as given ("211.84(c)(1)").
- strength: "mandatory" for shall / must / is required / may not; "recommended" for should; "optional" for may.
  A sub-paragraph without such a word takes its parent's lead-in ("(c) Samples shall be collected in accordance
  with the following procedures:" makes (c)(1)-(c)(6) mandatory).
- plant_types: from OSD, LIQ, SEMI, INJ, API (INJ = sterile injectables); the plant scope given unless the text
  narrows it. A paragraph limited to drug products not required to be sterile does not apply to INJ; one limited to
  sterile drug products ("purporting to be sterile") applies only to INJ (and API where in scope).
- numbers: every number, limit, frequency or period in the quote, as written.
- condition: the condition or trigger in a few words, "" if none. A condition stated in a parent paragraph's
  lead-in belongs to every sub-paragraph under it. This field only repeats what the statement already says.

A lead-in sentence that also states a duty of its own ("The written program shall be followed and shall include:")
needs its own item for that duty, quoting the whole sentence including "shall include:". That item states only the
lead-in's own duty ("follow the written stability program"); do not summarise the sub-paragraphs in it (their
items carry them with their qualifiers). Where the text refers to a closed list of other sections ("operations
addressed by §§ 211.101(c) or (d), 211.103 ..."), keep the list closed: name the operations, never "such as".
Do not narrow or widen a term ("washing facilities" is not "hand-washing facilities"; "in and from" is not "from").
- topic: the sub-topic id from TOPICS the obligation belongs to.

Sentences that state no obligation for the manufacturer (a heading, a definition, a scope statement, a statement
of purpose, an exemption, an enforcement or interpretation statement addressed to FDA) go in not_applicable: one
entry per SENTENCE (a paragraph of three such sentences needs three entries), each with the paragraph reference,
the sentence's first 8 or more words copied exactly (without the paragraph designation), and the reason in a few
words.

Write the answers file named in your task: {"answers": [one object per section with "section" set to the section's
"id" exactly]}.
