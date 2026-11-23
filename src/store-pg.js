// PostgreSQL store (platform): database "audit" as audit_app. Same interface as store-sqlite.js for templates and
// audits; sign-on sessions follow the Logbook pattern (core's permissions in the session, renewed every few minutes).
import postgres from 'postgres';

const iso = (d) => (d instanceof Date ? d.toISOString() : d);
const row = (r) => (r ? Object.fromEntries(Object.entries(r).map(([k, v]) => [k, iso(v)])) : r);

export function pgStore(url, { max = 10 } = {}) {
  // Sessions run in UTC so timestamps never depend on the server's zone.
  const sql = postgres(url, { max, onnotice: () => {}, connection: { TimeZone: 'UTC' }, types: { int8: { to: 20, from: [20], serialize: (x) => String(x), parse: (x) => Number(x) } } });
  const S = {
    kind: 'pg', sql,
    async health() { await sql`select 1`; },
    async close() { await sql.end({ timeout: 5 }); },

    // ----- id map + sessions (PL-01) -----
    async upsertEmployee({ sub, login, name }) {
      const [u] = await sql`insert into users (employee_id, login, name, last_login_at) values (${sub}, ${login}, ${name}, now())
        on conflict (employee_id) do update set name = excluded.name, login = excluded.login, last_login_at = now() returning id`;
      return { id: Number(u.id) };
    },
    async createSession(key, userId, { permissions, refreshToken, idToken }) {
      await sql`insert into sessions (id, user_id, permissions, refresh_token, id_token) values (${key}, ${userId}, ${permissions}, ${refreshToken ?? null}, ${idToken ?? null})`;
    },
    // One request claims a due renewal (the others go on with the current permissions).
    async claimRenewal(key, checkMinutes, idleMinutes) {
      const [due] = await sql`update sessions set checked_at = now()
        where id = ${key} and checked_at < now() - make_interval(mins => ${checkMinutes}) and last_seen_at > now() - make_interval(mins => ${idleMinutes})
        returning refresh_token`;
      return due ? { refreshToken: due.refresh_token } : null;
    },
    async renewSession(key, { permissions, refreshToken, idToken }) {
      await sql`update sessions set permissions = ${permissions}, refresh_token = coalesce(${refreshToken ?? null}, refresh_token),
        id_token = coalesce(${idToken ?? null}, id_token) where id = ${key}`;
    },
    async loadSession(key, idleMinutes, touch) {
      const [r] = await sql`update sessions s set last_seen_at = case when ${touch} then now() else s.last_seen_at end
        from users u join companies c on c.id = u.company_id
        where s.id = ${key} and u.id = s.user_id and s.last_seen_at > now() - make_interval(mins => ${idleMinutes})
        returning u.id, u.login, u.name, u.employee_id, u.company_id, c.name as company, s.permissions`;
      return r ? { id: Number(r.id), login: r.login, name: r.name, sub: r.employee_id, company_id: r.company_id, company: r.company, permissions: r.permissions } : null;
    },
    async deleteSession(key) {
      const [r] = await sql`delete from sessions where id = ${key} returning id_token, user_id`;
      return r ? { idToken: r.id_token, userId: Number(r.user_id) } : null;
    },
    async deleteSessionsOf(sub) {
      const r = await sql`delete from sessions s using users u where u.id = s.user_id and u.employee_id = ${sub} returning s.user_id`;
      return r.length;
    },
    async pruneSessions(idleMinutes) { await sql`delete from sessions where last_seen_at < now() - make_interval(mins => ${idleMinutes})`; },

    // ----- templates -----
    async listTemplates(cid) {
      return (await sql`select id, name, config, data_version, updated, updated_by from templates where company_id = ${cid} order by updated desc`).map(row);
    },
    async createTemplate(cid, t) {
      const [r] = await sql`insert into templates (company_id, name, config, data_version, updated_by) values (${cid}, ${t.name}, ${sql.json(t.config)}, ${t.data_version}, ${t.by}) returning id`;
      return Number(r.id);
    },
    async getTemplate(cid, id) {
      const [r] = await sql`select * from templates where id = ${id} and company_id = ${cid}`;
      return row(r);
    },
    async updateTemplate(id, t) {
      await sql`update templates set name = ${t.name}, config = ${sql.json(t.config)}, data_version = ${t.data_version}, updated = now(), updated_by = ${t.by} where id = ${id}`;
    },
    async deleteTemplate(id) { await sql`delete from templates where id = ${id}`; },

    // ----- audits -----
    async listAudits(cid) {
      return (await sql`select id, name, site, auditor, audit_date, status, template_name, config, answers, updated from audits where company_id = ${cid} order by updated desc`).map(row);
    },
    async createAudit(cid, a) {
      const [r] = await sql`insert into audits (company_id, template_id, template_name, name, site, auditor, audit_date, header, config, data_version, updated_by)
        values (${cid}, ${a.template_id}, ${a.template_name}, ${a.name}, ${a.site}, ${a.auditor}, ${a.audit_date}, ${sql.json(a.header)}, ${sql.json(a.config)}, ${a.data_version}, ${a.by}) returning id`;
      return Number(r.id);
    },
    async getAudit(cid, id) {
      const [r] = await sql`select * from audits where id = ${id} and company_id = ${cid}`;
      return row(r);
    },
    async updateAudit(id, a) {
      const [r] = await sql`update audits set name = ${a.name}, site = ${a.site}, auditor = ${a.auditor}, audit_date = ${a.audit_date}, status = ${a.status},
        header = ${sql.json(a.header)}, answers = ${sql.json(a.answers)}, updated = now(), updated_by = ${a.by} where id = ${id} returning updated`;
      return iso(r.updated);
    },
    // MED-11: kept with its reason; only an open audit (a closed one is final). Returns false when it was not open.
    async withdrawAudit(id, { reason, by }) {
      const r = await sql`update audits set status = 'withdrawn', withdrawn_reason = ${reason}, updated = now(), updated_by = ${by}
        where id = ${id} and status = 'open' returning id`;
      return r.length > 0;
    },

    // ----- audit trail (insert-only) -----
    async trail(u, action, objectType, objectId, detail) {
      await sql`insert into audit_trail (user_id, user_name, action, object_type, object_id, detail)
        values (${u?.id ?? null}, ${u?.name || u?.login || '-'}, ${action}, ${objectType}, ${objectId ?? null}, ${detail ? sql.json(detail) : null})`;
    },
  };
  return S;
}
