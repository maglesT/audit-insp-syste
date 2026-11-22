// Platform tests, named by rule ID (run by scripts/test-platform.sh: throwaway postgres:17 set up like the platform's
// init.sh; identity / master_data stand-ins with core's report view columns; a stand-in core OIDC provider over HTTP).
import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import postgres from 'postgres';
import { migrate } from '../../db/migrate.js';

const SU = process.env.PGTEST_SU, APP = process.env.PGTEST_APP;
if (!SU || !APP) throw new Error('run scripts/test-platform.sh');
const su = (db) => postgres(`${SU}/${db}`, { max: 1, onnotice: () => {} });
const appDb = (db) => postgres(`${APP}/${db}`, { max: 1, onnotice: () => {} });
const sqlstate = async (q) => { try { await q; return 'ok'; } catch (e) { return e.code; } };
const listen = (srv) => new Promise((r) => srv.listen(0, '127.0.0.1', () => r(`http://127.0.0.1:${srv.address().port}`)));

// ---------- stand-in core: OIDC code flow + PKCE, /me with the permissions claim, refresh, JWKS, session end ----------
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', { modulusLength: 2048 });
const jwk = { ...publicKey.export({ format: 'jwk' }), kid: 'k1', use: 'sig', alg: 'RS256' };
const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
const jwt = (payload, key = privateKey, kid = 'k1') => {
  const h = b64({ alg: 'RS256', kid, typ: 'JWT' }), p = b64(payload);
  return `${h}.${p}.${crypto.sign('sha256', Buffer.from(`${h}.${p}`), key).toString('base64url')}`;
};
const core = { people: new Map(), current: null, codes: new Map(), tokens: new Map(), refresh: new Map(), secret: 's3cret', redirect: '' };
const coreSrv = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x');
  const body = await new Promise((ok) => { let s = ''; req.on('data', (c) => { s += c; }); req.on('end', () => ok(new URLSearchParams(s))); });
  const json = (code, o) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(o)); };
  if (u.pathname === '/oidc/auth') {
    const q = u.searchParams; const who = core.people.get(core.current);
    assert.equal(q.get('scope'), 'openid profile permissions'); assert.equal(q.get('code_challenge_method'), 'S256'); assert.equal(q.get('client_id'), 'audit');
    if (!who) { res.writeHead(200); return res.end('sign in'); }
    const code = crypto.randomBytes(8).toString('hex');
    core.codes.set(code, { sub: who.sub, challenge: q.get('code_challenge'), redirect: q.get('redirect_uri') });
    res.writeHead(302, { location: `${q.get('redirect_uri')}?${new URLSearchParams({ code, state: q.get('state') })}` }); return res.end();
  }
  const issue = (sub) => {
    const at = crypto.randomBytes(8).toString('hex'), rt = crypto.randomBytes(8).toString('hex');
    core.tokens.set(at, sub); core.refresh.set(rt, sub);
    return { access_token: at, refresh_token: rt, id_token: jwt({ iss: core.issuer, sub, aud: 'audit', auth_time: Math.floor(Date.now() / 1000) }) };
  };
  if (u.pathname === '/oidc/token') {
    if (req.headers.authorization !== 'Basic ' + Buffer.from('audit:' + core.secret).toString('base64')) return json(401, { error: 'invalid_client' });
    if (body.get('grant_type') === 'authorization_code') {
      const c = core.codes.get(body.get('code')); core.codes.delete(body.get('code'));
      const ok = c && crypto.createHash('sha256').update(body.get('code_verifier') || '').digest('base64url') === c.challenge && c.redirect === body.get('redirect_uri');
      return ok ? json(200, issue(c.sub)) : json(400, { error: 'invalid_grant' });
    }
    if (body.get('grant_type') === 'refresh_token') {
      const sub = core.refresh.get(body.get('refresh_token')); const p = [...core.people.values()].find((x) => x.sub === sub);
      // core refuses a renewal for a deactivated person or one with no permission left in the product
      if (!p || !p.active || !p.permissions.length) return json(400, { error: 'invalid_grant' });
      return json(200, issue(sub));
    }
  }
  if (u.pathname === '/oidc/me') {
    const sub = core.tokens.get((req.headers.authorization || '').replace('Bearer ', ''));
    const p = [...core.people.values()].find((x) => x.sub === sub);
    return p ? json(200, { sub, name: p.name, preferred_username: p.login, permissions: p.permissions }) : json(401, {});
  }
  if (u.pathname === '/oidc/jwks') return json(200, { keys: [jwk] });
  json(404, {});
});

