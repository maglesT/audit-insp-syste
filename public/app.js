// Medhanta CLEAR: browser app (no framework). All data text goes in via textContent (never innerHTML).
import { MARKETS, AREA_NAMES, AUDIENCE_LABELS, ANSWERS, GRADES, POS, NEG, answersFor, selectItems, selectPoints, selectOthers, otherKey, auditLines, lineStats, modeOf, findItems, askQuestionFor } from './select.js';

const $app = document.getElementById('app');
const $nav = document.getElementById('nav');
let DATA = null, ME = null, BYID = null, licNoted = false; // licNoted: WHO/PIC/S licence note shown once per list

// ---------- tiny DOM helper ----------
const add = (e, ...kids) => { for (const k of kids.flat(9)) if (k != null && k !== false) e.append(k); return e; };
function h(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (k === 'class') e.className = v;
    else if (k === 'value') e.value = v;
    else if (k === 'checked') e.checked = !!v;
    else e.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat(9)) if (k != null && k !== false) e.append(k instanceof Node ? k : String(k));
  return e;
}
async function call(method, url, body) {
  const r = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'mac' }, body: body ? JSON.stringify(body) : undefined });
  const j = r.headers.get('content-type')?.includes('json') ? await r.json() : null;
  if (r.status === 401 && url !== '/api/login') { ME = null; keepNext(location.hash); location.hash = '#/login'; throw new Error('Please log in'); }
  if (!r.ok) throw new Error(j?.error || 'Error ' + r.status);
  return j;
}
const fmtDate = (s) => (s ? new Date(s).toLocaleString() : '');
// Rights (server checks every action; the page only hides what the person cannot do). Standalone: all rights.
const can = (code) => !!ME?.permissions?.includes(code);
const PLATFORM = () => ME?.mode === 'platform';

// ---------- boot / router ----------
async function loadData() {
  if (DATA) return;
  $app.replaceChildren(h('p', { class: 'muted pad' }, 'Loading the checklist library…'));
  DATA = await (await fetch('/data/items.json')).json();
  BYID = new Map(DATA.items.map((x) => [x.id, x]));
}
async function route() {
  const hash = location.hash || '#/';
  const [, view, id] = hash.match(/^#\/([a-z]*)\/?([^/?]*)/) || [];
  if (view !== 'login' && !ME) {
    try { ME = await call('GET', '/api/me'); } catch { return; }
    // back from Medhanta sign-in (platform): open the page that was asked for before
    if (!view) { const nx = takeNext(); if (nx !== '#/') { location.hash = nx; return; } }
  }
  drawNav(view); licNoted = false;
  window.scrollTo(0, 0);
  try {
    if (view === 'login') return viewLogin();
    await loadData();
    if (view === 'template') return viewTemplate(id);
    if (view === 'audit') return viewAudit(id);
    if (view === 'print') return viewPrint(id);
    if (view === 'definitions') return viewDefinitions();
    if (view === 'ask') return viewAsk();
    if (view === 'account') return viewAccount();
    if (view === 'item') return viewItem(decodeURIComponent(id));
    return viewHome();
  } catch (e) { $app.replaceChildren(h('p', { class: 'err' }, e.message)); }
}
function drawNav(view) {
  if (!ME) { $nav.replaceChildren(); return; }
  const a = (href, label, v) => h('a', { href, class: view === v ? 'on' : '' }, label);
  $nav.replaceChildren(a('#/', 'Templates & audits', ''), a('#/definitions', 'Definitions', 'definitions'), PLATFORM() ? null : a('#/ask', 'Ask', 'ask'),
    a('#/account', ME.name, 'account'),
    h('button', { onclick: async () => { const r = await call('POST', '/api/logout'); ME = null; takeNext(); if (r?.logoutUrl) { location.href = r.logoutUrl; return; } location.hash = '#/login'; } }, 'Log out'));
}
let skipNext = false;
window.addEventListener('hashchange', () => { if (skipNext) { skipNext = false; return; } if (!leaveGuard()) return; route(); });
route();
let dirty = false;
function leaveGuard() { if (dirty && !confirm('You have unsaved changes. Leave this page?')) { skipNext = true; history.back(); return false; } dirty = false; return true; }
window.addEventListener('beforeunload', (e) => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });

// ---------- login ----------
// After login, go back to the page that was asked for (lead 2c, 20 Nov): only an in-app '#/...' route, never #/login.
const okNext = (x) => typeof x === 'string' && /^#\/[A-Za-z0-9._~%\/-]*$/.test(x) && !/^#\/login\b/.test(x) && x.length < 300;
let nextHash = null;
function keepNext(x) { if (!okNext(x)) return; nextHash = x; try { sessionStorage.setItem('mac_next', x); } catch { /* storage off: in-memory only */ } }
function takeNext() { let x = nextHash; nextHash = null; try { x = x || sessionStorage.getItem('mac_next'); sessionStorage.removeItem('mac_next'); } catch { /* ignore */ } return okNext(x) ? x : '#/'; }
function viewLogin() {
  // Platform: sign-on through Medhanta core (/login starts the OIDC flow). /api/health tells which installation this is.
  fetch('/api/health').then((r) => r.json()).then((hl) => {
    if (hl.mode !== 'platform') return;
    $app.replaceChildren(h('div', { class: 'panel login' }, h('img', { src: '/brand/clear-logo.svg', alt: 'Medhanta CLEAR' }), h('h1', {}, 'Medhanta CLEAR'), h('p', { class: 'muted small' }, 'Compliance Library for Evaluation and Audit Readiness'),
      h('p', {}, 'Sign in with your Medhanta login.'), h('a', { class: 'btn pri', href: '/login' }, 'Sign in')));
  }).catch(() => {});
  const em = h('input', { type: 'email', autocomplete: 'username', required: true });
  const pw = h('input', { type: 'password', autocomplete: 'current-password', required: true });
  const err = h('div', { class: 'err' });
  const f = h('form', { class: 'panel login', onsubmit: async (e) => {
    e.preventDefault(); err.textContent = '';
    try { await call('POST', '/api/login', { email: em.value, password: pw.value }); ME = null; location.hash = takeNext(); route(); }
    catch (x) { err.textContent = x.message; }
  } }, h('img', { src: '/brand/clear-logo.svg', alt: 'Medhanta CLEAR' }), h('h1', {}, 'Medhanta CLEAR'), h('p', { class: 'muted small' }, 'Compliance Library for Evaluation and Audit Readiness'),
  h('label', { class: 'f' }, 'E-mail', em), h('br'), h('label', { class: 'f' }, 'Password', pw), err, h('br'),
  h('button', { class: 'btn pri', type: 'submit' }, 'Log in'));
  $app.replaceChildren(f); em.focus();
}

