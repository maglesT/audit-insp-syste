You read an FDA web page (a Q&A page on CGMP, a Guide to Inspections, an Inspection Technical Guide, a Compliance
Policy Guide or an alert to manufacturers) and list what it expects of a drug manufacturer. Each unit is given as
its paragraphs, each with its reference ("Q4.2" on a Q&A page: question 4, answer paragraph 2; "¶17" elsewhere) and
its exact text; "context" entries are headings or labels (not citable); "list_item" marks a list item, whose
lead-in is the paragraph ending in ":" above it. Your output is checked by software against that exact text and by
independent reviewers, so precision matters more than wording.

List each separate expectation as its own item, so that together your items cover every expectation in the unit.
One expectation is one thing a manufacturer must, should or may do, with all its conditions, numbers and
qualifiers; do not split one expectation across items. What counts:
- what FDA says a firm must, should or may do ("FDA expects firms to have written procedures ...", "manufacturers
  should ...", "are required by the CGMP regulations to ...");
- in a Guide to Inspections or Inspection Technical Guide, what the investigator is told to check ("Determine
  whether the firm has validated ...", "Check that ...", "Review the ..."): write the practice the firm is expected
  to have ("Validate ..."), not the investigator's task. When the text only says what to look at ("Examine the
  design of equipment") and states no expectation, write the expectation the text itself gives in the same
  paragraph; if it gives none, put the sentence in not_applicable ("inspection step without a stated expectation").
For each item:
- statement: the expectation in your own plain English words, as one checklist item a site could be audited
  against. Do not copy more than a few words in a row. Keep every condition ("where", "if", "unless", "when",
  "except") and every number. Do not add anything the text does not say. The statement itself must carry every
  condition or qualifier of the lead-in above a list item. The statement is shown to customers: never cite a
  regulation, section, question or paragraph number in it ("21 CFR 211.42(d)", "Q4", "see above"); say what is
  required instead.
- quote: the exact span of ONE paragraph's text that states the whole expectation, copied character for character
  (matched against the page text by software; do not fix typos or change punctuation, keep footnote marks as
  printed). A quote may continue into the paragraphs after it in the same unit, in order (e.g. a lead-in and its
  list items), but must start in the cited paragraph.
- clause_number: the reference of the paragraph the quote starts in, exactly as given ("Q4.2", "¶17").
- strength: "mandatory" where the text states a legal requirement (shall / must / is required / may not, "the
  CGMP regulations require"); "recommended" for should, "FDA expects", "FDA recommends", and for an inspection
  point; "optional" for may / is acceptable. A list item without such a word takes its lead-in's.
- plant_types: from OSD, LIQ, SEMI, INJ, API (INJ = sterile injectables); the plant scope given unless the text
  narrows it. Text limited to non-sterile products does not apply to INJ; text limited to sterile products
  (parenterals, aseptic processing, terminal sterilization) applies only to INJ (and API where in scope). Text
  that rests on the CGMP regulations for finished pharmaceuticals (21 CFR 210/211, "drug product manufacturers",
  "finished drug products") does not apply to API unless it speaks of APIs or bulk drug substances too.
- numbers: every number, limit, frequency or period in the quote, as written (not regulation references).
- condition: the condition or trigger in a few words, "" if none. This field only repeats what the statement
  already says.
- topic: the sub-topic id from TOPICS the expectation belongs to.

Do not narrow or widen a term. Where the text gives examples ("such as ..."), keep them as examples; where it
gives a closed list, keep it closed.

Sentences that state no expectation for the manufacturer go in not_applicable: the question itself, background and
history, definitions, descriptions of what happened at a firm, FDA's own actions or enforcement, statements of
purpose or scope, references, an inspection step without a stated expectation. One entry per SENTENCE, each with
the paragraph reference, the sentence's first 8 or more words copied exactly, and the reason in a few words. A
sentence with "should", "must", "FDA expects" or an instruction to the investigator needs an item or a
not_applicable entry.

Write the answers file named in your task: {"answers": [one object per unit with "unit" set to the unit's "id"
exactly, "items" and "not_applicable"]}.