let base = '', server, deps, idSu, mdSu, auditSu;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'mac-pl-'));
const ids = {};
test.before(async () => {
  core.issuer = (await listen(coreSrv)) + '/oidc';
  assert.deepEqual(await migrate(`${SU}/audit`, { role: 'audit_owner' }), ['0001_init.sql']);
  assert.deepEqual(await migrate(`${SU}/audit`, { role: 'audit_owner' }), [], 'second run: up to date');
  idSu = su('identity'); mdSu = su('master_data'); auditSu = su('audit');
  // What apply does for a licensed product: its links switched on through the platform's own function.
  await idSu`select platform.set_link('audit_app', array['employee_v1'], true, 'CC-A1', 'audit reads employees')`;
  await mdSu`select platform.set_link('audit_app', array['room_v1', 'equipment_v1', 'product_v1'], true, 'CC-A2', 'audit reads master data')`;
  for (const [k, login, name, active] of [['ann', 'ann', 'Ann Auditor', true], ['bob', 'bob', 'Bob Auditee', true], ['old', 'old', 'Old Leaver', false]]) {
    ids[k] = (await idSu`insert into employee (login, full_name, active) values (${login}, ${name}, ${active}) returning id::text`)[0].id;
  }
  for (const [k, kind, code, name, active] of [['room', 'room', 'R-101', 'Granulation room', true], ['eq', 'equipment', 'EQ-7', 'Fluid bed dryer', true],
    ['prod', 'product', 'P-1', 'Paracetamol 500 mg tablets', true], ['eqOld', 'equipment', 'EQ-0', 'Retired blender', false]]) {
    ids[k] = (await mdSu`insert into item (kind, code, name, active) values (${kind}, ${code}, ${name}, ${active}) returning id::text`)[0].id;
  }
  Object.assign(process.env, { AUDIT_DATABASE_URL: `${APP}/audit`, IDENTITY_DATABASE_URL: `${APP}/identity`, MASTER_DATA_DATABASE_URL: `${APP}/master_data`,
    OIDC_ISSUER: core.issuer, OIDC_CLIENT_SECRET: core.secret, OIDC_REDIRECT_URI: 'http://placeholder/cb', COOKIE_SECURE: 'false', SITE_NAME: 'Pune plant',
    WEB_ASK_FLAG: path.join(tmp, 'ask-enabled') });
  fs.writeFileSync(process.env.WEB_ASK_FLAG, 'on'); // must be ignored on the platform
  // the redirect URI needs the port: start, then point the client at it
  const { start } = await import('../../server.js');
  const pre = http.createServer(); base = await listen(pre); pre.close();
  process.env.OIDC_REDIRECT_URI = `${base}/cb`;
  ({ server, deps } = await start());
  await new Promise((r) => server.listen(Number(new URL(base).port), '127.0.0.1', r));
});
test.after(async () => {
  server?.close(); coreSrv.close();
  await idSu?.end(); await mdSu?.end(); await auditSu?.end(); fs.rmSync(tmp, { recursive: true });
});