// ---------- home: templates + audits ----------
async function viewHome() {
  const [tpls, audits] = await Promise.all([call('GET', '/api/templates'), call('GET', '/api/audits')]);
  const tl = h('div', { class: 'list' });
  if (!tpls.length) tl.append(h('p', { class: 'muted' }, 'No templates yet. Make one: choose your markets and plant types, remove what does not apply, add your own items.'));
  for (const t of tpls) {
    const pts = modeOf(t.config) === 'points';
    const n = pts ? selectPoints(DATA, t.config) : selectItems(DATA.items, t.config).filter((x) => !x.bg);
    const cp = auditLines(DATA, t.config).length;
    tl.append(h('div', { class: 'li' },
      h('div', {}, h('div', { class: 'ctitle' }, t.name),
        h('div', { class: 'small muted' }, t.config.markets.map((m) => MARKETS[m].label).join(' · '), ' — ',
          t.config.plants.length ? t.config.plants.join(', ') : 'general GMP only'),
        h('div', { class: 'small muted' }, `${pts ? (isBeta() ? 'audit points (Beta) · ' : 'audit points · ') : ''}${n.length} ${pts ? 'points' : 'items'} · ${cp} lines to answer · ${Object.keys(t.config.removed).length} removed · ${t.config.company_items.length} company items · saved ${fmtDate(t.updated)}`)),
      h('div', { class: 'row' }, h('a', { class: 'btn sm', href: '#/template/' + t.id }, can('audit.template.edit') ? 'Edit' : 'View'),
        can('audit.audit.perform') && h('button', { class: 'btn sm pri', onclick: () => startAudit(t) }, 'Start audit'),
        can('audit.template.edit') && h('button', { class: 'btn sm', onclick: () => copyTemplate(t) }, 'Copy'),
        can('audit.template.edit') && h('button', { class: 'btn sm danger', onclick: async () => { if (confirm(`Delete template "${t.name}"? Audits made from it stay.`)) { await call('DELETE', '/api/templates/' + t.id); route(); } } }, 'Delete'))));
  }
  const al = h('div', { class: 'list' });
  if (!audits.length) al.append(h('p', { class: 'muted' }, 'No audits yet. Start one from a template.'));
  for (const a of audits) {
    const done = a.yes + a.no + a.na; const w = (x) => a.total ? (100 * x / a.total) + '%' : '0';
    al.append(h('div', { class: 'li' },
      h('div', {}, h('div', { class: 'ctitle' }, a.name, ' ', h('span', { class: 'badge' }, a.status)),
        h('div', { class: 'small muted' }, [a.site, a.auditor, a.audit_date].filter(Boolean).join(' · '), a.site || a.auditor || a.audit_date ? ' · ' : '', 'template: ', a.template_name),
        h('div', { class: 'row small' }, h('div', { class: 'bar' }, h('i', { class: 'y', style: 'width:' + w(a.yes) }), h('i', { class: 'n', style: 'width:' + w(a.no) }), h('i', { class: 'na', style: 'width:' + w(a.na) })),
          `${done}/${a.total} answered · ${a.mode === 'points' ? 'Not compliant' : 'No'}: ${a.no}`)),
      h('div', { class: 'row' }, h('a', { class: 'btn sm pri', href: '#/audit/' + a.id }, 'Open'),
        h('a', { class: 'btn sm', href: `/api/audits/${a.id}/export.xlsx` }, 'Excel'),
        h('a', { class: 'btn sm', href: `/api/audits/${a.id}/export.pdf` }, 'PDF'),
        h('a', { class: 'btn sm', href: '#/print/' + a.id }, 'Print'),
        can('audit.audit.close') && a.status === 'open' && h('button', { class: 'btn sm danger', onclick: async () => { const reason = prompt(`Withdraw audit "${a.name}"? It is kept, marked withdrawn. Reason:`); if (reason?.trim()) { await call('DELETE', '/api/audits/' + a.id, { reason }); route(); } } }, 'Withdraw'))));
  }
  $app.replaceChildren(findBox(),
    h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, 'Templates'), can('audit.template.edit') && h('a', { class: 'btn pri', href: '#/template/new' }, '+ New template')),
    h('div', { class: 'panel' }, tl),
    h('h1', {}, 'Audits'), h('div', { class: 'panel' }, al),
    h('p', { class: 'small muted' }, `Library: ${DATA.counts.items} regulation items (Schedule M, EU GMP, US 21 CFR), version ${DATA.version}.`));
}
// Find a clause without knowing its link (lead 2c, 20 Nov): reference number or words; links to #/item/<id>.
function findBox() {
  const inp = h('input', { type: 'search', placeholder: 'e.g. 1.7, 211.84, supplier', 'aria-label': 'Find a clause', autocomplete: 'off' });
  const out = h('div', { class: 'findres' }); let t = null;
  const run = () => {
    const all = findItems(DATA.items, inp.value); out.replaceChildren();
    if (inp.value.trim().length < 2) return;
    if (!all.length) { out.append(h('p', { class: 'small muted' }, 'No clause found.')); return; }
    out.append(h('p', { class: 'small muted' }, all.length > 50 ? `First 50 of ${all.length}. Add a word to narrow it down.` : `${all.length} found.`));
    for (const x of all.slice(0, 50)) out.append(h('a', { class: 'li findhit', href: '#/item/' + encodeURIComponent(x.id) },
      h('span', { class: 'ref' }, x.ref), ' ', h('span', { class: 'badge' }, x.reg), ' ', h('span', { class: 'small muted' }, (x.title ? x.title + ': ' : '') + x.text.slice(0, 140) + (x.text.length > 140 ? '…' : ''))));
  };
  inp.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 200); });
  return h('div', { class: 'panel find' }, h('label', { class: 'f' }, h('b', {}, 'Find a clause'), inp), out);
}
async function startAudit(t) {
  const name = prompt('Audit name', `${t.name} – ${new Date().toISOString().slice(0, 10)}`);
  if (name == null) return;
  const r = await call('POST', '/api/audits', { template_id: t.id, name, audit_date: new Date().toISOString().slice(0, 10), auditor: PLATFORM() ? undefined : ME.name });
  location.hash = '#/audit/' + r.id;
}
async function copyTemplate(t) {
  const name = prompt('Name of the copy', t.name + ' (copy)'); if (name == null) return;
  await call('POST', '/api/templates', { name, config: t.config }); route();
}

// ---------- shared card rendering ----------
function renderTables(it) {
  return (it.tables || []).map((tb) => h('div', { class: 'tbl' },
    tb.title || tb.caption ? h('div', { class: 'small muted' }, [tb.caption, tb.title].filter(Boolean).join(': ')) : null,
    h('table', {}, (tb.header || []).map((r) => h('tr', {}, r.map((c) => h('th', {}, c)))), (tb.rows || []).map((r) => h('tr', {}, r.map((c) => h('td', {}, c))))),
    tb.notes ? h('div', { class: 'small muted' }, [].concat(tb.notes).join(' ')) : null));
}
function cardHead(it, extra) {
  return [h('div', { class: 'chead' }, h('span', { class: 'ref' }, it.ref), h('span', { class: 'badge' }, it.reg),
    it.bg ? h('span', { class: 'badge info' }, it.def ? 'definition' : 'background') : null,
    it.aud !== 'manufacturer' ? h('span', { class: 'badge' }, AUDIENCE_LABELS[it.aud] || it.aud) : null, extra),
  it.path?.length ? h('div', { class: 'path' }, it.path.join(' › ')) : null,
  it.title ? h('div', { class: 'ctitle' }, it.title) : null,
  it.lead ? h('div', { class: 'lead' }, it.lead) : null];
}
function alsoLine(it) { return alsoRefs(it.refs); }
// "Also" refs (owner via lead 2c, 20 Nov): a SHOWN regulator's ref (EU / US FDA / Schedule M, text in DATA.ref_texts) is a
// toggle that opens its full clause text below; WHO / PIC/S stay plain numbers (licence: cite only), with one note per list.
const LIC = 'WHO / PIC/S: clause number only (text not reproduced, licence)';
const CITE_ONLY = /^(WHO|PIC\/S)\b/;
function alsoToggle(ref, panes) {
  let pane = null;
  const b = h('button', { type: 'button', class: 'alsoref', 'aria-expanded': 'false', title: 'Show the text of ' + ref, onclick: () => {
    if (pane) { pane.remove(); pane = null; b.setAttribute('aria-expanded', 'false'); return; }
    pane = h('div', { class: 'card alsocard' }, h('div', { class: 'chead' }, h('span', { class: 'ref' }, ref)), h('div', { class: 'text' }, DATA.ref_texts[ref]));
    panes.append(pane); b.setAttribute('aria-expanded', 'true');
  } }, ref);
  return b;
}
function alsoRefs(refs) {
  if (!refs?.length) return null;
  const line = h('div', { class: 'also' }, 'Also: '); const panes = h('div', { class: 'alsotexts' }); let cite = false;
  refs.forEach((r, i) => {
    if (i) line.append(' · ');
    if (DATA.ref_texts?.[r]) line.append(alsoToggle(r, panes));
    else { const c = CITE_ONLY.test(r); cite = cite || c; line.append(h('span', c ? { title: LIC } : {}, r)); }
  });
  const note = cite && !licNoted ? h('div', { class: 'small muted licnote' }, LIC) : null; if (note) licNoted = true;
  return add(h('div', { class: 'alsobox' }), line, panes, note);
}
// Template view: whole clause, duty sentences normal, information sentences grey.
// paint text[from, to) with layers [{ranges: [[s, e], ...] (absolute offsets), cls}]: one span per segment, its classes
// = every layer covering it. Used for editor insertions (ed), Ask highlights (hl) and question words (term).
function paint(text, from, to, layers) {
  const cuts = new Set([from, to]);
  for (const L of layers) for (const [s, e] of L.ranges || []) if (e > from && s < to) { cuts.add(Math.max(s, from)); cuts.add(Math.min(e, to)); }
  const pts = [...cuts].sort((a, b) => a - b); const out = [];
  for (let i = 0; i + 1 < pts.length; i++) {
    const s = pts[i], e = pts[i + 1];
    const cls = layers.filter((L) => (L.ranges || []).some(([a, b]) => a <= s && b >= e)).map((L) => L.cls);
    out.push(cls.length ? h('span', { class: cls.join(' ') }, text.slice(s, e)) : text.slice(s, e));
  }
  return out;
}
// Only the checklist editors' insertions are marked (build_data.py "ed": table/figure placeholders + "inserted"
// cross-references); other [brackets] are the regulation's own words and stay plain.
const edLayer = (it) => ({ ranges: it?.ed || [], cls: 'ed' });
const edLegend = (it) => (it?.ed?.length ? h('div', { class: 'legend' }, h('span', { class: 'ed' }, '[ ]'), ' = reference added by the checklist editors') : null);
function clauseText(it) {
  const d = h('div', { class: 'text' }); let pos = 0; const L = [edLayer(it)];
  for (const [, s, e, duty] of it.u) {
    if (s > pos) add(d, paint(it.text, pos, s, L));
    d.append(add(h('span', { class: duty ? 'u-duty' : 'u-bg' }), paint(it.text, s, e, L))); pos = e;
  }
  if (pos < it.text.length) add(d, paint(it.text, pos, it.text.length, L));
  return [d, edLegend(it)];
}
function matches(it, q) { return !q || it.text.toLowerCase().includes(q) || it.ref.toLowerCase().includes(q) || (it.title || '').toLowerCase().includes(q) || (it.refs || []).some((r) => r.toLowerCase().includes(q)); }

