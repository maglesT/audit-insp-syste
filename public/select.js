// Shared by the browser and the server: which items a template/audit shows. ONE rule, used everywhere.
export const MARKETS = {
  india: { label: 'India (Schedule M)', reg: 'Schedule M' },
  eu: { label: 'EU export (EU GMP)', reg: 'EU' },
  us: { label: 'US export (US FDA 21 CFR)', reg: 'US FDA' },
};
// Area names from sample/areas.md (owner-approved area list).
export const AREA_NAMES = {
  QS: 'Quality system', SUP: 'Suppliers and outsourced activities', DOC: 'Documentation and records',
  REL: 'Batch record review and release', CMP: 'Complaints, quality defects, recalls, returns',
  PER: 'Personnel', PREM: 'Premises', UTIL: 'Utilities', EQ: 'Equipment', WH: 'Warehouse',
  PROD: 'Production (non-sterile)', PACK: 'Packaging and labelling', STER: 'Production (sterile)',
  QC: 'QC laboratory', VAL: 'Qualification and validation', CSV: 'Computerised systems and data integrity',
};
export const AUDIENCE_LABELS = {
  manufacturer: 'Manufacturer', 'manufacturer-EU-export': 'Manufacturer exporting to the EU (QP, Site Master File)',
  'MA holder': 'Marketing authorisation holder', 'EU importer': 'EU importer', 'trial sponsor': 'Clinical trial sponsor',
};

// cfg: {markets[], plants[], audiences[], removed{id:reason}}; opts.keepRemoved: also return removed items.
// An item shows if: its regulator is in a chosen market, its plant types include "all" or ANY chosen plant type,
// and its audience is chosen. Background-only items (bg) are returned too; the page hides them unless asked.
export function selectItems(items, cfg, opts = {}) {
  const regs = new Set(cfg.markets.map((m) => MARKETS[m]?.reg).filter(Boolean));
  const plants = new Set(['all', ...(cfg.plants || [])]);
  const auds = new Set(cfg.audiences && cfg.audiences.length ? cfg.audiences : ['manufacturer']);
  const removed = cfg.removed || {};
  return items.filter((it) => regs.has(it.reg) && it.pt.some((p) => plants.has(p)) && auds.has(it.aud)
    && (opts.keepRemoved || !(it.id in removed)));
}

// ---------- audit lines (one model for every screen + the server) ----------
// A template/audit has mode "clauses" (each DUTY sentence of a clause = one line, Yes/No/N/A) or "points" (audit
// layer: each AUDIT POINT = one line, Compliant/Not compliant/N/A + observation + grade; its clauses are shown under it;
// plus "Other requirements (check the clause)": duty units no point covers, Yes/No/N/A like clause mode).
// Company items are lines in both modes (answer set of the mode).
// Keys: clause unit "<itemId>#<n>", point "P:<pointId>", other requirement "O:<itemId>#<n>", company "C:<cid>".
export const ANSWERS = {
  clauses: { set: ['Yes', 'No', 'N/A'], pos: 'Yes', neg: 'No', note: 'Note / evidence' },
  points: { set: ['Compliant', 'Not compliant', 'N/A'], pos: 'Compliant', neg: 'Not compliant', note: 'Observation' },
};
export const GRADES = ['critical', 'major', 'other'];
export const modeOf = (cfg) => (cfg.mode === 'points' ? 'points' : 'clauses');
// answer set of one line: points (and company items in points mode) = Compliant set; units, others = Yes set
export const answersFor = (kind, mode) => ANSWERS[kind === 'point' || (kind === 'company' && mode === 'points') ? 'points' : 'clauses'];
export const POS = new Set(['Yes', 'Compliant']), NEG = new Set(['No', 'Not compliant']);

// Scope (lead audit-admin-2c, 19 Nov): market = the regulator(s) of the entry's clause items (regs); plant types /
// audience = the entry's OWN plant_types / audience when present. Fallback when an entry has no plant_types: it shows
// if ANY of its clause items is selected. Same rule for points and other requirements.
function scopeFilter(data, cfg) {
  const regs = new Set(cfg.markets.map((m) => MARKETS[m]?.reg).filter(Boolean));
  const plants = new Set(['all', ...(cfg.plants || [])]);
  const auds = new Set(cfg.audiences && cfg.audiences.length ? cfg.audiences : ['manufacturer']);
  let live = null;
  return (e, itemIds) => {
    if (e.plant_types && e.plant_types.length) {
      const ea = e.audience ? [].concat(e.audience) : ['manufacturer'];
      return (e.regs || []).some((r) => regs.has(r)) && e.plant_types.some((x) => plants.has(x)) && ea.some((a) => auds.has(a));
    }
    live = live || new Set(selectItems(data.items, { ...cfg, removed: {} }).map((x) => x.id));
    return itemIds.some((id) => live.has(id));
  };
}
export function selectPoints(data, cfg, opts = {}) {
  if (!data.points) return [];
  const inScope = scopeFilter(data, cfg); const removed = cfg.removed || {};
  return data.points.filter((p) => (opts.keepRemoved || !(('P:' + p.id) in removed)) && inScope(p, p.clauses.map((c) => c.item)));
}
export const otherKey = (o) => `O:${o.item}#${o.unit}`;
export function selectOthers(data, cfg, opts = {}) {
  if (!data.other_requirements) return [];
  const inScope = scopeFilter(data, cfg); const removed = cfg.removed || {};
  return data.other_requirements.filter((o) => (opts.keepRemoved || !(otherKey(o) in removed)) && inScope(o, [o.item]));
}