/** A browser: cookie jar per origin; follows redirects through the stand-in core. */
function browser() {
  const jars = new Map();
  async function go(url, init = {}) {
    const o = new URL(url).origin; const jar = jars.get(o) || new Map(); jars.set(o, jar);
    const r = await fetch(url, { ...init, redirect: 'manual', headers: { ...(init.headers || {}), cookie: [...jar].map(([k, v]) => `${k}=${v}`).join('; ') } });
    for (const c of r.headers.getSetCookie()) { const [kv] = c.split(';'); const i = kv.indexOf('='); const k = kv.slice(0, i), v = kv.slice(i + 1); if (!v || /Max-Age=0/i.test(c)) jar.delete(k); else jar.set(k, v); }
    return r;
  }
  async function signIn() {
    let r = await go(`${base}/login`);
    for (let i = 0; i < 5 && r.headers.get('location'); i++) r = await go(new URL(r.headers.get('location'), base).href);
    return { status: r.status, body: await r.text(), url: r.url };
  }
  const api = async (method, p, body) => {
    const r = await go(base + p, { method, headers: { 'X-Requested-With': 'mac', 'content-type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
    return { status: r.status, json: r.headers.get('content-type')?.includes('json') ? await r.json() : null, r };
  };
  return { signIn, api, go, jars };
}
async function person(login, permissions, name = 'Name of ' + login) {
  const sub = ids[login] || crypto.randomUUID();
  core.people.set(login, { sub, login, name, permissions, active: true });
  core.current = login;
  const b = browser(); const r = await b.signIn(); b.first = r; b.sub = sub;
  return b;
}
const ALL = ['audit.view', 'audit.template.edit', 'audit.audit.perform', 'audit.audit.close'];
const CFG = { markets: ['india'], plants: ['oral-solid'] };
async function newAudit(b) {
  const t = (await b.api('POST', '/api/templates', { name: 'T', config: CFG })).json.id;
  return (await b.api('POST', '/api/audits', { template_id: t, name: 'A' })).json.id;
}

test('PL-01 sign-on through core (code flow + PKCE): permissions only from the claim; none = no entry', async () => {
  const b = await person('ann', ['audit.view', 'audit.audit.perform', 'other.product.code']);
  const me = (await b.api('GET', '/api/me')).json;
  assert.equal(me.mode, 'platform'); assert.equal(me.name, 'Name of ann'); assert.equal(me.company, 'Pune plant');
  assert.deepEqual(me.permissions, ['audit.view', 'audit.audit.perform'], 'only this product\'s codes count');
  assert.deepEqual(me.links, { identity: true, master_data: true });
  const n = await person('nobody', []);
  assert.equal(n.first.status, 403); assert.match(n.first.body, /no right to use Medhanta CLEAR/);
  assert.equal((await n.api('GET', '/api/me')).status, 401);
  // no local logins or passwords on the platform
  assert.equal((await b.api('POST', '/api/login', { email: 'a', password: 'b' })).status, 404);
  assert.equal((await b.api('POST', '/api/password', { old: 'a', new: 'bbbbbbbbbbbb' })).status, 404);
  // a forged callback (state not started by this browser) is refused
  assert.equal((await browser().go(`${base}/cb?code=x&state=y`)).status, 400);
  // the library itself needs a session
  assert.equal((await fetch(base + '/data/items.json')).status, 401);
  assert.equal((await b.go(base + '/data/items.json')).status, 200);
});

test('PL-01 each action checks its permission on the server', async () => {
  const admin = await person('adm', ALL); const aid = await newAudit(admin);
  const tid = (await admin.api('GET', '/api/templates')).json[0].id;
  const view = await person('v1', ['audit.view']);
  assert.equal((await view.api('GET', '/api/templates')).status, 200);
  assert.equal((await view.api('GET', `/api/audits/${aid}/export.xlsx`)).status, 200);
  assert.equal((await view.api('POST', '/api/templates', { name: 'x', config: CFG })).status, 403);
  assert.equal((await view.api('PUT', '/api/audits/' + aid, { answers: {} })).status, 403);
  const ed = await person('e1', ['audit.template.edit']);
  assert.equal((await ed.api('PUT', '/api/templates/' + tid, { name: 'T2', config: CFG })).status, 200);
  assert.equal((await ed.api('POST', '/api/audits', { template_id: tid })).status, 403);
  const perf = await person('p1', ['audit.audit.perform']);
  assert.equal((await perf.api('PUT', '/api/audits/' + aid, { answers: {}, name: 'renamed' })).status, 200);
  assert.equal((await perf.api('PUT', '/api/audits/' + aid, { status: 'closed' })).status, 403);
  assert.equal((await perf.api('DELETE', '/api/audits/' + aid)).status, 403);
  assert.equal((await perf.api('DELETE', '/api/templates/' + tid)).status, 403);
  const closer = await person('c1', ['audit.audit.close']);
  assert.equal((await closer.api('PUT', '/api/audits/' + aid, { status: 'closed', name: 'not allowed to rename' })).status, 200);
  const a = (await closer.api('GET', '/api/audits/' + aid)).json;
  assert.equal(a.status, 'closed'); assert.equal(a.name, 'renamed', 'close-only right changes the status only');
  assert.equal((await perf.api('PUT', '/api/audits/' + aid, { answers: {} })).status, 409, 'closed audit is read-only');
  assert.equal((await closer.api('PUT', '/api/audits/' + aid, { answers: {} })).status, 403);
  // the audit trail records who did it (insert-only)
  const tr = await auditSu`select action, user_name from audit_trail where object_type = 'audit' and object_id = ${aid} order by id`;
  assert.deepEqual(tr.map((x) => x.action), ['audit.create', 'audit.header', 'audit.close']);
  assert.equal(tr[2].user_name, 'Name of c1');
});

test('PL-01 permissions are renewed from core: a revoked right ends the session; core logout ends it at once', async () => {
  const b = await person('rv', ['audit.view']);
  assert.equal((await b.api('GET', '/api/templates')).status, 200);
  core.people.get('rv').permissions = [];
  assert.equal((await b.api('GET', '/api/templates')).status, 200, 'within the renewal interval');
  await auditSu`update sessions set checked_at = now() - interval '6 minutes'`;
  assert.equal((await b.api('GET', '/api/templates')).status, 401, 'renewal refused by core: session ended');
  // a granted right arrives at the next renewal
  const g = await person('gr', ['audit.view']);
  core.people.get('gr').permissions = ['audit.view', 'audit.template.edit'];
  await auditSu`update sessions set checked_at = now() - interval '6 minutes'`;
  assert.deepEqual((await g.api('GET', '/api/me')).json.permissions, ['audit.view', 'audit.template.edit']);
  // idle sessions end
  await auditSu`update sessions set last_seen_at = now() - interval '16 minutes' where user_id = (select id from users where login = 'gr')`;
  assert.equal((await g.api('GET', '/api/me')).status, 401);
  // back-channel logout (OIDC Back-Channel Logout 1.0)
  const x = await person('bc', ['audit.view']);
  const tok = (o = {}) => jwt({ iss: core.issuer, aud: 'audit', iat: Math.floor(Date.now() / 1000), sub: x.sub, jti: crypto.randomUUID(), events: { 'http://schemas.openid.net/event/backchannel-logout': {} }, ...o });
  const post = (t) => fetch(base + '/backchannel-logout', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ logout_token: t }) });
  assert.equal((await post(tok({ iss: 'http://evil' }))).status, 400);
  assert.equal((await post(jwt({ iss: core.issuer, aud: 'audit', iat: Math.floor(Date.now() / 1000), sub: x.sub, events: { 'http://schemas.openid.net/event/backchannel-logout': {} } }, crypto.generateKeyPairSync('rsa', { modulusLength: 2048 }).privateKey))).status, 400, 'bad signature');
  assert.equal((await x.api('GET', '/api/me')).status, 200);
  assert.equal((await post(tok())).status, 200);
  assert.equal((await x.api('GET', '/api/me')).status, 401);
  // logout here sends the browser to core's session end
  const y = await person('lo', ['audit.view']);
  const out = (await y.api('POST', '/api/logout')).json;
  assert.match(out.logoutUrl, /\/oidc\/session\/end\?id_token_hint=/);
  assert.equal((await y.api('GET', '/api/me')).status, 401);
});

