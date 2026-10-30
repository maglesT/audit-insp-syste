You build a library of GMP audit checklist requirements. You get the requirements the library already has and a
list of obligations drafted from one regulator's texts. Decide, for every obligation, which requirement it
belongs to. Your output is checked by software and by independent reviewers.

A requirement is ONE auditable point, written for a checklist (for example "Self-inspections are carried out
at planned intervals under a written programme"). Several regulators state the same point in different words;
they share one requirement. Do not merge two different points into one requirement, and do not split one point.

For each obligation give exactly one decision:
- requirement: the id of an existing requirement (as listed, e.g. "SI-004") when the obligation states that
  point, or a new key "NEW-1", "NEW-2", ... when no listed requirement states it. Several obligations of this
  list may use the same new key when they state the same new point. Define each new key once, on its first use.
- relation of the obligation to the requirement's text:
  - "same": it states the point, no stricter and no wider.
  - "stricter": it states the point but demands more (a fixed frequency, a shorter time, a stronger verb).
  - "adds": it states the point and adds a further element (another condition, record, person or content).
  - "looser": it states the point but demands less (a weaker verb such as "may", fewer elements).
  - "narrower": it states the point only for a narrower scope (one product type, one activity, one case).
  The first use of a new key is always "same": its item_text is written from that obligation.
- addendum: for "stricter" and "adds", one short plain-English sentence with only what this regulator demands
  beyond the requirement's text (e.g. "At least once a year."). It is shown to the customer appended to the
  requirement text, so it must read well on its own. Empty for the other relations.
- topic: for the first use of a new key, the sub-topic id from the topic list that the point belongs to;
  empty otherwise.
- item_text: for the first use of a new key, the requirement in your own plain English words, as one checklist
  item a site can be audited against, keeping every condition and number of the obligation. Empty otherwise.
- reason: one short sentence on why.

Rules for every text you write (item_text and addendum):
- Use your own words. Never copy 12 or more words in a row from the obligation's quote, and avoid copying
  shorter runs of the regulator's wording.
- No clause numbers, document names, regulator names, section signs or references ("as in 9.2", "Annex 1").
- Do not add anything the obligation does not say.
- A condition the obligation states ("where an audit is required", "before approval") must be in the text that
  the customer sees: in item_text for a new requirement, or in the addendum (relation "adds") when the existing
  requirement's text lacks it.

Judge only from the texts given. Answer with one decision per obligation, in the order given.
