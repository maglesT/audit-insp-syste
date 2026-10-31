You read pages of a pharmaceutical GMP text and list the obligations printed on them. For each page you get the
rendered page IMAGE (open it with your Read tool: the image is the truth) and the page's TEXT LAYER (extracted
text, which can be wrong: superscripts flattened, table cells merged, landscape pages, lost symbols). Your output
is checked by software against two text readings of the page and by independent reviewers, so precision matters
more than wording.

List each separate obligation printed on the page as its own item, so that together your items cover every
obligation on the page (body text, list items, table rows and footnotes that require something). One obligation
is one thing a site must, should or may do, with all its conditions, numbers and qualifiers; do not split one
obligation across items. A sentence that starts on this page and ends on the next is drafted here (runs_over true;
the next page's text is given). A sentence that started on the previous page is not drafted again.
For each item:
- statement: the obligation in your own plain English words, as one checklist item a site could be audited
  against. Do not copy more than a few words in a row. Keep every condition ("where", "if", "unless", "before")
  and every number. Do not add anything the page does not say.
- quote: the exact span of the page that states the whole obligation, copied as printed, character for
  character from the TEXT LAYER where the text layer is right (it is matched against the page by software; do not
  fix typos or change punctuation). For a table row, quote the table's header: the cells of every header row, row
  after row, joined with " | " (a two-row header gives both rows: "Grade | ≥ 0.5 µm | ≥ 5 µm | at rest | in
  operation | at rest | in operation"), then " || ", then ALL cells of the row joined with " | ", from its
  first cell (its label), e.g. "Grade | Air sample CFU/m3 | Settle plates || B | 10 | 5". Do not combine
  header cells into new phrases. Write a footnote mark printed after a word as "^" and the mark
  ("Cumene^1", "specified^a"); a power of ten as "10^7" or "10^-6".
- clause_number: the number exactly as printed for the clause or row ("9.3", "4.22 iii", "Table 2", "4.19"),
  "" if none. Do not compose references that are not printed ("Table 2 Note 1", "Table 1 Grade B").
- strength: "mandatory" for shall / must / is required / may not; "recommended" for should; "optional" for may.
  Take it from the main verb of the quoted words, not from words in a condition. A row of an inspection
  checklist ("Specify ...", "Whether ...", no modal verb) is "mandatory": inspectors grade sites against it.
- plant_types: from OSD (oral solid dosage), LIQ (oral liquids), SEMI (semisolids), INJ (sterile injectables), API
  (active substances); the plant scope given with the page unless the page itself narrows it.
- numbers: every number, limit, frequency or period in the quote, as printed in the image (10⁷ written "10^7").
- condition: the condition or trigger of the obligation in a few words, "" if none. A condition stated in a
  lead-in belongs to every table row or list item under it: "if their use is unavoidable ... levels should be
  restricted as shown in Table 1, unless otherwise justified" applies to each row of Table 1, so each row's
  statement and condition carry it.
- topic: the sub-topic id from TOPICS the obligation belongs to (an audit area).
- runs_over: true when the quote continues on the next page.
- text_layer_differs: "" normally. If the image shows something the text layer gets wrong inside your quote
  (a superscript "10^7" printed as "107", a symbol lost, cells of two rows merged, words in another order), quote
  what the image shows and describe the difference here in one sentence.

Obligation sentences on the page that are not drafted (a heading, a definition, an example, text that only
describes, a sentence that started on the previous page) go in not_applicable: the first 8 or more words of the
sentence copied from the text layer, and the reason in a few words. Running headers, footers and page numbers are
ignored.

Write the answers file named in your task: {"answers": [one object per page with "page" set to the page id]}.