test('PL-07 auditors, auditees, rooms and finding links are picked from core and kept as at saving', async () => {
  const b = await person('ann', ALL);
  const people = (await b.api('GET', '/api/pick/employee?q=au')).json;
  assert.ok(people.some((p) => p.id === ids.ann) && people.some((p) => p.id === ids.bob) && !people.some((p) => p.id === ids.old), 'active people only');
  const eq = (await b.api('GET', '/api/pick/equipment?q=EQ')).json;
  assert.deepEqual(eq.map((x) => x.code), ['EQ-7'], 'inactive equipment not offered');
  const aid = await newAudit(b);
  const a0 = (await b.api('GET', '/api/audits/' + aid)).json;
  assert.equal(a0.site, 'Pune plant');
  const DATA = JSON.parse(fs.readFileSync(new URL('../../data/items.json', import.meta.url)));
  const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.pt.includes('all') && x.aud === 'manufacturer' && x.u.some((u) => u[3]));
  const k = it.id + '#' + it.u.find((u) => u[3])[0];
  const r = await b.api('PUT', '/api/audits/' + aid, {
    header: { auditors: [{ id: ids.ann, name: 'tampered' }], auditees: [{ id: ids.bob }], rooms: [{ id: ids.room }] },
    answers: { [k]: { a: 'No', note: 'dryer filter torn', links: [{ kind: 'equipment', id: ids.eq }, { kind: 'product', id: ids.prod }, { kind: 'room', id: ids.room }] } },
  });
  assert.equal(r.status, 200, JSON.stringify(r.json));
  let a = (await b.api('GET', '/api/audits/' + aid)).json;
  assert.deepEqual(a.header.auditors, [{ id: ids.ann, login: 'ann', name: 'Ann Auditor' }], 'display values from the view, not the client');
  assert.deepEqual(a.header.auditees, [{ id: ids.bob, login: 'bob', name: 'Bob Auditee' }]);
  assert.equal(a.auditor, 'Ann Auditor');
  assert.deepEqual(a.answers[k].links, [{ kind: 'equipment', id: ids.eq, code: 'EQ-7', name: 'Fluid bed dryer', version: 1 },
    { kind: 'product', id: ids.prod, code: 'P-1', name: 'Paracetamol 500 mg tablets', version: 1 }, { kind: 'room', id: ids.room, code: 'R-101', name: 'Granulation room', version: 1 }]);
  // master data and identity change; the saved audit keeps the values as they were, also after another save
  await mdSu`update item set name = 'Fluid bed dryer 2', version = 2 where id = ${ids.eq}`;
  await idSu`update employee set full_name = 'Ann Renamed' where id = ${ids.ann}`;
  assert.equal((await b.api('PUT', '/api/audits/' + aid, { header: a.header, answers: { ...a.answers, [k]: { ...a.answers[k], note: 'filter torn, replaced' } } })).status, 200);
  a = (await b.api('GET', '/api/audits/' + aid)).json;
  assert.equal(a.answers[k].links[0].name, 'Fluid bed dryer'); assert.equal(a.answers[k].links[0].version, 1);
  assert.equal(a.header.auditors[0].name, 'Ann Auditor');
  // Excel shows the values as saved
  const x = await b.api('GET', `/api/audits/${aid}/export.xlsx`);
  assert.equal(x.status, 200);
  const ExcelJS = (await import('exceljs')).default; const wb = new ExcelJS.Workbook(); await wb.xlsx.load(Buffer.from(await x.r.arrayBuffer()));
  let found = false; wb.getWorksheet('Check points').eachRow((row) => { if (row.values.some((v) => String(v).includes('equipment: EQ-7 Fluid bed dryer'))) found = true; });
  assert.ok(found, 'finding links in Excel');
  assert.equal(wb.getWorksheet('Summary').getRow(5).values[2], 'Bob Auditee');
});

