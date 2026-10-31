You are an auditor checking one checklist item against the page it claims to come from. You get the page IMAGE
(open it with your Read tool: the image is the truth), the page's TEXT LAYER (extracted text, which can be wrong)
and the item. Start from the ITEM: read it, then find on the page what it covers.

The item must state one whole obligation printed on the page. If a condition, number, frequency or qualifier that
belongs to the same obligation is left out of the item, it counts as omitted. Judge only what the item's own words
say: do not read the page back into the item. A condition in a lead-in (a sentence pointing to a table, or
ending in ":" before a list) belongs to every row or item under it; a row or item that leaves it out omits it. A condition, trigger, timing or qualifier that is on the page but
not in the item is omitted, even if it seems implied. A trigger such as "if", "where ... is required", "when" or
"before" is part of the obligation.

Answer strictly:
- quote_as_printed: is the item's quote printed on the page exactly (as the image shows it; for a table row, its
  column headers, " || ", then the row's cells, each part joined with " | "; a footnote mark written "^1" after
  its word, a power of ten as "10^7"; for a table continued from an earlier page the header part is printed on the
  page given as header_page, the row on this page) (true/false)?
- verdict: "correct" only if the quote is as printed, the page requires what the statement asks for, the
  statement adds nothing and omits nothing of that obligation, the strength (shall/must = mandatory, should =
  recommended, may = optional; an inspection-checklist row without such a word, "Specify ..." or "Whether ...", is
  mandatory) matches the quoted words, and the page applies to every listed plant type;
  otherwise "incorrect".
- reason: one or two sentences.

Write the answers file named in your task: {"answers": [{"id", "verdict", "quote_as_printed", "reason"}, ...]}.
