You are an auditor checking one checklist item against the regulatory clause it claims to come from. Start
from the ITEM: read it, then look in the clause for each thing the item asks for.

A clause may hold several separate obligations, each turned into its own item. Judge the item against the
part of the clause it covers (given as COVERS), not against the whole clause. But that part must be a whole
obligation: if a condition, number, frequency or qualifier that belongs to the same obligation is left out,
of the item or of the COVERS span, it counts as omitted.

Answer every question strictly:
- required_by_clause: does the clause require what the item asks for (true/false)?
- item_adds: anything the item asks for that the clause does not say (empty string if nothing).
- item_omits: anything belonging to the covered obligation that the item leaves out, including conditions,
  numbers and frequencies (empty string if nothing). Other, separate obligations of the clause are not
  omissions.
- strictness: "same", "stricter" (the item demands more than the clause) or "looser" (less).
- plant_types_ok: is the clause applicable to every listed plant type (true/false)?
- strength_ok: does the item's strength (mandatory / recommended / optional) match the clause's wording
  (shall/must = mandatory, should = recommended, may = optional) (true/false)?
- verdict: "correct" only if required_by_clause and plant_types_ok and strength_ok are true, strictness is
  "same", and item_adds and item_omits are empty; otherwise "incorrect".
- reason: one or two sentences.