test('PL-08 at writing, an inactive or unknown person or master-data item is refused; typed names refused while linked', async () => {
  const b = await person('ann', ALL); const aid = await newAudit(b);
  const DATA = JSON.parse(fs.readFileSync(new URL('../../data/items.json', import.meta.url)));
  const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.pt.includes('all') && x.aud === 'manufacturer' && x.u.some((u) => u[3]));
  const k = it.id + '#' + it.u.find((u) => u[3])[0];
  for (const body of [
    { header: { auditors: [{ id: ids.old }] } },
    { header: { auditees: [{ id: '00000000-0000-4000-8000-000000000000' }] } },
    { answers: { [k]: { a: 'No', links: [{ kind: 'equipment', id: ids.eqOld }] } } },
    { answers: { [k]: { a: 'No', links: [{ kind: 'equipment', id: ids.room }] } } },  // a room is not equipment
    { header: { auditors: [{ name: 'Typed Person' }] } },
    { answers: { [k]: { a: 'No', links: [{ kind: 'room', name: 'typed room' }] } } },
  ]) {
    const r = await b.api('PUT', '/api/audits/' + aid, body);
    assert.equal(r.status, 400, JSON.stringify(body)); assert.match(r.json.error, /No such active|Pick the/);
  }
  const a = (await b.api('GET', '/api/audits/' + aid)).json;
  assert.deepEqual(a.answers, {}); assert.deepEqual(a.header.auditors, []);
});