export function auditLines(data, cfg) {
  const lines = []; const mode = modeOf(cfg);
  if (mode === 'points') {
    const byId = new Map(data.items.map((x) => [x.id, x]));
    for (const p of selectPoints(data, cfg)) lines.push({ key: 'P:' + p.id, kind: 'point', area: p.area, point: p });
    for (const o of selectOthers(data, cfg)) {
      const it = byId.get(o.item); const u = it.u.find((x) => x[0] === o.unit);
      lines.push({ key: otherKey(o), kind: 'other', area: o.area, other: o, item: it, n: o.unit, text: it.text.slice(u[1], u[2]) });
    }
  } else {
    for (const it of selectItems(data.items, cfg)) {
      if (it.bg) continue;
      for (const u of it.u) if (u[3] === 1) lines.push({ key: it.id + '#' + u[0], kind: 'unit', area: it.area, item: it, n: u[0], text: it.text.slice(u[1], u[2]) });
    }
  }
  for (const c of cfg.company_items || []) lines.push({ key: 'C:' + c.cid, kind: 'company', area: c.area, company: c, text: c.text });
  return lines;
}

// yes = Yes or Compliant, no = No or Not compliant (each line has one answer set)
export function lineStats(lines, answers) {
  const s = { total: lines.length, yes: 0, no: 0, na: 0 };
  for (const l of lines) { const v = answers[l.key]?.a; if (POS.has(v)) s.yes++; else if (NEG.has(v)) s.no++; else if (v === 'N/A') s.na++; }
  return s;
}

// Find a clause (home page): every term must match. A number term ("1.7", "211.84") matches the reference only, as a whole
// number (1.7 finds 1.7 and 1.7.2, not 11.7 or 1.71); a word term matches reference, title or text. Reference hits first.
export function findItems(items, query, max = Infinity) {
  const terms = (query || '').toLowerCase().match(/[a-z0-9][a-z0-9.()/-]*/g) || [];
  if (!terms.length || terms.join('').length < 2) return [];
  const tests = terms.map((t) => {
    t = t.replace(/[.]+$/, '');
    const esc = t.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
    if (/^\d/.test(t)) { const re = new RegExp('(^|[^\\d.])' + esc + '(?![\\d])'); return { num: true, f: (x) => re.test(x.ref.toLowerCase()) }; }
    return { num: false, f: (x) => x.ref.toLowerCase().includes(t) || x.id.toLowerCase().includes(t) || (x.title || '').toLowerCase().includes(t) || x.text.toLowerCase().includes(t) };
  });
  const hits = items.filter((x) => tests.every((t) => t.f(x)));
  const rank = (x) => (terms.some((t) => x.ref.toLowerCase().includes(t)) ? 0 : 1) + (x.bg ? 1 : 0);
  return hits.map((x, i) => [rank(x), i, x]).sort((a, b) => a[0] - b[0] || a[1] - b[1]).slice(0, max).map((r) => r[2]);
}

// "Ask about this" (lead 2c, 20 Nov): the pre-filled question is built BY CODE from the line (no model text).
// Point: its own question. Clause item: its title, else its first sentence. Other requirement: its duty sentence.
// The user can edit it and must press Send.
function subjectOf(text, max = 200) {
  let s = (text || '').replace(/\s+/g, ' ').trim().replace(/^\(?[0-9ivxlc]+(\.[0-9]+)*[.)]?\s+(?=[A-Z(])/i, '');
  const m = s.match(/^.+?[.;:](?=\s|$)/); if (m && m[0].length >= 20) s = m[0];
  let cut = false;
  if (s.length > max) { s = s.slice(0, max); const sp = s.lastIndexOf(' '); if (sp > max / 2) s = s.slice(0, sp); cut = true; }
  s = s.replace(/[\s.,;:—–-]+$/, ''); return cut ? s + ' …' : s;
}
export function askQuestionFor(x) {
  if (x.point) return x.point.question;
  const subj = x.other ? subjectOf(x.text) : x.item.title ? subjectOf(x.item.title) : subjectOf(x.item.text);
  return `What do the regulations require about: ${subj}?`;
}
