// Medhanta CLEAR (Compliance Library for Evaluation and Audit Readiness; earlier "Medhanta Audit Checklist"): the HTTP app, for both installations:
//  - standalone (sale on its own): SQLite + local logins; people, rooms, equipment, products are TYPED.
//  - platform (Medhanta): PostgreSQL "audit" + sign-on through core (PL-01) with per-employee permissions from the
//    token's "permissions" claim; auditors / auditees picked from identity employee_v1, rooms / equipment / products
//    from master_data (room_v1, equipment_v1, product_v1) through report views only, write-time check (PL-08),
//    id + display values kept as at saving (PL-07). Ask (RAG) is OFF on the platform (no API key in the image).
// Regulation text is LOCKED: data/items.json is served read-only; templates/audits store ids, reasons, answers only.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import ExcelJS from 'exceljs';
import { MARKETS, AREA_NAMES, ANSWERS, GRADES, modeOf, auditLines, lineStats, answersFor, otherKey } from '../public/select.js';
import { checkPw } from './store-sqlite.js';
import { CODES, asPermissions, newVerifier, challengeOf } from './signon.js';
import { ConnectionOff, KINDS, isUuid } from './core-links.js';
import { pdfInWorker } from './pdf-worker.js';

export const PRODUCT = 'Medhanta CLEAR'; // owner 20 Nov 2026; product key stays 'audit'

export const VERSION = '0.2.0';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');