test('PL-08 core is read only through report views; a cut link shows "connection off" and serves nothing stale', async () => {
  const id = appDb('identity'); const md = appDb('master_data');
  assert.equal(await sqlstate(id`select * from public.employee`), '42501');
  assert.equal(await sqlstate(md`select * from public.item`), '42501');
  assert.equal(await sqlstate(md`insert into public.item (kind, code, name) values ('room', 'X', 'x')`), '42501');
  assert.equal(await sqlstate(md`select 1 from report.room_v1`), 'ok');
  await id.end(); await md.end();
  const b = await person('ann', ALL); const aid = await newAudit(b);
  assert.equal((await b.api('PUT', '/api/audits/' + aid, { header: { rooms: [{ id: ids.room }] } })).status, 200);
  await mdSu`select platform.set_link('audit_app', array['room_v1', 'equipment_v1', 'product_v1'], false, 'CC-A3', 'cut for test')`;
  try {
    const r = await b.api('GET', '/api/pick/room?q=R');
    assert.equal(r.status, 503); assert.equal(r.json.error, 'Connection to master data is off. Ask your administrator.');
    const s = await b.api('PUT', '/api/audits/' + aid, { header: { rooms: [{ id: ids.room }], auditors: [] } , answers: {} });
    assert.equal(s.status, 200, 'already saved values need no read');
    const n = await b.api('PUT', '/api/audits/' + aid, { header: { rooms: [{ id: ids.room }] }, answers: {} });
    assert.equal(n.status, 200);
    const DATA = JSON.parse(fs.readFileSync(new URL('../../data/items.json', import.meta.url)));
    const it = DATA.items.find((x) => x.reg === 'Schedule M' && x.pt.includes('all') && x.aud === 'manufacturer' && x.u.some((u) => u[3]));
    const k = it.id + '#' + it.u.find((u) => u[3])[0];
    const w = await b.api('PUT', '/api/audits/' + aid, { answers: { [k]: { a: 'No', links: [{ kind: 'product', id: ids.prod }] } } });
    assert.equal(w.status, 503, 'a new pick needs the link'); assert.match(w.json.error, /Connection to master data is off/);
    assert.equal((await b.api('GET', '/api/audits/' + aid)).json.header.rooms[0].name, 'Granulation room', 'stored values still shown');
    assert.equal((await b.api('GET', '/api/pick/employee?q=a')).status, 200, 'identity link still on');
  } finally {
    await mdSu`select platform.set_link('audit_app', array['room_v1', 'equipment_v1', 'product_v1'], true, 'CC-A4', 'restored')`;
  }
  assert.equal((await b.api('GET', '/api/pick/room?q=R')).status, 200);
});

test('PL-06 least privilege: audit_trail is insert-only, the site row and the id map are not the app\'s to change', async () => {
  const db = appDb('audit');
  assert.equal(await sqlstate(db`update audit_trail set action = 'x'`), '42501');
  assert.equal(await sqlstate(db`delete from audit_trail`), '42501');
  assert.equal(await sqlstate(db`update companies set name = 'x'`), '42501');
  assert.equal(await sqlstate(db`update users set employee_id = gen_random_uuid()`), '42501');
  assert.equal(await sqlstate(db`delete from users`), '42501');
  assert.equal(await sqlstate(auditSu`update audit_trail set action = 'x'`), '42501', 'even the owner cannot change the trail');
  await db.end();
});