// Groups items by area (area order as in the library), keeps the library order inside.
function byArea(items) { const g = new Map(DATA.areas.map((a) => [a, []])); for (const it of items) g.get(it.area)?.push(it); return g; }

// ---------- audit points (audit layer) ----------
export const BETA = 'Beta – independently checked, not yet expert-certified';
const isBeta = () => DATA.points_status === 'beta';
const betaNote = () => (isBeta() ? h('span', { class: 'badge beta' }, BETA) : null);
const evText = (ev) => [].concat(ev || []).map((e) => (typeof e === 'string' ? e : (e.type ? e.type + ': ' : '') + e.what)).join('; ');
const pointRefs = (p) => [...new Set(p.clauses.map((c) => BYID.get(c.item)?.ref).filter(Boolean))];
function pointMatches(p, q) {
  if (!q) return true;
  return (p.question + ' ' + (p.verify || '') + ' ' + evText(p.evidence)).toLowerCase().includes(q)
    || p.clauses.some((c) => { const it = BYID.get(c.item); return it && matches(it, q); });
}
// The clause text with the units this point covers marked (others normal / grey as usual).
function coveredText(it, units) {
  const on = new Set(units); const d = h('div', { class: 'text' }); let pos = 0; const L = [edLayer(it)];
  for (const [n, s, e, duty] of it.u) {
    if (s > pos) add(d, paint(it.text, pos, s, L));
    d.append(add(h(on.has(n) ? 'mark' : 'span', { class: duty ? 'u-duty' : 'u-bg' }), paint(it.text, s, e, L))); pos = e;
  }
  if (pos < it.text.length) add(d, paint(it.text, pos, it.text.length, L));
  return [d, edLegend(it)];
}
function pointBody(p) {
  const refs = pointRefs(p);
  const det = h('details', { class: 'clauses' }, h('summary', { class: 'small' }, `Regulation clauses (${p.clauses.length}): `, refs.join(' · ')));
  det.addEventListener('toggle', () => {
    if (!det.open || det.dataset.filled) return; det.dataset.filled = 1;
    for (const c of p.clauses) { const it = BYID.get(c.item); if (it) det.append(add(h('div', { class: 'card' }), cardHead(it), coveredText(it, c.units), renderTables(it), alsoLine(it))); }
  });
  return [h('div', { class: 'chead' }, h('span', { class: 'badge co' }, 'Audit point'), p.system ? h('span', { class: 'badge' }, p.system) : null,
      p.modality === 'should' ? h('span', { class: 'badge info' }, 'recommended (should)') : null),
    h('div', { class: 'ctitle', style: 'margin-top:4px' }, p.question),
    p.verify ? h('div', { class: 'small', style: 'margin-top:4px' }, h('b', {}, 'Verify: '), p.verify) : null,
    p.evidence?.length ? h('div', { class: 'small' }, h('b', {}, 'Evidence: '), evText(p.evidence)) : null, ownAlso(p), det];
}

// "Other requirements (check the clause)": one duty sentence no audit point covers; whole clause expandable.
function otherBody(o) {
  const it = BYID.get(o.item); const u = it.u.find((x) => x[0] === o.unit);
  const det = h('details', { class: 'clauses' }, h('summary', { class: 'small' }, 'Show the whole clause'));
  det.addEventListener('toggle', () => { if (det.open && !det.dataset.filled) { det.dataset.filled = 1; det.append(add(h('div', { class: 'card' }), coveredText(it, [o.unit]), renderTables(it))); } });
  return [h('div', { class: 'chead' }, h('span', { class: 'badge' }, 'Other requirement'), h('span', { class: 'ref' }, it.ref), h('span', { class: 'badge' }, it.reg)),
    add(h('div', { class: 'text' }), paint(it.text, u[1], u[2], [edLayer(it)])), it.ed?.some(([a, b]) => a < u[2] && b > u[1]) ? edLegend(it) : null, ownAlso(o), det];
}
// a point's / other requirement's OWN references (subset of its items' refs); the clause cards keep the full list
function ownAlso(x) { return alsoRefs(x.refs); }
function otherSrc(o) { const it = BYID.get(o.item); const u = it.u.find((x) => x[0] === o.unit); return { other: o, item: it, text: it.text.slice(u[1], u[2]) }; }
const otherHeader = () => h('h3', { class: 'otherh' }, 'Other requirements (check the clause)');