export class HttpErr extends Error { constructor(code, msg) { super(msg); this.code = code; } }
const now = () => new Date().toISOString();
const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
const str = (v, max, def = '') => (typeof v === 'string' ? v.trim().slice(0, max) : def);
const SEC = {
  'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'same-origin', 'X-Frame-Options': 'DENY',
  'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'",
};
function send(res, code, body, headers = {}) {
  const b = typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body);
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...SEC, ...headers });
  res.end(b);
}
const htmlPage = (title, text, link = true) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · Medhanta CLEAR</title><style>body{font-family:system-ui,sans-serif;max-width:32rem;margin:4rem auto;padding:0 1rem;color:#333}a{color:#e8500f}</style></head>
<body><h1>${title}</h1><p>${text}</p>${link ? '<p><a href="/login">Sign in again</a></p>' : ''}</body></html>`;
function readRaw(req, limit) {
  return new Promise((ok, bad) => {
    let n = 0; const parts = [];
    req.on('data', (c) => { n += c.length; if (n > limit) { bad(new HttpErr(413, 'Too large')); req.destroy(); } else parts.push(c); });
    req.on('end', () => ok(Buffer.concat(parts).toString('utf8')));
    req.on('error', bad);
  });
}
async function readBody(req, limit = 2_000_000) {
  const s = await readRaw(req, limit);
  try { return s ? JSON.parse(s) : {}; } catch { throw new HttpErr(400, 'Bad JSON'); }
}
function cookies(req) {
  const o = {};
  for (const p of (req.headers.cookie || '').split(';')) { const i = p.indexOf('='); if (i > 0) o[p.slice(0, i).trim()] = p.slice(i + 1).trim(); }
  return o;
}

/**
 * deps: { store, mode: 'standalone'|'platform', signOn (platform), links (coreLinks or null), siteName, cookieSecure,
 *         dataFile, askFlag, askCmd, askLog, idleMinutes, checkMinutes }
 */
export function createApp(deps) {
  const { store, signOn = null } = deps;
  const PLATFORM = deps.mode === 'platform';
  const links = deps.links || null;
  const IDLE = deps.idleMinutes ?? 15, CHECK = deps.checkMinutes ?? 5, LOCAL_DAYS = 14;
  const askFlag = deps.askFlag || path.join(ROOT, 'ask-enabled');
  const askOn = () => !PLATFORM && fs.existsSync(askFlag);
  const ASK_PER_HOUR = 30; const askTimes = new Map();
  const secureFlag = (req) => (PLATFORM ? deps.cookieSecure !== false : req.headers['x-forwarded-proto'] === 'https') ? '; Secure' : '';

  // ---------- data ----------
  const DATA_FILE = deps.dataFile || path.join(ROOT, 'data', 'items.json');
  const DATA_RAW = fs.readFileSync(DATA_FILE);
  const DATA = JSON.parse(DATA_RAW);
  const DATA_GZ = zlib.gzipSync(DATA_RAW, { level: 9 });
  const DATA_ETAG = '"' + DATA.version + '"';
  const ITEM = new Map(DATA.items.map((x) => [x.id, x]));
  const POINT = new Map((DATA.points || []).map((x) => ['P:' + x.id, x]));
  const OTHER = new Map((DATA.other_requirements || []).map((x) => [otherKey(x), x]));
  const PLANTS = new Set(Object.keys(DATA.plant_types));
  const AUDS = new Set(DATA.audiences);

  // ---------- sessions ----------
  async function user(req, touch = true) {
    const t = cookies(req).mac_s;
    if (!t || t.length > 100) return null;
    const key = sha(t);
    if (!PLATFORM) {
      const u = await store.loadLocalSession(key);
      return u && { ...u, login: u.email, permissions: CODES };
    }
    // Permissions older than CHECK minutes are renewed from core first; if core refuses, the session ends (PL-01).
    const due = await store.claimRenewal(key, CHECK, IDLE);
    if (due) {
      try {
        const id = await signOn.refresh(due.refreshToken ?? '');
        await store.renewSession(key, { permissions: asPermissions(id.permissions), refreshToken: id.refreshToken, idToken: id.idToken });
      } catch { await store.deleteSession(key); return null; }
    }
    const u = await store.loadSession(key, IDLE, touch);
    if (!u || !u.permissions.length) { if (u) await store.deleteSession(key); return null; }
    return { ...u, company: deps.siteName || u.company, email: u.login };
  }
  const need = (u, ...codes) => { if (!codes.some((c) => u.permissions.includes(c))) throw new HttpErr(403, 'You do not have the right for this.'); };
  const READ = CODES; // any Audit Checklist permission may read

  // ---------- template / audit validation (regulation text never stored) ----------
  function cleanConfig(c) {
    if (!c || typeof c !== 'object') throw new HttpErr(400, 'config missing');
    const markets = (Array.isArray(c.markets) ? c.markets : []).filter((m) => m in MARKETS);
    if (!markets.length) throw new HttpErr(400, 'Choose at least one market');
    const plants = (Array.isArray(c.plants) ? c.plants : []).filter((p) => PLANTS.has(p) && p !== 'all');
    const audiences = (Array.isArray(c.audiences) ? c.audiences : []).filter((a) => AUDS.has(a));
    if (!audiences.includes('manufacturer')) audiences.unshift('manufacturer');
    const mode = c.mode === 'points' ? 'points' : 'clauses';
    if (mode === 'points' && !POINT.size) throw new HttpErr(400, 'Audit points are not available yet');
    const removed = {};
    for (const [id, why] of Object.entries(c.removed || {})) {
      const what = ITEM.get(id) || POINT.get(id) || (OTHER.has(id) && ITEM.get(OTHER.get(id).item));
      if (!what) continue;
      const r = str(why, 500);
      if (!r) throw new HttpErr(400, `A reason is required to remove ${what.ref || what.question.slice(0, 60)}`);
      removed[id] = r;
    }
    const company_items = [];
    for (const ci of Array.isArray(c.company_items) ? c.company_items.slice(0, 2000) : []) {
      const text = str(ci.text, 4000);
      if (!text) continue;
      const area = DATA.areas.includes(ci.area) ? ci.area : 'QS';
      const cid = /^[a-z0-9]{6,20}$/.test(ci.cid || '') ? ci.cid : crypto.randomBytes(5).toString('hex');
      company_items.push({ cid, area, title: str(ci.title, 200), ref: str(ci.ref, 80), text });
    }
    return { mode, markets, plants, audiences, removed, company_items };
  }

  // ---------- picked references: people, rooms, equipment, products ----------
  // jobs: [{ kind, v (as sent), old: [stored entries at this place] }] -> cleaned entries (null = dropped).
  // Linked (platform, link URL set): an entry must carry an id from core; an id already stored at this place keeps its
  // stored values (as at saving, PL-07); a NEW id is read through the view and refused if unknown or inactive (PL-08).
  // Not linked (standalone): typed names. Entries typed before a link was switched on stay as they were.
  async function resolveRefs(jobs) {
    const out = new Array(jobs.length).fill(null); const pending = {};
    jobs.forEach((j, i) => {
      const v = j.v && typeof j.v === 'object' ? j.v : {};
      const k = KINDS[j.kind];
      if (v.id != null && v.id !== '') {
        if (!isUuid(v.id)) throw new HttpErr(400, `Unknown ${k.label}.`);
        const prev = j.old.find((o) => o.id === v.id);
        if (prev) { out[i] = prev; return; }
        if (links?.linked(j.kind)) { (pending[j.kind] ||= []).push(i); return; }
      }
      const name = str(v.name, 200);
      if (!name) return;
      if (links?.linked(j.kind) && !j.old.some((o) => !o.id && o.name === name)) throw new HttpErr(400, `Pick the ${k.label} from the list (from ${k.provider}).`);
      out[i] = { name };
    });
    for (const [kind, idx] of Object.entries(pending)) {
      const rows = new Map((await links.byIds(kind, [...new Set(idx.map((i) => jobs[i].v.id))])).map((r) => [r.id, r]));
      for (const i of idx) {
        const r = rows.get(jobs[i].v.id);
        if (!r || !r.active) throw new HttpErr(400, `No such active ${KINDS[kind].label}: ${str(jobs[i].v.name, 100) || jobs[i].v.id}`);
        const { active, ...keep } = r; out[i] = keep;
      }
    }
    return out;
  }
  const HEADER = { auditors: 'employee', auditees: 'employee', rooms: 'room' };
  const LINK_KINDS = ['room', 'equipment', 'product'];
  async function cleanHeader(h, old) {
    const jobs = [];
    for (const [f, kind] of Object.entries(HEADER)) for (const v of (Array.isArray(h?.[f]) ? h[f] : []).slice(0, 50)) jobs.push({ f, kind, v, old: old?.[f] || [] });
    const r = await resolveRefs(jobs); const out = { auditors: [], auditees: [], rooms: [] };
    jobs.forEach((j, i) => { if (r[i] && !out[j.f].some((x) => x.id ? x.id === r[i].id : !x.id && x.name === r[i].name)) out[j.f].push(r[i]); });
    return out;
  }
  // Only keys of this audit's lines survive; answers from the mode's set; grade only on a "not compliant" point;
  // links: the rooms / equipment / products a finding names.
  async function cleanAnswers(a, cfg, old) {
    const out = {}; const mode = modeOf(cfg); const jobs = [];
    const kinds = new Map(auditLines(DATA, cfg).map((l) => [l.key, l.kind]));
    for (const [k, v] of Object.entries(a || {})) {
      if (!v || typeof v !== 'object' || !kinds.has(k)) continue;
      const A = answersFor(kinds.get(k), mode);
      const ans = A.set.includes(v.a) ? v.a : '';
      const note = str(v.note, 4000);
      const grade = A === ANSWERS.points && ans === A.neg && GRADES.includes(v.grade) ? v.grade : '';
      for (const l of (Array.isArray(v.links) ? v.links : []).slice(0, 20)) {
        if (LINK_KINDS.includes(l?.kind)) jobs.push({ k, kind: l.kind, v: l, old: (old?.[k]?.links || []).filter((o) => o.kind === l.kind).map(({ kind, ...x }) => x) });
      }
      if (ans || note) out[k] = { ...(ans ? { a: ans } : {}), ...(note ? { note } : {}), ...(grade ? { grade } : {}) };
    }
    const r = await resolveRefs(jobs);
    jobs.forEach((j, i) => {
      if (!r[i]) return;
      const L = ((out[j.k] ||= {}).links ||= []);
      if (!L.some((x) => x.kind === j.kind && (x.id ? x.id === r[i].id : !x.id && x.name === r[i].name))) L.push({ kind: j.kind, ...r[i] });
    });
    return out;
  }
  const names = (l) => (l || []).map((x) => x.name).join(', ');
  function changes(a, b) {
    const d = {};
    for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
      if (JSON.stringify(a[k]) !== JSON.stringify(b[k])) d[k] = { from: a[k] ?? null, to: b[k] ?? null };
      if (Object.keys(d).length >= 200) break;
    }
    return d;
  }

  // ---------- routes ----------
  const loginTries = new Map();
  async function api(req, res, url) {
    const p = url.pathname; const m = req.method;
    if (p === '/api/health' && m === 'GET') {
      try { await store.health(); return send(res, 200, { status: 'ok', version: VERSION, mode: deps.mode, db: 'ok' }); }
      catch { return send(res, 503, { status: 'error', version: VERSION, db: 'unreachable' }); }
    }
    if (m !== 'GET' && req.headers['x-requested-with'] !== 'mac') throw new HttpErr(403, 'Bad request origin');

    if (p === '/api/login' && m === 'POST') {
      if (PLATFORM) throw new HttpErr(404, 'Sign in through Medhanta: /login');
      const ip = req.headers['x-forwarded-for']?.split(',')[0].trim() || req.socket.remoteAddress;
      const t = loginTries.get(ip) || []; const recent = t.filter((x) => x > Date.now() - 15 * 60e3);
      if (recent.length >= 10) throw new HttpErr(429, 'Too many tries. Wait 15 minutes.');
      const b = await readBody(req, 10_000);
      const u = await store.userByEmail(str(b.email, 200).toLowerCase());
      const ok = checkPw(str(b.password, 200), u ? u.pw : DUMMY_HASH) && !!u;
      if (!ok) { recent.push(Date.now()); loginTries.set(ip, recent); throw new HttpErr(401, 'Wrong e-mail or password'); }
      const tok = crypto.randomBytes(32).toString('base64url');
      await store.createLocalSession(sha(tok), u.id, Date.now() + LOCAL_DAYS * 864e5);
      return send(res, 200, { ok: true }, { 'Set-Cookie': `mac_s=${tok}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${LOCAL_DAYS * 86400}${secureFlag(req)}` });
    }
    if (p === '/api/logout' && m === 'POST') {
      const t = cookies(req).mac_s; let logoutUrl = null;
      if (t && t.length <= 100) {
        const s = await store.deleteSession(sha(t));
        if (PLATFORM) { logoutUrl = signOn.logoutUrl(s?.idToken ?? null); if (s) await store.trail({ id: s.userId, name: '' }, 'logout', 'user', s.userId); }
      }
      return send(res, 200, { ok: true, logoutUrl }, { 'Set-Cookie': `mac_s=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0${secureFlag(req)}` });
    }
    const u = await user(req);
    if (!u) throw new HttpErr(401, 'Please log in');
    if (p === '/api/me') {
      return send(res, 200, { email: u.email, login: u.login, name: u.name, company: u.company, ask: askOn(), data_version: DATA.version,
        mode: deps.mode, permissions: u.permissions, links: links ? links.status() : { identity: false, master_data: false } });
    }
    if (p === '/api/password' && m === 'POST') {
      if (PLATFORM) throw new HttpErr(404, 'Passwords are managed in Medhanta.');
      const b = await readBody(req, 10_000);
      if (!checkPw(str(b.old, 200), await store.userPw(u.id))) throw new HttpErr(400, 'Old password is wrong');
      if (str(b.new, 200).length < 10) throw new HttpErr(400, 'New password: at least 10 characters');
      await store.setPw(u.id, str(b.new, 200));
      return send(res, 200, { ok: true });
    }

    // pickers (platform, link on): read live through the views; "connection off" when cut
    let mm = p.match(/^\/api\/pick\/(employee|room|equipment|product)$/);
    if (mm && m === 'GET') {
      need(u, ...READ);
      if (!links?.linked(mm[1])) throw new HttpErr(404, 'Not linked: type the name.');
      return send(res, 200, await links.search(mm[1], str(url.searchParams.get('q') || '', 60)));
    }

    // templates
    if (p === '/api/templates' && m === 'GET') { need(u, ...READ); return send(res, 200, await store.listTemplates(u.company_id)); }
    if (p === '/api/templates' && m === 'POST') {
      need(u, 'audit.template.edit');
      const b = await readBody(req); const cfg = cleanConfig(b.config); const name = str(b.name, 200) || 'Untitled template';
      const id = await store.createTemplate(u.company_id, { name, config: cfg, data_version: DATA.version, by: u.email });
      await store.trail(u, 'template.create', 'template', id, { name });
      return send(res, 200, { id });
    }
    mm = p.match(/^\/api\/templates\/(\d+)$/);
    if (mm) {
      need(u, ...READ);
      const t = await store.getTemplate(u.company_id, +mm[1]);
      if (!t) throw new HttpErr(404, 'Template not found');
      if (m === 'GET') return send(res, 200, t);
      need(u, 'audit.template.edit');
      if (m === 'PUT') {
        const b = await readBody(req); const cfg = cleanConfig(b.config); const name = str(b.name, 200) || t.name;
        await store.updateTemplate(t.id, { name, config: cfg, data_version: DATA.version, by: u.email });
        await store.trail(u, 'template.update', 'template', t.id, { name, removed: Object.keys(cfg.removed).length, company_items: cfg.company_items.length });
        return send(res, 200, { ok: true });
      }
      if (m === 'DELETE') { await store.deleteTemplate(t.id); await store.trail(u, 'template.delete', 'template', t.id, { name: t.name }); return send(res, 200, { ok: true }); }
    }

    // audits
    if (p === '/api/audits' && m === 'GET') {
      need(u, ...READ);
      const rows = await store.listAudits(u.company_id);
      return send(res, 200, rows.map((r) => { const { config, answers, ...rest } = r; return { ...rest, ...stats(config, answers), mode: modeOf(config) }; }));
    }
    if (p === '/api/audits' && m === 'POST') {
      need(u, 'audit.audit.perform');
      const b = await readBody(req);
      const t = await store.getTemplate(u.company_id, +b.template_id);
      if (!t) throw new HttpErr(404, 'Template not found');
      const header = await cleanHeader(b.header || (PLATFORM ? {} : { auditors: b.auditor ? [{ name: b.auditor }] : [] }), {});
      const id = await store.createAudit(u.company_id, { template_id: t.id, template_name: t.name, name: str(b.name, 200) || t.name + ' audit',
        site: PLATFORM ? (deps.siteName || u.company) : str(b.site, 200), auditor: names(header.auditors) || (PLATFORM ? '' : str(b.auditor, 200)),
        audit_date: str(b.audit_date, 20), header, config: t.config, data_version: DATA.version, by: u.email });
      await store.trail(u, 'audit.create', 'audit', id, { template: t.name });
      return send(res, 200, { id });
    }
    mm = p.match(/^\/api\/audits\/(\d+)(\/export\.(?:xlsx|pdf))?$/);
    if (mm) {
      need(u, ...READ);
      const a = await store.getAudit(u.company_id, +mm[1]);
      if (!a) throw new HttpErr(404, 'Audit not found');
      const cfg = a.config;
      if (mm[2] === '/export.pdf' && m === 'GET') {
        let buf;
        try { buf = await pdfInWorker(DATA_FILE, a, { printedBy: u.email, product: PRODUCT }); }
        catch (e) { if (e.busy) throw new HttpErr(429, e.message); throw e; }
        const fname = (a.name || 'audit').replace(/[^A-Za-z0-9 _.-]/g, '').slice(0, 60) || 'audit';
        res.writeHead(200, { ...SEC, 'Content-Type': 'application/pdf', 'Content-Disposition': `attachment; filename="${fname}.pdf"`, 'Cache-Control': 'no-store' });
        return res.end(buf);
      }
      if (mm[2] && m === 'GET') return exportXlsx(res, a, cfg, a.answers, u);
      if (m === 'GET') return send(res, 200, a);
      if (m === 'PUT') {
        if (a.status === 'withdrawn') throw new HttpErr(409, 'This audit was withdrawn. It is kept as it was and cannot be changed.');
        const b = await readBody(req);
        const status = ['open', 'closed'].includes(b.status) ? b.status : a.status;
        if (status !== a.status) need(u, 'audit.audit.close');
        const perform = u.permissions.includes('audit.audit.perform');
        if (!perform && status === a.status) throw new HttpErr(403, 'You do not have the right for this.');
        if (a.status === 'closed' && status !== 'open') throw new HttpErr(409, 'This audit is closed. Re-open it to change answers.');
        // Without audit.audit.perform only the status changes (close / re-open).
        const answers = perform && b.answers ? await cleanAnswers(b.answers, cfg, a.answers) : a.answers;
        const header = perform && b.header ? await cleanHeader(b.header, a.header) : a.header;
        const next = {
          name: (perform && str(b.name, 200)) || a.name,
          site: PLATFORM ? a.site : perform && b.site !== undefined ? str(b.site, 200) : a.site,
          auditor: perform && b.header ? names(header.auditors) || (PLATFORM ? '' : str(b.auditor, 200)) : perform && !PLATFORM && b.auditor !== undefined ? str(b.auditor, 200) : a.auditor,
          audit_date: perform && b.audit_date !== undefined ? str(b.audit_date, 20) : a.audit_date,
          status, header, answers, by: u.email,
        };
        const updated = await store.updateAudit(a.id, next);
        const diff = changes(a.answers, answers);
        if (status !== a.status) await store.trail(u, status === 'closed' ? 'audit.close' : 'audit.reopen', 'audit', a.id);
        if (Object.keys(diff).length) await store.trail(u, 'audit.answers', 'audit', a.id, diff);
        if (JSON.stringify(header) !== JSON.stringify(a.header) || next.name !== a.name || next.audit_date !== a.audit_date || next.site !== a.site)
          await store.trail(u, 'audit.header', 'audit', a.id, { name: next.name, site: next.site, audit_date: next.audit_date, header });
        return send(res, 200, { ok: true, updated, header, answers });
      }
      // MED-11 (PL-06): an audit is never deleted. An open one is withdrawn with a reason and kept; a closed one stays.
      if (m === 'DELETE') {
        need(u, 'audit.audit.close');
        const reason = str((await readBody(req)).reason, 500);
        if (!reason) throw new HttpErr(400, 'Give the reason for withdrawing this audit.');
        if (a.status !== 'open') throw new HttpErr(409, a.status === 'closed' ? 'This audit is closed. A closed audit cannot be withdrawn.' : 'This audit was already withdrawn.');
        if (!(await store.withdrawAudit(a.id, { reason, by: u.email }))) throw new HttpErr(409, 'This audit is no longer open. Reload the page.');
        await store.trail(u, 'audit.withdraw', 'audit', a.id, { name: a.name, reason });
        return send(res, 200, { ok: true });
      }
    }

    // Ask (RAG): standalone only, and only while the flag file exists. Never on the platform.
    if (p === '/api/ask' && m === 'POST') {
      need(u, ...READ);
      if (!askOn()) return send(res, 200, { v: 1, status: 'unavailable', message: 'Ask is not switched on yet. It opens when its accuracy check has passed.' });
      const b = await readBody(req, 20_000);
      const q = str(b.question, 500);
      if (q.length < 3) throw new HttpErr(400, 'Question too short');
      const t = (askTimes.get(u.id) || []).filter((x) => x > Date.now() - 3600e3);
      if (t.length >= ASK_PER_HOUR) throw new HttpErr(429, `Limit reached: ${ASK_PER_HOUR} questions per hour. Please try later.`);
      t.push(Date.now()); askTimes.set(u.id, t);
      const r = await ask({ question: q, market: (b.market || []).filter((x) => x in MARKETS), plants: b.plants, audience: b.audience });
      // cost log: no question or answer text; only who/when/how much
      fs.appendFile(deps.askLog, JSON.stringify({ t: now(), company: u.company_id, user: u.id, status: r.status, points: (r.points || []).length,
        seconds: r.meta?.seconds ?? null, cost_usd: r.meta?.cost_usd ?? null, model: r.meta?.model ?? null, q_len: q.length }) + '\n', () => {});
      return send(res, 200, r);
    }
    throw new HttpErr(404, 'Not found');
  }
  const DUMMY_HASH = 'scrypt$16384$8$1$' + crypto.randomBytes(16).toString('base64') + '$' + crypto.randomBytes(64).toString('base64');

  function ask(payload) {
    return new Promise((ok) => {
      const ch = spawn('python3', ['-I', deps.askCmd || path.join(ROOT, 'rag', 'api.py')], { stdio: ['pipe', 'pipe', 'ignore'] });
      let out = ''; const timer = setTimeout(() => ch.kill(), 60_000);
      ch.stdout.on('data', (d) => { out += d; });
      ch.on('close', () => { clearTimeout(timer); try { ok(JSON.parse(out)); } catch { ok({ v: 1, status: 'unavailable', message: 'The answer service is not available. Please try again later.' }); } });
      ch.stdin.end(JSON.stringify(payload));
    });
  }

  // ---------- sign-on through core (platform) ----------
  const PENDING = 'mac_signon';
  async function signon(req, res, url) {
    const p = url.pathname;
    if (p === '/login' && req.method === 'GET') {
      const state = newVerifier(); const verifier = newVerifier();
      // Lax: the cookie must come back on core's top-level redirect to /cb. Only this browser's state is accepted.
      res.writeHead(302, { ...SEC, Location: signOn.authUrl({ state, challenge: challengeOf(verifier) }), 'Cache-Control': 'no-store',
        'Set-Cookie': `${PENDING}=${state}.${verifier}; HttpOnly; SameSite=Lax; Path=/cb; Max-Age=600${secureFlag(req)}` });
      return res.end();
    }
    if (p === '/cb' && req.method === 'GET') {
      const page = (code, title, text) => { res.writeHead(code, { ...SEC, 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Set-Cookie': clear }); res.end(htmlPage(title, text)); };
      const clear = `${PENDING}=; HttpOnly; SameSite=Lax; Path=/cb; Max-Age=0${secureFlag(req)}`;
      const [state, verifier] = (cookies(req)[PENDING] || '').split('.');
      const code = url.searchParams.get('code'); const qs = url.searchParams.get('state');
      if (!code || !state || !verifier || qs !== state) return page(400, 'Sign-in expired', 'This sign-in link is no longer valid.');
      let who;
      try { who = await signOn.exchange(code, verifier); } catch { return page(401, 'Sign-in failed', 'The sign-in service did not confirm who you are.'); }
      const permissions = asPermissions(who.permissions);
      const name = (who.name || '').trim() || who.login;
      const { id } = await store.upsertEmployee({ sub: who.sub, login: who.login || who.sub, name });
      if (!permissions.length) {
        await store.trail({ id, name }, 'login.refused', 'user', id, { reason: 'no audit.* permission' });
        return page(403, 'No access', `You have no right to use ${PRODUCT}. Ask your administrator.`);
      }
      const tok = crypto.randomBytes(32).toString('base64url');
      await store.createSession(sha(tok), id, { permissions, refreshToken: who.refreshToken, idToken: who.idToken });
      await store.trail({ id, name }, 'login', 'user', id, { permissions });
      res.writeHead(302, { ...SEC, Location: '/', 'Cache-Control': 'no-store',
        'Set-Cookie': [clear, `mac_s=${tok}; HttpOnly; SameSite=Lax; Path=/${secureFlag(req)}`] });
      return res.end();
    }
    // OIDC Back-Channel Logout 1.0: core posts a signed logout token when the person signs out there; every session
    // of that person ends at once (shared terminals, PL-01).
    if (p === '/backchannel-logout' && req.method === 'POST') {
      const token = new URLSearchParams(await readRaw(req, 20_000)).get('logout_token');
      let who;
      try { if (!token) throw new Error('no token'); who = await signOn.verifyLogoutToken(token); }
      catch { return send(res, 400, { error: 'invalid_request' }); }
      const n = await store.deleteSessionsOf(who.sub);
      if (n) await store.trail(null, 'logout.backchannel', 'user', null, { sub: who.sub, sessions: n });
      return send(res, 200, { ok: true });
    }
    return false;
  }

  // ---------- audit stats + Excel export ----------
  const stats = (cfg, answers) => lineStats(auditLines(DATA, cfg), answers);
  const BETA = 'Beta – independently checked, not yet expert-certified';
  const NEGS = new Set(['No', 'Not compliant']), POSS = new Set(['Yes', 'Compliant']);
  const evidenceText = (ev) => [].concat(ev || []).map((e) => (typeof e === 'string' ? e : (e.type ? e.type + ': ' : '') + e.what)).join('; ');
  const refsOfPoint = (p) => [...new Set(p.clauses.map((c) => ITEM.get(c.item)?.ref).filter(Boolean))];
  const linkText = (L) => (L || []).map((x) => `${x.kind}: ${x.code ? x.code + ' ' : ''}${x.name}`).join('; ');
  async function exportXlsx(res, a, cfg, answers, u) {
    const wb = new ExcelJS.Workbook(); wb.creator = PRODUCT; wb.created = new Date();
    const lines = auditLines(DATA, cfg); const mode = modeOf(cfg); const st = lineStats(lines, answers); const A = ANSWERS[mode];
    const hd = a.header || {};
    const s0 = wb.addWorksheet('Summary');
    s0.columns = [{ width: 28 }, { width: 70 }];
    const info = [[PRODUCT, ''], ['Audit', a.name], ['Site', a.site || ''], ['Auditor', a.auditor || ''],
      ['Auditees', names(hd.auditees)], ['Rooms / areas', (hd.rooms || []).map((r) => (r.code ? r.code + ' ' : '') + r.name).join(', ')], ['Audit date', a.audit_date || ''],
      ['Template', a.template_name], ['Status', a.status], ['Markets', cfg.markets.map((x) => MARKETS[x].label).join(', ')],
      ['Plant types', ['all (general GMP)', ...cfg.plants].join(', ')], ['Audiences', cfg.audiences.join(', ')],
      ['Checklist style', mode === 'points' ? 'Audit points' + (DATA.points_status === 'beta' ? ' (' + BETA + ')' : '') : 'Regulation clauses'],
      [mode === 'points' ? 'Audit points' : 'Check points', st.total], [mode === 'points' ? 'Compliant / Yes' : 'Yes', st.yes], [mode === 'points' ? 'Not compliant / No' : 'No', st.no], ['N/A', st.na], ['Not answered', st.total - st.yes - st.no - st.na],
      ['Exported', `${now()} by ${u.email}`], ['Data version', a.data_version],
      ['Note', 'Not affiliated with or endorsed by CDSCO, the European Commission, US FDA, WHO or PIC/S. WHO and PIC/S are cited by clause number only (text not reproduced, licence).']];
    for (const r of info) s0.addRow(r);
    s0.getRow(1).font = { bold: true, size: 14, color: { argb: 'FFE8500F' } };
    s0.getColumn(1).font = { bold: true };
    const ws = wb.addWorksheet(mode === 'points' ? 'Audit points' : 'Check points', { views: [{ state: 'frozen', ySplit: 1 }] });
    const cols = [{ header: 'Area', key: 'area', width: 22 }, { header: 'Regulation', key: 'reg', width: 12 }, { header: 'Reference', key: 'ref', width: 24 },
      { header: 'Also (same requirement)', key: 'also', width: 28 }, { header: 'Also (text)', key: 'alsot', width: 60 }];
    if (mode === 'points') cols.push({ header: 'Audit point', key: 'text', width: 60 }, { header: 'What to verify', key: 'verify', width: 40 }, { header: 'Evidence', key: 'evidence', width: 30 });
    else cols.push({ header: 'Check point (regulation text)', key: 'text', width: 80 });
    cols.push({ header: 'Answer', key: 'ans', width: 14 });
    if (mode === 'points') cols.push({ header: 'Grade', key: 'grade', width: 10 });
    cols.push({ header: A.note, key: 'note', width: 40 }, { header: 'Rooms / equipment / products', key: 'links', width: 30 });
    ws.columns = cols;
    if (mode === 'points' && DATA.points_status === 'beta') { ws.headerFooter.oddHeader = '&L' + BETA; s0.getCell('B1').value = 'Audit points: ' + BETA; s0.getCell('B1').font = { bold: true, color: { argb: 'FF8A5A00' } }; }
    ws.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
    ws.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE8500F' } };
    for (const l of lines) {
      const area = AREA_NAMES[l.area] || l.area; const v = answers[l.key] || {};
      let row;
      if (l.kind === 'company') row = { area, reg: 'Company item', ref: l.company.ref || '', also: '', text: (l.company.title ? l.company.title + ': ' : '') + l.text };
      else if (l.kind === 'other') row = { area, reg: l.item.reg, ref: l.item.ref + (l.item.u.filter((x) => x[3]).length > 1 ? ` (${l.n})` : ''), also: (l.other.refs || []).join(' · '),
        text: 'Other requirement (check the clause): ' + l.text, verify: '', evidence: '' };
      else if (l.kind === 'unit') row = { area, reg: l.item.reg, ref: l.item.ref + (l.item.u.filter((x) => x[3]).length > 1 ? ` (${l.n})` : ''), also: (l.item.refs || []).join(' · '), text: l.text };
      else {
        const its = l.point.clauses.map((c) => ITEM.get(c.item)).filter(Boolean);
        row = { area, reg: [...new Set(its.map((x) => x.reg))].join(', '), ref: refsOfPoint(l.point).join('; '), also: (l.point.refs || []).join(' · '),
          text: (l.point.modality === 'should' ? '(Recommended) ' : '') + l.point.question, verify: l.point.verify || '', evidence: evidenceText(l.point.evidence) };
      }
      // "Also (text)": full clause text of SHOWN-regulator refs only (EU / US FDA / Schedule M); WHO / PIC/S never (licence)
      const own = l.kind === 'unit' ? l.item.refs : l.kind === 'other' ? l.other.refs : l.kind === 'point' ? l.point.refs : null;
      const alsot = (own || []).filter((r) => DATA.ref_texts?.[r]).map((r) => r + ': ' + DATA.ref_texts[r]).join('\n\n');
      const x = ws.addRow({ ...row, alsot, ans: v.a || '', grade: v.grade || '', note: v.note || '', links: linkText(v.links) });
      x.alignment = { vertical: 'top', wrapText: true };
      const c = x.getCell('ans');
      if (NEGS.has(v.a)) c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFDEBE9' } };
      if (POSS.has(v.a)) c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE4F5EA' } };
    }
    ws.autoFilter = { from: { row: 1, column: 1 }, to: { row: 1, column: cols.length } };
    const rem = Object.entries(cfg.removed);
    if (rem.length) {
      const w2 = wb.addWorksheet('Removed items');
      w2.columns = [{ header: 'Reference', key: 'ref', width: 28 }, { header: 'Reason (customer)', key: 'why', width: 80 }];
      w2.getRow(1).font = { bold: true };
      for (const [id, why] of rem) w2.addRow({ ref: ITEM.get(id)?.ref || (POINT.get(id) ? 'Audit point: ' + POINT.get(id).question : OTHER.get(id) ? 'Other requirement: ' + (ITEM.get(OTHER.get(id).item)?.ref || '') : id), why });
    }
    const buf = Buffer.from(await wb.xlsx.writeBuffer());
    const fname = (a.name || 'audit').replace(/[^A-Za-z0-9 _.-]/g, '').slice(0, 60) || 'audit';
    res.writeHead(200, { ...SEC, 'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'Content-Disposition': `attachment; filename="${fname}.xlsx"`, 'Cache-Control': 'no-store' });
    res.end(buf);
  }

  // ---------- static ----------
  const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json' };
  async function serveStatic(req, res, url) {
    if (url.pathname === '/data/items.json') {
      // Platform: the library is for signed-in people only.
      if (PLATFORM && !(await user(req, false))) throw new HttpErr(401, 'Please log in');
      if (req.headers['if-none-match'] === DATA_ETAG) { res.writeHead(304, SEC); return res.end(); }
      const gz = /\bgzip\b/.test(req.headers['accept-encoding'] || '');
      res.writeHead(200, { ...SEC, 'Content-Type': 'application/json', ETag: DATA_ETAG, 'Cache-Control': 'no-cache', ...(gz ? { 'Content-Encoding': 'gzip' } : {}) });
      return res.end(gz ? DATA_GZ : DATA_RAW);
    }
    const rel = url.pathname === '/' ? '/index.html' : url.pathname;
    const base = rel.startsWith('/brand/') ? ROOT : path.join(ROOT, 'public');
    const f = path.normalize(path.join(base, rel));
    if (!f.startsWith(base + path.sep) || (base === ROOT && !f.startsWith(path.join(ROOT, 'brand') + path.sep)) || !fs.existsSync(f) || !fs.statSync(f).isFile()) {
      return serveFile(res, path.join(ROOT, 'public', 'index.html'));
    }
    return serveFile(res, f);
  }
  function serveFile(res, f) {
    const b = fs.readFileSync(f);
    res.writeHead(200, { ...SEC, 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(b);
  }

  const handler = async (req, res) => {
    // `//host/path` would be read as a host by the URL parser, hiding the real path: refuse it.
    if (/^[\\/]{2}/.test(req.url)) return send(res, 404, { error: 'Not found' });
    const url = new URL(req.url, 'http://x');
    try {
      if (url.pathname.startsWith('/api/')) return await api(req, res, url);
      // Pen test PH-01: an encoded or odd-cased spelling of an API path (/%61pi/..., /API/..., //api/...) is never served, not even as a page.
      let decoded = url.pathname; try { decoded = decodeURIComponent(decoded); } catch { throw new HttpErr(400, 'Bad path'); }
      if (/^[\\/]+api([\\/]|$)/i.test(decoded)) throw new HttpErr(404, 'Not found');
      if (PLATFORM && ['/login', '/cb', '/backchannel-logout'].includes(url.pathname)) { if ((await signon(req, res, url)) !== false) return; }
      if (req.method !== 'GET' && req.method !== 'HEAD') throw new HttpErr(405, 'Method not allowed');
      return await serveStatic(req, res, url);
    } catch (e) {
      if (e instanceof ConnectionOff) return send(res, 503, { error: e.message, connection_off: true });
      if (!(e instanceof HttpErr)) console.error(e);
      if (!res.headersSent) send(res, e instanceof HttpErr ? e.code : 500, { error: e instanceof HttpErr ? e.message : 'Server error' });
    }
  };
  return { handler, DATA };
}
