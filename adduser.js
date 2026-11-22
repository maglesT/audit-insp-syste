// Add a login (company is created if new). The password is read from stdin, or a random one is generated and
// printed ONCE (never stored in a file). Standalone (SQLite) only: on the platform people come from Medhanta core.
// Usage: node --no-warnings adduser.js <email> "<name>" "<company>" [--stdin < pwfile]   (database: AUDIT_DB or db/audit.sqlite)
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { sqliteStore, hashPw } from './src/store-sqlite.js';
const { db } = sqliteStore(process.env.AUDIT_DB || path.join(path.dirname(fileURLToPath(import.meta.url)), 'db', 'audit.sqlite'));
const fromStdin = process.argv.includes('--stdin');
const [email, name, company] = process.argv.slice(2).filter((a) => a !== '--stdin');
if (!email || !name || !company) { console.error('usage: adduser.js <email> "<name>" "<company>"'); process.exit(2); }
let pw = fromStdin ? fs.readFileSync(0, 'utf8').trim() : '';
const gen = !pw;
if (gen) pw = crypto.randomBytes(9).toString('base64url');
if (pw.length < 10) { console.error('password: at least 10 characters'); process.exit(2); }
let c = db.prepare('SELECT id FROM companies WHERE name=?').get(company);
if (!c) c = { id: Number(db.prepare('INSERT INTO companies (name) VALUES (?)').run(company).lastInsertRowid) };
db.prepare('INSERT INTO users (company_id,email,name,pw,created) VALUES (?,?,?,?,?)').run(c.id, email.toLowerCase(), name, hashPw(pw), new Date().toISOString());
console.log(`added ${email} (${company})` + (gen ? `\npassword (shown once): ${pw}` : ''));
process.exit(0);