// ---------- template builder ----------
async function viewTemplate(id) {
  let t = { name: '', config: { mode: 'clauses', markets: ['india'], plants: [], audiences: ['manufacturer'], removed: {}, company_items: [] } };
  if (id && id !== 'new') t = await call('GET', '/api/templates/' + id);
  const cfg = structuredClone(t.config); cfg.mode = modeOf(cfg);
  const ui = { showBg: false, q: '', open: new Set() };
  const name = h('input', { type: 'text', value: t.name, placeholder: 'Template name, e.g. "Unit 2 – oral solids, EU + US export"', style: 'width:100%', oninput: () => { dirty = true; } });
  const msg = h('span', { class: 'small' });
  const stat = h('div', { class: 'stat' });
  const body = h('div');
  const save = h('button', { class: 'btn pri', onclick: async () => {
    msg.textContent = ''; msg.className = 'small';
    try {
      const payload = { name: name.value.trim() || 'Untitled template', config: cfg };
      if (id && id !== 'new') await call('PUT', '/api/templates/' + id, payload);
      else { const r = await call('POST', '/api/templates', payload); id = String(r.id); history.replaceState(null, '', '#/template/' + id); }
      dirty = false; msg.textContent = 'Saved ✓'; msg.className = 'small ok';
    } catch (e) { msg.textContent = e.message; msg.className = 'small err'; }
  } }, 'Save template');
  if (!can('audit.template.edit')) { save.disabled = true; save.title = 'You can view templates; editing needs the right "Create, edit and delete checklist templates".'; }
  const chip = (label, on, onclick, title) => h('span', { class: 'chip' + (on ? ' on' : ''), title, onclick }, label);
  const settings = h('div', { class: 'panel' });
  function drawSettings() {
    settings.replaceChildren();
    add(settings, h('label', { class: 'f' }, 'Template name', name),
      DATA.points ? [h('div', { class: 'step' }, 'Checklist style'), h('div', { class: 'chips' },
        chip('Regulation clauses (Yes / No / N/A per sentence)', cfg.mode === 'clauses', () => { cfg.mode = 'clauses'; changed(); }),
        chip('Audit points (question + evidence; Compliant / Not compliant)' + (isBeta() ? ' – Beta' : ''), cfg.mode === 'points', () => { cfg.mode = 'points'; changed(); })),
        cfg.mode === 'points' && isBeta() ? h('div', { class: 'small', style: 'margin-top:4px' }, betaNote()) : null] : null,
      h('div', { class: 'step' }, '1. Markets'),
      h('div', { class: 'chips' }, Object.entries(MARKETS).map(([k, m]) => chip(m.label, cfg.markets.includes(k), () => {
        cfg.markets = cfg.markets.includes(k) ? cfg.markets.filter((x) => x !== k) : [...cfg.markets, k]; changed();
      }))),
      h('div', { class: 'step' }, '2. Plant types ', h('span', { class: 'small muted' }, '(general GMP items are always in; add the dosage forms you make)')),
      h('div', { class: 'chips' }, Object.entries(DATA.plant_types).filter(([k]) => k !== 'all').map(([k, d]) => chip(k, cfg.plants.includes(k), () => {
        cfg.plants = cfg.plants.includes(k) ? cfg.plants.filter((x) => x !== k) : [...cfg.plants, k]; changed();
      }, d))),
      h('div', { class: 'step' }, '3. Who is audited'),
      h('div', { class: 'chips' }, DATA.audiences.map((a) => a === 'manufacturer' ? h('span', { class: 'chip fixed' }, AUDIENCE_LABELS[a] + ' (always)')
        : chip(AUDIENCE_LABELS[a] || a, cfg.audiences.includes(a), () => { cfg.audiences = cfg.audiences.includes(a) ? cfg.audiences.filter((x) => x !== a) : [...cfg.audiences, a]; changed(); }))));
  }
  function changed() { dirty = true; drawSettings(); drawBody(); }
  const search = h('input', { type: 'search', placeholder: 'Search text or reference…', oninput: () => { ui.q = search.value.trim().toLowerCase(); drawBody(); } });
  const bgT = h('label', { class: 'small' }, h('input', { type: 'checkbox', onchange: (e) => { ui.showBg = e.target.checked; drawBody(); } }), ' Show background text');
  const removeBtn = (key, act) => h('button', { class: 'btn sm', onclick: () => {
    const why = h('input', { type: 'text', placeholder: 'Reason (required), e.g. "No sterile products made at this site"' });
    const box = h('div', { class: 'reasonbox' }, why, h('button', { class: 'btn sm pri', onclick: () => {
      if (!why.value.trim()) { why.focus(); why.style.borderColor = 'var(--bad)'; return; }
      cfg.removed[key] = why.value.trim(); dirty = true; drawBody();
    } }, 'Remove'), h('button', { class: 'btn sm', onclick: () => box.remove() }, 'Cancel'));
    act().after(box); why.focus();
  } }, 'Remove from template');
  const putBack = (key) => [h('span', { class: 'small' }, 'Removed: ', h('i', {}, cfg.removed[key])),
    h('button', { class: 'btn sm', onclick: () => { delete cfg.removed[key]; dirty = true; drawBody(); } }, 'Put back')];
  function drawBody() {
    const pts = cfg.mode === 'points';
    // all = every candidate (removed included); key = what "removed" uses
    const all = pts ? [...selectPoints(DATA, cfg, { keepRemoved: true }).map((p) => ({ key: 'P:' + p.id, area: p.area, p })),
      ...selectOthers(DATA, cfg, { keepRemoved: true }).map((o) => ({ key: otherKey(o), area: o.area, o, it: BYID.get(o.item) }))]
      : selectItems(DATA.items, cfg, { keepRemoved: true }).map((it) => ({ key: it.id, area: it.area, it }));
    const isRem = (x) => x.key in cfg.removed;
    const ok = (x) => (x.p ? pointMatches(x.p, ui.q) : matches(x.it, ui.q));
    const lines = auditLines(DATA, cfg);
    const live = all.filter((x) => !isRem(x)); const hiddenBg = pts ? 0 : live.filter((x) => x.it.bg).length; const nOther = live.filter((x) => x.o).length;
    stat.replaceChildren(); add(stat, h('b', {}, live.length - hiddenBg - nOther), pts ? ' audit points · ' : ' items · ', nOther ? [h('b', {}, nOther), ' other requirements · '] : null, h('b', {}, lines.length), pts ? ' lines to answer · ' : ' check points (Yes/No/N/A) · ',
      h('b', {}, all.length - live.length), ' removed · ', h('b', {}, cfg.company_items.length), ' company items', hiddenBg ? ` · ${hiddenBg} background items hidden` : '');
    body.replaceChildren();
    for (const [area, xs] of byArea(all)) {
      const companies = cfg.company_items.filter((c) => c.area === area);
      const vis = xs.filter((x) => !isRem(x) && (pts || ui.showBg || !x.it.bg) && ok(x));
      const rem = xs.filter((x) => isRem(x) && ok(x));
      if (!vis.length && !rem.length && !companies.length && ui.q) continue;
      const det = h('details', { class: 'area', open: ui.open.has(area) || (!!ui.q && vis.length < 200) });
      const inner = h('div', { class: 'areabody' });
      det.append(h('summary', {}, h('span', {}, AREA_NAMES[area] || area),
        h('span', { class: 'c' }, `${vis.length} ${pts ? 'points' : 'items'}${companies.length ? ' + ' + companies.length + ' company' : ''}${rem.length ? ' · ' + rem.length + ' removed' : ''}`)), inner);
      const fill = () => {
        inner.replaceChildren(); licNoted = false;
        for (const c of companies) inner.append(companyCard(c));
        inner.append(addCompanyForm(area));
        for (const x of vis.filter((y) => !y.o)) inner.append(templateCard(x));
        const ov = vis.filter((y) => y.o); if (ov.length) { inner.append(otherHeader()); for (const x of ov) inner.append(templateCard(x)); }
        if (rem.length) inner.append(h('details', {}, h('summary', { class: 'small' }, `Removed (${rem.length})`), rem.map((x) => templateCard(x, true))));
      };
      det.addEventListener('toggle', () => { if (det.open) { ui.open.add(area); fill(); } else ui.open.delete(area); });
      if (det.open) fill();
      body.append(det);
    }
  }
  function templateCard(x, removed) {
    const c = h('div', { class: 'card' + (x.it?.bg ? ' bgitem' : '') + (removed ? ' removed' : '') + (x.p ? ' point' : '') });
    const act = h('div', { class: 'cact' });
    if (removed) add(act, putBack(x.key)); else act.append(removeBtn(x.key, () => act));
    const ask = removed ? null : askAbout(x.p ? { point: x.p } : x.o ? otherSrc(x.o) : { item: x.it }, cfg.markets);
    if (x.p) add(c, pointBody(x.p), act, ask);
    else if (x.o) add(c, otherBody(x.o), act, ask);
    else add(c, cardHead(x.it), clauseText(x.it), renderTables(x.it), alsoLine(x.it), act, ask);
    return c;
  }
  function companyCard(ci) {
    const c = h('div', { class: 'card company' });
    add(c, h('div', { class: 'chead' }, h('span', { class: 'badge co' }, 'Company item'), ci.ref ? h('span', { class: 'ref' }, ci.ref) : null),
      ci.title ? h('div', { class: 'ctitle' }, ci.title) : null, h('div', { class: 'text' }, ci.text),
      h('div', { class: 'cact' }, h('button', { class: 'btn sm', onclick: () => c.replaceWith(companyForm(ci.area, ci)) }, 'Edit'),
        h('button', { class: 'btn sm danger', onclick: () => { if (confirm('Delete this company item?')) { cfg.company_items = cfg.company_items.filter((x) => x !== ci); dirty = true; drawBody(); } } }, 'Delete')));
    return c;
  }
  function addCompanyForm(area) { return h('div', { class: 'cact' }, h('button', { class: 'btn sm', onclick: (e) => e.target.parentNode.replaceWith(companyForm(area)) }, '+ Add company item')); }
  function companyForm(area, ci) {
    const title = h('input', { type: 'text', value: ci?.title || '', placeholder: 'Title (optional)' });
    const ref = h('input', { type: 'text', value: ci?.ref || '', placeholder: 'Your reference, e.g. SOP-QA-012 (optional)' });
    const text = h('textarea', { placeholder: 'The requirement to check (your own words)' }, ci?.text || '');
    const ar = h('select', {}, DATA.areas.map((a) => h('option', { value: a, selected: a === area }, AREA_NAMES[a])));
    return h('div', { class: 'card company' }, h('span', { class: 'badge co' }, 'Company item'),
      h('div', { class: 'row', style: 'margin-top:6px' }, title, ref, ar), h('div', { style: 'margin-top:6px' }, text),
      h('div', { class: 'cact' }, h('button', { class: 'btn sm pri', onclick: () => {
        if (!text.value.trim()) { text.focus(); return; }
        const v = { cid: ci?.cid || Math.random().toString(36).slice(2, 12).padEnd(8, '0'), area: ar.value, title: title.value.trim(), ref: ref.value.trim(), text: text.value.trim() };
        if (ci) Object.assign(ci, v); else cfg.company_items.push(v);
        dirty = true; ui.open.add(ar.value); drawBody();
      } }, ci ? 'Save item' : 'Add item'), h('button', { class: 'btn sm', onclick: () => drawBody() }, 'Cancel')));
  }
  drawSettings(); drawBody();
  $app.replaceChildren(h('h1', {}, id && id !== 'new' ? 'Edit template' : 'New template'),
    h('p', { class: 'small muted' }, 'Regulation text is locked. You can remove items (with a reason) and add your own company items.'),
    settings,
    h('div', { class: 'sticky' }, h('div', { class: 'row', style: 'justify-content:space-between' }, stat, h('div', { class: 'row' }, msg, save)),
      h('div', { class: 'row', style: 'margin-top:6px' }, search, cfg.mode === 'points' ? null : bgT)),
    body);
}

