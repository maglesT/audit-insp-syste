// SQLite store (standalone sale): built-in node:sqlite, local logins (scrypt). Same template / audit interface as
// store-pg.js, all methods async. Opens existing web/ databases unchanged (new columns are added when missing).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

export function hashPw(pw) {
  const salt = crypto.randomBytes(16);
  const h = crypto.scryptSync(pw, salt, 64, { N: 16384, r: 8, p: 1 });
  return `scrypt$16384$8$1$${salt.toString('base64')}$${h.toString('base64')}`;
}
export function checkPw(pw, stored) {
  const [k, N, r, p, s, h] = String(stored).split('$');
  if (k !== 'scrypt') return false;
  const want = Buffer.from(h, 'base64');
  const got = crypto.scryptSync(pw, Buffer.from(s, 'base64'), want.length, { N: +N, r: +r, p: +p });
  return crypto.timingSafeEqual(want, got);
}

const J = (s, d) => { try { return s ? JSON.parse(s) : d; } catch { return d; } };
const now = () => new Date().toISOString();

export function sqliteStore(file) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id),
  email TEXT NOT NULL UNIQUE, name TEXT NOT NULL, pw TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
  expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS templates (id INTEGER PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id),
  name TEXT NOT NULL, config TEXT NOT NULL, data_version TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL,
  updated_by TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audits (id INTEGER PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id),
  template_id INTEGER, template_name TEXT NOT NULL, name TEXT NOT NULL, site TEXT, auditor TEXT, audit_date TEXT,
  status TEXT NOT NULL DEFAULT 'open', config TEXT NOT NULL, answers TEXT NOT NULL DEFAULT '{}',
  data_version TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL, updated_by TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY, at TEXT NOT NULL, user_id INTEGER, user_name TEXT NOT NULL,
  action TEXT NOT NULL, object_type TEXT NOT NULL, object_id INTEGER, detail TEXT);
CREATE TRIGGER IF NOT EXISTS audit_trail_no_update BEFORE UPDATE ON audit_trail BEGIN SELECT RAISE(ABORT, 'audit_trail is insert-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_trail_no_delete BEFORE DELETE ON audit_trail BEGIN SELECT RAISE(ABORT, 'audit_trail is insert-only'); END;`);
  if (!db.prepare('PRAGMA table_info(audits)').all().some((c) => c.name === 'header')) db.exec("ALTER TABLE audits ADD COLUMN header TEXT NOT NULL DEFAULT '{}'");
  if (!db.prepare('PRAGMA table_info(audits)').all().some((c) => c.name === 'withdrawn_reason')) db.exec('ALTER TABLE audits ADD COLUMN withdrawn_reason TEXT');

  const tpl = (r) => r && { ...r, config: J(r.config, {}) };
  const aud = (r) => r && { ...r, config: J(r.config, {}), answers: J(r.answers, {}), header: J(r.header, {}) };
  return {
    kind: 'sqlite', db,
    async health() { db.prepare('SELECT 1').get(); },
    async close() { db.close(); },

    // ----- local logins -----
    async userByEmail(email) { return db.prepare('SELECT * FROM users WHERE email=?').get(email); },
    async userPw(id) { return db.prepare('SELECT pw FROM users WHERE id=?').get(id)?.pw; },
    async setPw(id, pw) { db.prepare('UPDATE users SET pw=? WHERE id=?').run(hashPw(pw), id); },
    async createLocalSession(key, userId, expires) {
      db.prepare('DELETE FROM sessions WHERE expires<?').run(Date.now());
      db.prepare('INSERT INTO sessions VALUES (?,?,?)').run(key, userId, expires);
    },
    async loadLocalSession(key) {
      const r = db.prepare(`SELECT u.id, u.email, u.name, u.company_id, c.name AS company, s.expires FROM sessions s
        JOIN users u ON u.id=s.user_id JOIN companies c ON c.id=u.company_id WHERE s.token=?`).get(key);
      return r && r.expires >= Date.now() ? r : null;
    },
    async deleteSession(key) { db.prepare('DELETE FROM sessions WHERE token=?').run(key); return null; },

    // ----- templates -----
    async listTemplates(cid) {
      return db.prepare('SELECT id,name,config,data_version,updated,updated_by FROM templates WHERE company_id=? ORDER BY updated DESC').all(cid).map(tpl);
    },
    async createTemplate(cid, t) {
      return Number(db.prepare('INSERT INTO templates (company_id,name,config,data_version,created,updated,updated_by) VALUES (?,?,?,?,?,?,?)')
        .run(cid, t.name, JSON.stringify(t.config), t.data_version, now(), now(), t.by).lastInsertRowid);
    },
    async getTemplate(cid, id) { return tpl(db.prepare('SELECT * FROM templates WHERE id=? AND company_id=?').get(id, cid)); },
    async updateTemplate(id, t) {
      db.prepare('UPDATE templates SET name=?,config=?,data_version=?,updated=?,updated_by=? WHERE id=?').run(t.name, JSON.stringify(t.config), t.data_version, now(), t.by, id);
    },
    async deleteTemplate(id) { db.prepare('DELETE FROM templates WHERE id=?').run(id); },

    // ----- audits -----
    async listAudits(cid) {
      return db.prepare('SELECT id,name,site,auditor,audit_date,status,template_name,config,answers,updated FROM audits WHERE company_id=? ORDER BY updated DESC').all(cid).map(aud);
    },
    async createAudit(cid, a) {
      return Number(db.prepare(`INSERT INTO audits (company_id,template_id,template_name,name,site,auditor,audit_date,header,config,data_version,created,updated,updated_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(cid, a.template_id, a.template_name, a.name, a.site, a.auditor, a.audit_date, JSON.stringify(a.header),
        JSON.stringify(a.config), a.data_version, now(), now(), a.by).lastInsertRowid);
    },
    async getAudit(cid, id) { return aud(db.prepare('SELECT * FROM audits WHERE id=? AND company_id=?').get(id, cid)); },
    async updateAudit(id, a) {
      const t = now();
      db.prepare('UPDATE audits SET name=?,site=?,auditor=?,audit_date=?,status=?,header=?,answers=?,updated=?,updated_by=? WHERE id=?')
        .run(a.name, a.site, a.auditor, a.audit_date, a.status, JSON.stringify(a.header), JSON.stringify(a.answers), t, a.by, id);
      return t;
    },
    // MED-11: kept with its reason; only an open audit (a closed one is final). Returns false when it was not open.
    async withdrawAudit(id, { reason, by }) {
      return db.prepare("UPDATE audits SET status='withdrawn',withdrawn_reason=?,updated=?,updated_by=? WHERE id=? AND status='open'")
        .run(reason, now(), by, id).changes > 0;
    },

    async trail(u, action, objectType, objectId, detail) {
      db.prepare('INSERT INTO audit_trail (at,user_id,user_name,action,object_type,object_id,detail) VALUES (?,?,?,?,?,?,?)')
        .run(now(), u?.id ?? null, u?.email || u?.name || '-', action, objectType, objectId ?? null, detail ? JSON.stringify(detail) : null);
    },
  };
}
