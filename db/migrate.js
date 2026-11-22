// Applies db/migrations/NNNN_name.sql in order, each in its own transaction, recorded in platform.migration with the
// file's SHA-256: the same algorithm as the Medhanta platform's db/migrate.ts (which runs these files itself, as
// audit_owner, at apply). Used by the tests and for a manual setup. A recorded file whose content changed is an error.
// Usage: MIGRATION_DATABASE_URL=postgres://... [MIGRATION_ROLE=audit_owner] node db/migrate.js
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import postgres from 'postgres';

export const MIGRATIONS_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), 'migrations');

export async function migrate(url, { role, dir = MIGRATIONS_DIR } = {}) {
  const sql = postgres(url, { max: 1, onnotice: () => {} });
  const asOwner = async (tx) => { if (role) await tx.unsafe(`set local role ${role.replace(/[^a-z0-9_]/g, '')}`); };
  try {
    await sql.begin(async (tx) => {
      await asOwner(tx);
      await tx`create schema if not exists platform`;
      await tx`create table if not exists platform.migration (name text primary key, sha256 text not null, applied_at timestamptz not null default now())`;
    });
    const done = new Map((await sql`select name, sha256 from platform.migration`).map((r) => [r.name, r.sha256]));
    const applied = [];
    for (const file of readdirSync(dir).filter((f) => /^\d{4}_[a-z0-9_]+\.sql$/.test(f)).sort()) {
      const text = readFileSync(path.join(dir, file), 'utf8');
      const sha = createHash('sha256').update(text).digest('hex');
      if (done.has(file)) { if (done.get(file) !== sha) throw new Error(`${file} changed after it was applied`); continue; }
      await sql.begin(async (tx) => { await asOwner(tx); await tx.unsafe(text); await tx`insert into platform.migration (name, sha256) values (${file}, ${sha})`; });
      applied.push(file);
    }
    return applied;
  } finally { await sql.end(); }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const url = process.env.MIGRATION_DATABASE_URL;
  if (!url) throw new Error('MIGRATION_DATABASE_URL is required');
  const applied = await migrate(url, { role: process.env.MIGRATION_ROLE });
  console.log(applied.length ? `applied: ${applied.join(', ')}` : 'up to date');
}