// ---------- picked people / rooms / equipment / products ----------
// Platform with the link on: picked from Medhanta (identity / master data), saved with id + values as at saving.
// Standalone or link off: typed names. "Connection to … is off" is shown as the server says it.
const KIND_LABEL = { employee: 'person', room: 'room / area', equipment: 'equipment', product: 'product' };
const linkedKind = (k) => (k === 'employee' ? ME?.links?.identity : ME?.links?.master_data);
const refLabel = (x) => (x.code ? x.code + ' ' : '') + x.name;
function refPicker({ list, kinds, onChange, disabled, placeholder }) {
  const box = h('div', { class: 'picker' }); const chips = h('span', { class: 'chips' }); const res = h('div', { class: 'pickres' });
  let kind = kinds[0];
  const sel = kinds.length > 1 ? h('select', { disabled, onchange: () => { kind = sel.value; inp.placeholder = ph(); res.replaceChildren(); } }, kinds.map((k) => h('option', { value: k }, KIND_LABEL[k]))) : null;
  const ph = () => placeholder || (linkedKind(kind) ? `Find ${KIND_LABEL[kind]}…` : `Type ${KIND_LABEL[kind]} name, Enter`);
  const inp = h('input', { type: 'search', placeholder: ph(), disabled, autocomplete: 'off' });
  const addOne = (x) => {
    if (list.some((y) => (kinds.length > 1 ? y.kind === x.kind : true) && (x.id ? y.id === x.id : !y.id && y.name === x.name))) return;
    list.push(x); draw(); onChange();
  };
  function draw() {
    chips.replaceChildren(...list.map((x, i) => h('span', { class: 'chip fixed', title: x.id ? 'from Medhanta' + (x.version ? ', version ' + x.version : '') : 'typed' },
      (kinds.length > 1 ? KIND_LABEL[x.kind] + ': ' : '') + refLabel(x), disabled ? null : h('button', { class: 'x', title: 'Remove', onclick: () => { list.splice(i, 1); draw(); onChange(); } }, '×'))));
  }
  let t = null;
  inp.addEventListener('input', () => {
    if (!linkedKind(kind)) return;
    clearTimeout(t); t = setTimeout(async () => {
      res.replaceChildren();
      try {
        const rows = await call('GET', `/api/pick/${kind}?q=${encodeURIComponent(inp.value.trim())}`);
        if (!rows.length) res.append(h('span', { class: 'small muted' }, 'Nothing found.'));
        for (const r of rows) res.append(h('button', { class: 'btn sm', onclick: () => { addOne(kinds.length > 1 ? { kind, ...r } : r); inp.value = ''; res.replaceChildren(); } }, refLabel(r)));
      } catch (e) { res.append(h('span', { class: 'err small' }, e.message)); }
    }, 250);
  });
  inp.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || linkedKind(kind)) return;
    e.preventDefault(); const name = inp.value.trim(); if (!name) return;
    addOne(kinds.length > 1 ? { kind, name } : { name }); inp.value = '';
  });
  draw();
  return add(box, chips, disabled ? null : h('span', { class: 'row' }, sel, inp), res);
}

