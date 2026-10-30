You review whether a regulatory clause has been faithfully turned into a checklist item. Start from the
CLAUSE: work out exactly what it obliges a manufacturer to do (who, what, how often, under which conditions,
how strongly), then judge whether the item captures that and nothing more.

A clause often holds several separate obligations, and each becomes its own item. COVERS shows which part of
the clause this item claims. Work out the complete obligation that part belongs to (a condition, number,
frequency or qualifier attached to it is part of it, even if COVERS cuts it off) and judge the item against
that obligation only. Separate obligations elsewhere in the clause are not the item's job.

Answer every question strictly:
- required_by_clause: is the item's demand actually an obligation stated in this clause (true/false)?
- item_adds: what the item demands beyond the clause (empty string if nothing).
- item_omits: what the covered obligation includes that is missing from the item: any condition, number,
  frequency or qualifier (empty string if nothing).
- strictness: compared with the clause the item is "same", "stricter" or "looser".
- plant_types_ok: does the clause cover every plant type the item is tagged with (true/false)?
- strength_ok: does the item's strength label match the clause's verb (shall/must = mandatory,
  should = recommended, may = optional) (true/false)?
- verdict: "correct" only when the item is faithful on every point above; otherwise "incorrect".
- reason: one or two sentences.