test('platform: health endpoint; Ask is off even with the flag file; no internal texts in the data', async () => {
  const h = await (await fetch(base + '/api/health')).json();
  assert.equal(h.status, 'ok'); assert.equal(h.db, 'ok'); assert.equal(h.mode, 'platform');
  const b = await person('ann', ['audit.view']);
  assert.equal((await b.api('GET', '/api/me')).json.ask, false);
  assert.equal((await b.api('POST', '/api/ask', { question: 'water for injection?' })).json.status, 'unavailable');
  assert.ok(deps.mode === 'platform');
});

// Browser run (PGTEST_E2E=1; uses playwright-core + Chromium already on the server, read-only): sign in through core,
// pick auditor / equipment from Medhanta, rights hide buttons.
test('PL-01 PL-07 browser: sign-in through core, pickers from Medhanta, buttons follow the rights', { skip: !process.env.PGTEST_E2E }, async () => {
  const { createRequire } = await import('node:module');
  const { chromium } = createRequire(process.env.PW_MODULES || './node_modules/')('playwright-core');
  const admin = await person('ann', ALL); const aid = await newAudit(admin);
  core.current = 'ann';
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 390, height: 800 } });
  const errs = []; pg.on('pageerror', (e) => errs.push(e.message)); pg.on('console', (m) => m.type() === 'error' && !/401/.test(m.text()) && errs.push(m.text()));
  try {
    await pg.goto(base + '/#/audit/' + aid);
    await pg.waitForSelector('a[href="/login"]'); await pg.click('a[href="/login"]');
    await pg.waitForSelector('.hdrpick');
    assert.ok((await pg.inputValue('.panel input[disabled]')).includes('Pune plant'), 'site from the platform, read-only');
    const ins = pg.locator('.hdrpick input[type=search]');
    await ins.nth(0).fill('Ann'); await pg.locator('.pickres button', { hasText: 'Ann' }).first().click();
    await pg.locator('details.area summary').first().click();
    await pg.locator('.linkbtn').first().click();
    await pg.locator('.links select').first().selectOption('equipment');
    await pg.locator('.links input[type=search]').first().fill('EQ'); await pg.locator('.links .pickres button', { hasText: 'EQ-7' }).click();
    await pg.locator('.ans button.No').first().click();
    await pg.waitForSelector('text=Saved ✓', { timeout: 10000 });
    const a = (await admin.api('GET', '/api/audits/' + aid)).json;
    assert.equal(a.header.auditors[0].id, ids.ann);
    assert.ok(Object.values(a.answers).some((v) => v.links?.some((l) => l.id === ids.eq && l.code === 'EQ-7')));
    assert.equal(await pg.locator('nav a[href="#/ask"]').count(), 0, 'no Ask on the platform');
    await pg.screenshot({ path: path.join(process.env.PGTEST_SHOTS || tmp, 'platform-audit.png') });
    // a view-only person: no New template / Start audit / Delete; answers disabled
    await pg.evaluate(() => fetch('/api/logout', { method: 'POST', headers: { 'X-Requested-With': 'mac' } }));
    core.people.set('viewer', { sub: crypto.randomUUID(), login: 'viewer', name: 'Vera Viewer', permissions: ['audit.view'], active: true }); core.current = 'viewer';
    await pg.goto(base + '/login'); await pg.waitForSelector('text=Templates');
    assert.equal(await pg.locator('text=+ New template').count(), 0);
    assert.equal(await pg.locator('button:has-text("Start audit")').count(), 0);
    assert.equal(await pg.locator('button:has-text("Delete")').count(), 0);
    await pg.goto(base + '/#/audit/' + aid); await pg.waitForSelector('.hdrpick');
    await pg.locator('details.area summary').first().click();
    assert.ok(await pg.locator('.ans button').first().isDisabled());
    assert.equal(await pg.locator('button:has-text("Close audit")').isVisible(), false);
    assert.deepEqual(errs, []);
  } finally { await br.close(); }
});