// ---------- audit ----------
async function viewAudit(id) {
  const a = await call('GET', '/api/audits/' + id);
  const cfg = a.config; const answers = a.answers; const mode = modeOf(cfg); const A = ANSWERS[mode];
  if (mode === 'points' && !DATA.points) { $app.replaceChildren(h('p', { class: 'err' }, 'This audit uses audit points, which are not loaded on this server.')); return; }
  const ui = { q: '', filter: 'all', showBg: false, open: new Set() };
  const lines = auditLines(DATA, cfg);
  const status = h('span', { class: 'small muted' });
  let timer = null, saving = Promise.resolve();
  const closed = () => a.status !== 'open';
  const ro = () => closed() || !can('audit.audit.perform');
  // header people / rooms: older audits had one typed auditor text
  const hd = { auditors: a.header?.auditors?.length ? a.header.auditors : a.auditor && !PLATFORM() ? [{ name: a.auditor }] : [], auditees: a.header?.auditees || [], rooms: a.header?.rooms || [] };
  const fields = () => ({ answers, header: hd, name: fName.value, ...(PLATFORM() ? {} : { site: fSite.value }), audit_date: fDate.value });
  function queueSave() {
    status.textContent = 'Saving…'; dirty = true; clearTimeout(timer);
    timer = setTimeout(() => { saving = saving.then(async () => {
      try { const r = await call('PUT', '/api/audits/' + id, fields()); syncSaved(r); status.textContent = 'Saved ✓ ' + new Date().toLocaleTimeString(); dirty = false; }
      catch (e) { status.textContent = 'Not saved: ' + e.message; }
    }); }, 700);
  }
  const fName = h('input', { type: 'text', value: a.name, oninput: () => queueSave(), disabled: ro() });
  const fSite = h('input', { type: 'text', value: a.site || '', placeholder: 'Site / plant', oninput: () => queueSave(), disabled: PLATFORM() || ro() });
  // the server returns what it saved (values from Medhanta as at saving): keep the page in step without redrawing
  function syncSaved(r) {
    if (!r?.header) return;
    for (const f of ['auditors', 'auditees', 'rooms']) r.header[f].forEach((x, i) => { if (hd[f][i] && (hd[f][i].id || '') === (x.id || '')) hd[f][i] = x; });
    for (const [k, v] of Object.entries(r.answers || {})) if (answers[k] && v.links) answers[k].links = v.links;
  }
  const pk = (f, kind) => refPicker({ list: hd[f], kinds: [kind], disabled: ro(), onChange: () => queueSave() });
  const fDate = h('input', { type: 'date', value: a.audit_date || '', onchange: () => queueSave(), disabled: ro() });
  const stat = h('div', { class: 'stat' });
  function counts() {
    const s = lineStats(lines, answers);
    for (const [el, keys] of areaCounters) el.textContent = areaText(keys);
    const g = mode === 'points' ? GRADES.map((x) => [x, lines.filter((l) => answers[l.key]?.grade === x && NEG.has(answers[l.key]?.a)).length]).filter(([, n]) => n) : [];
    const pl = mode === 'points' ? ['Compliant/Yes', 'Not compliant/No'] : ['Yes', 'No'];
    stat.replaceChildren(h('b', {}, s.yes + s.no + s.na), ` of ${s.total} answered · `, h('span', { class: 'ok' }, `${pl[0]} ${s.yes}`), ' · ',
      h('span', { class: 'err' }, `${pl[1]} ${s.no}`), g.length ? ` (${g.map(([x, n]) => n + ' ' + x).join(', ')})` : '', ` · N/A ${s.na}`);
  }
  const cls = (v) => (v ? ' a-' + (POS.has(v) ? 'Yes' : NEG.has(v) ? 'No' : 'NA') : '');
  function ansRow(key, el, kind, hint) {
    const v = answers[key] || {}; const A = answersFor(kind, mode); const graded = A === ANSWERS.points;
    const set = (patch) => { const cur = { ...(answers[key] || {}), ...patch }; for (const k of Object.keys(cur)) if (!cur[k]) delete cur[k]; if (Object.keys(cur).length) answers[key] = cur; else delete answers[key]; };
    const note = h(graded ? 'textarea' : 'input', { type: 'text', class: 'note', placeholder: A.note, value: v.note || '', disabled: ro(),
      oninput: () => { set({ note: note.value }); queueSave(); } });
    if (graded) note.value = v.note || '';
    const grade = graded ? h('select', { class: 'grade', disabled: ro(), onchange: () => { set({ grade: grade.value }); counts(); queueSave(); } },
      h('option', { value: '' }, hint ? `Grade… (suggested: ${hint})` : 'Grade…'), GRADES.map((g) => h('option', { value: g, selected: v.grade === g }, g))) : null;
    const showGrade = () => { if (grade) grade.style.display = answers[key]?.a === A.neg ? '' : 'none'; };
    const btns = A.set.map((x) => h('button', { class: (x === 'N/A' ? 'NA' : x === A.pos ? 'Yes' : 'No') + (v.a === x ? ' on' : ''), disabled: ro(), onclick: () => {
      const nv = answers[key]?.a === x ? '' : x; set({ a: nv, ...(nv !== A.neg ? { grade: '' } : {}) });
      if (grade && nv !== A.neg) grade.value = '';
      btns.forEach((b, i) => b.classList.toggle('on', A.set[i] === nv));
      el.className = el.className.replace(/ a-\S+/g, '') + cls(nv); showGrade(); counts(); queueSave();
    } }, x));
    el.className += cls(v.a); showGrade();
    // rooms / equipment / products this finding names (picked from master data when linked, else typed)
    const lk = (answers[key]?.links || []).slice();
    const lbox = h('div', { class: 'links' }); let shown = false;
    const showLinks = () => { if (shown) return; shown = true; lbox.replaceChildren(h('span', { class: 'small muted' }, 'Names: '),
      refPicker({ list: lk, kinds: ['room', 'equipment', 'product'], disabled: ro(), onChange: () => { set({ links: lk.length ? lk.slice() : '' }); answers[key] && (answers[key].links = lk); queueSave(); } })); };
    if (lk.length) showLinks();
    else if (!ro()) lbox.append(h('button', { class: 'linkbtn small', onclick: showLinks }, '+ room / equipment / product'));
    return h('div', {}, h('div', { class: 'ans' }, btns, grade, note), lbox);
  }
  const want = (key) => { const v = answers[key]?.a; return ui.filter === 'all' || (ui.filter === 'open' && !v) || (ui.filter === 'No' && NEG.has(v)); };
  function itemCard(it) {
    const keys = it.u.filter((u) => u[3]).map((u) => it.id + '#' + u[0]);
    if (!it.bg && !keys.some(want)) return null;
    if (it.bg && ui.filter !== 'all') return null;
    const c = h('div', { class: 'card' + (it.bg ? ' bgitem' : '') }, ...cardHead(it).filter(Boolean));
    let pos = 0;
    for (const [n, s, e, duty] of it.u) {
      const lead = it.text.slice(pos, s).trim(); pos = e;
      const txt = [lead ? lead + ' ' : '', paint(it.text, s, e, [edLayer(it)])];
      if (duty) { const u = h('div', { class: 'unit' }, h('div', { class: 'ut' }, txt)); u.append(ansRow(it.id + '#' + n, u, 'unit')); c.append(u); }
      else c.append(h('div', { class: 'unit bgu' }, h('div', { class: 'infolbl' }, 'information'), txt));
    }
    const tail = it.text.slice(pos).trim(); if (tail) c.append(h('div', { class: 'unit bgu' }, tail));
    return add(c, renderTables(it), alsoLine(it), edLegend(it), askAbout({ item: it }, cfg.markets));
  }
  function pointCard(p) {
    const key = 'P:' + p.id; if (!want(key)) return null;
    const u = h('div', { class: 'unit' }); u.append(ansRow(key, u, 'point', p.grade_hint));
    return add(h('div', { class: 'card point' }), pointBody(p), u, askAbout({ point: p }, cfg.markets));
  }
  function otherCard(o) {
    const key = otherKey(o); if (!want(key)) return null;
    const u = h('div', { class: 'unit' }); u.append(ansRow(key, u, 'other'));
    return add(h('div', { class: 'card other' }), otherBody(o), u, askAbout(otherSrc(o), cfg.markets));
  }
  function companyCard(ci) {
    const key = 'C:' + ci.cid; if (!want(key)) return null;
    const u = h('div', { class: 'unit' }, h('div', { class: 'ut' }, ci.text)); u.append(ansRow(key, u, 'company'));
    return add(h('div', { class: 'card company' }), h('div', { class: 'chead' }, h('span', { class: 'badge co' }, 'Company item'), ci.ref ? h('span', { class: 'ref' }, ci.ref) : null),
      ci.title ? h('div', { class: 'ctitle' }, ci.title) : null, u);
  }
  // display groups per area: clause mode = item cards (bg items optional); points mode = point cards
  const groups = mode === 'points' ? byArea([...selectPoints(DATA, cfg).map((p) => ({ area: p.area, p })), ...selectOthers(DATA, cfg).map((o) => ({ area: o.area, o, it: BYID.get(o.item) }))]) : byArea(selectItems(DATA.items, cfg).map((it) => ({ area: it.area, it })));
  const body = h('div'); let areaCounters = [];
  const areaText = (keys) => { const d = keys.filter((k) => answers[k]?.a).length, no = keys.filter((k) => NEG.has(answers[k]?.a)).length; return `${d}/${keys.length} answered${no ? ` · ${mode === 'points' ? 'Not compliant/No' : 'No'} ${no}` : ''}`; };
  function drawBody() {
    body.replaceChildren(); areaCounters = [];
    for (const [area, xs] of groups) {
      const comp = cfg.company_items.filter((c) => c.area === area && (!ui.q || (c.text + c.title + c.ref).toLowerCase().includes(ui.q)));
      const vis = xs.filter((x) => (x.p ? pointMatches(x.p, ui.q) : x.o ? matches(x.it, ui.q) : (ui.showBg || !x.it.bg) && matches(x.it, ui.q)));
      if (!vis.length && !comp.length) continue;
      const keys = [...comp.map((c) => 'C:' + c.cid), ...vis.flatMap((x) => (x.p ? ['P:' + x.p.id] : x.o ? [otherKey(x.o)] : x.it.bg ? [] : x.it.u.filter((u) => u[3]).map((u) => x.it.id + '#' + u[0])))];
      const cnt = h('span', { class: 'c' }, areaText(keys)); areaCounters.push([cnt, keys]);
      const det = h('details', { class: 'area', open: ui.open.has(area) || (!!ui.q && vis.length < 150) });
      const inner = h('div', { class: 'areabody' });
      det.append(h('summary', {}, h('span', {}, AREA_NAMES[area] || area), cnt), inner);
      const fill = () => { inner.replaceChildren(); licNoted = false; const ov = vis.filter((x) => x.o).map((x) => otherCard(x.o)).filter(Boolean);
        add(inner, comp.map(companyCard), vis.filter((x) => !x.o).map((x) => (x.p ? pointCard(x.p) : itemCard(x.it))), ov.length ? [otherHeader(), ov] : null); if (!inner.childNodes.length) inner.append(h('p', { class: 'small muted' }, 'Nothing here for this filter.')); };
      det.addEventListener('toggle', () => { if (det.open) { ui.open.add(area); fill(); } else ui.open.delete(area); });
      if (det.open) fill();
      body.append(det);
    }
  }
  const search = h('input', { type: 'search', placeholder: 'Search…', oninput: () => { ui.q = search.value.trim().toLowerCase(); drawBody(); } });
  const filt = h('select', { onchange: () => { ui.filter = filt.value; drawBody(); } }, h('option', { value: 'all' }, 'All'), h('option', { value: 'open' }, 'Not answered'), h('option', { value: 'No' }, mode === 'points' ? 'Answered Not compliant / No' : 'Answered No'));
  const bgT = mode === 'points' ? null : h('label', { class: 'small' }, h('input', { type: 'checkbox', onchange: (e) => { ui.showBg = e.target.checked; drawBody(); } }), ' Show background text');
  const closeBtn = h('button', { class: 'btn sm', onclick: async () => {
    const to = closed() ? 'open' : 'closed';
    if (to === 'closed' && !confirm('Close this audit? Answers become read-only (you can re-open it).')) return;
    clearTimeout(timer); await saving;
    await call('PUT', '/api/audits/' + id, { ...fields(), status: to });
    dirty = false; route();
  } }, closed() ? 'Re-open audit' : 'Close audit');
  if (!can('audit.audit.close') || a.status === 'withdrawn') closeBtn.style.display = 'none';
  counts(); drawBody();
  $app.replaceChildren(
    h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, 'Audit'), h('div', { class: 'row' },
      h('a', { class: 'btn sm', href: `/api/audits/${id}/export.xlsx` }, 'Export Excel'), h('a', { class: 'btn sm', href: `/api/audits/${id}/export.pdf` }, 'Download PDF'), h('a', { class: 'btn sm', href: '#/print/' + id }, 'Print'), closeBtn)),
    h('div', { class: 'panel' }, h('div', { class: 'row' }, h('label', { class: 'f', style: 'flex:2' }, 'Audit name', fName), h('label', { class: 'f' }, 'Site', fSite), h('label', { class: 'f' }, 'Date', fDate)),
      h('div', { class: 'row hdrpick' }, h('div', { class: 'f' }, h('b', { class: 'small' }, 'Auditors'), pk('auditors', 'employee')),
        h('div', { class: 'f' }, h('b', { class: 'small' }, 'Auditees'), pk('auditees', 'employee')), h('div', { class: 'f' }, h('b', { class: 'small' }, 'Rooms / areas audited'), pk('rooms', 'room'))),
      mode === 'points' && isBeta() ? h('div', { style: 'margin-top:6px' }, betaNote()) : null,
      h('div', { class: 'small muted', style: 'margin-top:6px' }, 'Template: ', a.template_name, ' · ', mode === 'points' ? 'audit points · ' : '', cfg.markets.map((m) => MARKETS[m].label).join(' · '), ' · ', cfg.plants.length ? cfg.plants.join(', ') : 'general GMP', closed() ? ' · CLOSED (read-only)' : '')),
    h('div', { class: 'sticky' }, h('div', { class: 'row', style: 'justify-content:space-between' }, stat, status), add(h('div', { class: 'row', style: 'margin-top:6px' }), search, filt, bgT)),
    body);
}

// ---------- print / PDF ----------
async function viewPrint(id) {
  const a = await call('GET', '/api/audits/' + id);
  const cfg = a.config; const ans = a.answers; const mode = modeOf(cfg); const A = ANSWERS[mode];
  const lines = auditLines(DATA, cfg); const s = lineStats(lines, ans);
  const tb = h('table', {}, h('tr', {}, h('th', {}, 'Reference'), h('th', {}, mode === 'points' ? 'Audit point' : 'Check point (regulation text)'), h('th', {}, 'Answer'), h('th', {}, A.note)));
  const cell = (v) => h('td', { class: POS.has(v.a) ? 'aYes' : NEG.has(v.a) ? 'aNo' : '' }, (v.a || '–') + (v.grade ? ` (${v.grade})` : ''));
  for (const [area, ls] of byArea(lines)) {
    if (!ls.length) continue;
    tb.append(h('tr', {}, h('th', { colspan: 4 }, AREA_NAMES[area])));
    for (const l of ls) {
      const v = ans[l.key] || {}; let ref, text;
      if (l.kind === 'company') { ref = 'Company item' + (l.company.ref ? ' ' + l.company.ref : ''); text = (l.company.title ? l.company.title + ': ' : '') + l.text; }
      else if (l.kind === 'other') { ref = l.item.ref; text = 'Other requirement (check the clause): ' + l.text; }
      else if (l.kind === 'unit') { ref = l.item.ref + (l.item.refs?.length ? '\nAlso: ' + l.item.refs.join(' · ') : ''); text = l.text; }
      else { ref = pointRefs(l.point).join('\n'); text = (l.point.modality === 'should' ? '(Recommended) ' : '') + l.point.question + (l.point.verify ? '\nVerify: ' + l.point.verify : '') + (l.point.evidence?.length ? '\nEvidence: ' + evText(l.point.evidence) : ''); }
      const names = (v.links || []).map((x) => `${KIND_LABEL[x.kind]}: ${refLabel(x)}`).join('; ');
      tb.append(h('tr', {}, h('td', { style: 'white-space:pre-line' }, ref), h('td', { style: 'white-space:pre-line' }, text), cell(v), h('td', { style: 'white-space:pre-line' }, [v.note, names && 'Names: ' + names].filter(Boolean).join('\n'))));
    }
  }
  const rem = Object.entries(cfg.removed);
  const remName = (k) => BYID.get(k)?.ref || (DATA.points?.find((p) => 'P:' + p.id === k)?.question)
    || (k.startsWith('O:') ? 'Other requirement: ' + (BYID.get(k.slice(2).split('#')[0])?.ref || '') : k);
  $app.replaceChildren(h('div', { class: 'rep' },
    h('div', { class: 'row noprint', style: 'margin-bottom:10px' }, h('a', { class: 'btn pri', href: `/api/audits/${id}/export.pdf` }, 'Download PDF'), h('button', { class: 'btn', onclick: () => window.print() }, 'Print'), h('a', { class: 'btn', href: '#/audit/' + id }, 'Back to audit')),
    h('h1', {}, a.name),
    h('p', {}, [a.site && 'Site: ' + a.site, a.auditor && 'Auditor: ' + a.auditor, a.header?.auditees?.length && 'Auditees: ' + a.header.auditees.map((x) => x.name).join(', '),
      a.header?.rooms?.length && 'Rooms / areas: ' + a.header.rooms.map(refLabel).join(', '), a.audit_date && 'Date: ' + a.audit_date, 'Status: ' + a.status + (a.withdrawn_reason ? ' (' + a.withdrawn_reason + ')' : '')].filter(Boolean).join(' · ')),
    mode === 'points' && isBeta() ? h('p', { class: 'small' }, h('b', {}, 'Audit points: ' + BETA)) : null,
    h('p', { class: 'small' }, 'Template: ', a.template_name, ' · Markets: ', cfg.markets.map((m) => MARKETS[m].label).join(', '), ' · Plant types: ', ['general GMP', ...cfg.plants].join(', ')),
    h('p', {}, h('b', {}, `${s.total} ${mode === 'points' ? 'lines (audit points + other requirements)' : 'check points'}: ${mode === 'points' ? 'Compliant/Yes' : 'Yes'} ${s.yes} · ${mode === 'points' ? 'Not compliant/No' : 'No'} ${s.no} · N/A ${s.na} · not answered ${s.total - s.yes - s.no - s.na}`)),
    tb,
    rem.length ? [h('h2', {}, 'Removed from the template'), h('table', {}, h('tr', {}, h('th', {}, 'Removed'), h('th', {}, 'Reason')), rem.map(([k, why]) => h('tr', {}, h('td', {}, remName(k)), h('td', {}, why))))] : null,
    h('p', { class: 'small muted' }, `Printed ${new Date().toLocaleString()} · Medhanta CLEAR · library ${a.data_version}. Not affiliated with or endorsed by CDSCO, the European Commission, US FDA, WHO or PIC/S.`)));
}

// ---------- definitions ----------
function viewDefinitions() {
  const out = h('div'); const q = h('input', { type: 'search', placeholder: 'Search definitions…', oninput: draw });
  function draw() {
    const s = q.value.trim().toLowerCase(); out.replaceChildren();
    for (const [reg, list] of Object.entries(DATA.definitions)) {
      const v = list.filter((d) => !s || (d.text + (d.title || '')).toLowerCase().includes(s));
      if (!v.length) continue;
      out.append(h('h2', {}, reg, ' ', h('span', { class: 'small muted' }, `(${v.length})`)),
        h('div', { class: 'panel' }, v.map((d) => h('div', { class: 'card' }, h('span', { class: 'ref' }, d.ref), d.title ? h('div', { class: 'ctitle' }, d.title) : null, h('div', { class: 'text' }, d.text)))));
    }
  }
  draw();
  $app.replaceChildren(h('h1', {}, 'Definitions'), q, out);
}

// ---------- ask (RAG) ----------
function viewAsk() {
  if (!ME.ask) {
    $app.replaceChildren(h('h1', {}, 'Ask'), h('div', { class: 'notice' }, 'Ask answers questions with exact quotes from the regulations and links to each clause. ',
      'It opens when its independent accuracy check has passed. Until then, use Search in a template or audit.'));
    return;
  }
  $app.replaceChildren(h('h1', {}, 'Ask'), h('div', { class: 'notice' }, 'Answers show the regulation text that applies. Check the clause yourself before relying on it.'), askForm());
}
// The Ask form + answer (Ask page and the inline "Ask about this" panel). Never sends by itself: the user presses the button.
function askForm(opts = {}) {
  const q = h('textarea', { placeholder: 'e.g. How often must water for injection be tested?', maxlength: 500 });
  if (opts.question) q.value = opts.question;
  const mk = new Set(opts.markets?.length ? opts.markets.filter((m) => MARKETS[m]) : ['india', 'eu', 'us']);
  const out = h('div', { class: 'askout' });
  const go = h('button', { class: 'btn pri', onclick: async () => {
    if (!q.value.trim()) { q.focus(); return; }
    go.disabled = true; out.replaceChildren(h('p', { class: 'muted' }, 'Looking up the regulations… (5–10 seconds)'));
    try { asked = q.value; showAnswer(await call('POST', '/api/ask', { question: q.value, market: [...mk] })); } catch (e) { out.replaceChildren(h('p', { class: 'err' }, e.message)); }
    go.disabled = false;
  } }, opts.send || 'Ask');
  let asked = '';
  function showAnswer(r) {
    out.replaceChildren(); let licShown = false;
    if (r.status === 'unavailable') { out.append(h('div', { class: 'notice' }, r.message || 'The answer service is not available right now. Please try again later, or use Search in a template or audit.')); return; }
    if (r.status !== 'answered') { out.append(h('div', { class: 'notice' }, r.message || 'This is not stated in the regulations in this checklist.')); return; }
    if ((r.points || []).length) out.append(h('p', { class: 'small muted' }, 'Each answer shows the whole clause. ', h('span', { class: 'term' }, 'Marked words'), ' are the words of your question, to help you find them; they are not part of the answer.'));
    for (const p of r.points || []) out.append(h('div', { class: 'point panel' }, p.intro ? h('b', {}, p.intro, ' ') : null,
      itemLink(p.item_id, p.ref), ' ', p.scope ? h('span', { class: 'badge' }, p.scope) : null, quoteBox(p.quote, p.highlights, asked, BYID.get(p.item_id))));
    if (r.not_found) out.append(h('p', {}, h('b', {}, 'Not found: '), r.not_found));
    for (const s of r.same_requirement || []) {
      const also = s.also_items || (s.also || []).map((ref) => ({ ref, item_id: null }));
      if (!also.length) continue;
      const panes = h('div', { class: 'alsotexts' }); let cite = false;
      out.append(h('div', { class: 'small alsobox' }, h('p', {}, 'Same requirement also in: ', itemLink(s.item_id, s.ref), ' → ', also.map((x, i) => {
        const t = DATA.ref_texts?.[x.ref]; if (!t && CITE_ONLY.test(x.ref)) cite = true;
        return [i ? ' · ' : '', t ? [alsoToggle(x.ref, panes), x.item_id && BYID.has(x.item_id) ? [' ', h('a', { href: '#/item/' + encodeURIComponent(x.item_id), title: 'Open the item' }, '↗')] : null] : itemLink(x.item_id, x.ref)];
      })), panes, cite && !licShown ? (licShown = true, h('div', { class: 'muted licnote' }, LIC)) : null));
    }
    if (r.comparison_note) out.append(h('p', { class: 'small muted' }, r.comparison_note));
  }
  return h('div', { class: 'askform' }, h('div', { class: 'panel' }, opts.note ? h('p', { class: 'small muted' }, opts.note) : null, q,
    h('div', { class: 'chips', style: 'margin:8px 0' }, Object.entries(MARKETS).map(([k, m]) => { const c = h('span', { class: 'chip' + (mk.has(k) ? ' on' : ''), onclick: () => { mk.has(k) ? mk.delete(k) : mk.add(k); c.classList.toggle('on'); } }, m.label); return c; })), go), out);
}
// "Ask about this" under a checklist item / audit point / other requirement (lead 2c, 20 Nov): an inline panel with a
// pre-filled, editable question built by code (askQuestionFor). Hidden when Ask is off. Nothing is sent until Send.
function askAbout(src, markets) {
  if (!ME?.ask) return null;
  const box = h('div', { class: 'askabout' }); let panel = null;
  const b = h('button', { type: 'button', class: 'btn sm', 'aria-expanded': 'false', onclick: () => {
    if (panel) { panel.remove(); panel = null; b.setAttribute('aria-expanded', 'false'); return; }
    panel = askForm({ question: askQuestionFor(src), markets, send: 'Send', note: 'Edit the question if you like, then press Send. Answers show the regulation text that applies; check the clause yourself.' });
    box.append(panel); b.setAttribute('aria-expanded', 'true'); panel.querySelector('textarea').focus();
  } }, 'Ask about this');
  box.append(b); return box;
}

// Whole clause (interface v1.2) with the answering passages marked. Long clauses fold to the marked parts +- context.
export function cleanRanges(q, hl) {
  const r = (Array.isArray(hl) ? hl : []).filter((x) => Array.isArray(x) && Number.isInteger(x[0]) && Number.isInteger(x[1]) && x[0] >= 0 && x[1] <= q.length && x[0] < x[1])
    .map((x) => [x[0], x[1]]).sort((a, b) => a[0] - b[0]);
  const out = []; for (const x of r) { const l = out[out.length - 1]; if (l && x[0] <= l[1]) l[1] = Math.max(l[1], x[1]); else out.push(x); } return out;
}
// Question words marked search-term style (neutral; no claim). Stop-words skipped; plural s/es tolerated.
const STOP = new Set(('the a an and or of to in on for by with is are be been was were must shall should may can could would will what which who whom ' +
  'whose when where why how does do did has have had this that these those it its as at from into than then there their our your any all each per not ' +
  'no yes about under over between within without need needs required require requirement requirements gmp').split(' '));
export function termRanges(text, question) {
  const words = [...new Set((question || '').toLowerCase().match(/[a-z0-9][a-z0-9-]{2,}/g) || [])].filter((w) => !STOP.has(w))
    .map((w) => (w.length > 4 && /[^s]s$/.test(w) ? w.slice(0, -1) : w));
  if (!words.length) return [];
  const re = new RegExp('\\b(' + words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')(s|es)?\\b', 'gi');
  return [...text.matchAll(re)].map((m) => [m.index, m.index + m[0].length]);
}
// Whole clause (interface v1.3: highlights normally []; quote = whole clause). Layers: highlights (if any), question
// words, editor insertions (when the quote is the item's own text). Long clauses fold ONLY around highlights.
function quoteBox(q, hl, question, item) {
  const ranges = cleanRanges(q, hl); const CTX = 220, FOLD = 900;
  const ed = item && item.text === q ? item : null;
  const layers = [{ ranges, cls: 'hl' }, { ranges: termRanges(q, question), cls: 'term' }, edLayer(ed)];
  const marked = (from, to) => paint(q, from, to, layers);
  const box = h('div', { class: 'quote' });
  const full = () => { box.replaceChildren(); add(box, marked(0, q.length), edLegend(ed)); };
  if (q.length <= FOLD || !ranges.length) { full(); return box; }
  const snapL = (i) => { if (i <= 0) return 0; const j = q.lastIndexOf(' ', i); const k = q.lastIndexOf('\n', i); return Math.max(j, k) + 1; };
  const snapR = (i) => { if (i >= q.length) return q.length; const m = q.slice(i).search(/\s/); return m < 0 ? q.length : i + m; };
  const win = []; for (const [a, b] of ranges) { const s = Math.min(a, snapL(Math.max(0, a - CTX))), e = Math.max(b, snapR(Math.min(q.length, b + CTX))); const l = win[win.length - 1]; if (l && s <= l[1]) l[1] = e; else win.push([s, e]); }
  const gap = () => h('span', { class: 'gap' }, ' … [part of the clause hidden] … ');
  const parts = []; win.forEach(([s, e], i) => { if (s > 0 || i) parts.push(gap()); parts.push(...marked(s, e)); });
  if (win[win.length - 1][1] < q.length) parts.push(gap());
  box.replaceChildren(...parts, h('div', { class: 'row', style: 'margin-top:6px' }, h('button', { class: 'btn sm', onclick: full }, 'Show the whole clause'),
    h('span', { class: 'small gap' }, 'Shortened: parts of this clause are hidden. Read the whole clause before relying on it.')));
  return box;
}

// ---------- one item card (links from Ask) ----------
function itemLink(id, ref) { return id && BYID.has(id) ? h('a', { class: 'ref', href: '#/item/' + encodeURIComponent(id) }, ref) : h('span', { class: 'ref' }, ref); }
function viewItem(id) {
  const it = BYID.get(id);
  if (!it) { $app.replaceChildren(h('p', { class: 'err' }, 'Item not found.')); return; }
  const c = h('div', { class: 'card' + (it.bg ? ' bgitem' : '') });
  add(c, cardHead(it, h('span', { class: 'badge' }, AREA_NAMES[it.area])), clauseText(it), renderTables(it), alsoLine(it), askAbout({ item: it }));
  $app.replaceChildren(h('div', { class: 'row' }, h('button', { class: 'btn sm', onclick: () => history.back() }, '← Back')), c,
    h('p', { class: 'small muted' }, 'Grey text = information (no tick boxes in an audit).'));
}

// ---------- account ----------
function viewAccount() {
  if (PLATFORM()) {
    const RIGHTS = { 'audit.view': 'See templates, audits and exports', 'audit.template.edit': 'Create, edit and delete checklist templates',
      'audit.audit.perform': 'Start audits and record answers, observations and findings', 'audit.audit.close': 'Close, re-open and delete audits' };
    $app.replaceChildren(h('h1', {}, 'Account'), h('div', { class: 'panel' }, h('p', {}, ME.name, ' · ', ME.login, ' · ', ME.company),
      h('h3', {}, 'Your rights in Medhanta CLEAR'), h('ul', {}, ME.permissions.map((c) => h('li', {}, RIGHTS[c] || c))),
      h('p', { class: 'small muted' }, 'Your login, password and rights are managed in Medhanta. Ask your administrator for changes.')));
    return;
  }
  const o = h('input', { type: 'password', autocomplete: 'current-password' }); const n = h('input', { type: 'password', autocomplete: 'new-password' });
  const m = h('div');
  $app.replaceChildren(h('h1', {}, 'Account'), h('div', { class: 'panel' }, h('p', {}, ME.name, ' · ', ME.email, ' · ', ME.company),
    h('h3', {}, 'Change password'), h('div', { class: 'row' }, h('label', { class: 'f' }, 'Old password', o), h('label', { class: 'f' }, 'New password (10+ characters)', n),
      h('button', { class: 'btn pri', onclick: async () => { try { await call('POST', '/api/password', { old: o.value, new: n.value }); m.replaceChildren(h('span', { class: 'ok' }, 'Password changed ✓')); } catch (e) { m.replaceChildren(h('span', { class: 'err' }, e.message)); } } }, 'Change')), m));
}
