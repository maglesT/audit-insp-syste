// Reading core (platform PL-07, PL-08): identity's employee_v1 and master_data's room_v1, equipment_v1, product_v1,
// ONLY through the report.*_v1 views, with the product's own login on a second connection pool per provider.
// No local copy (D-02). A cut link (42501 grant gone, 28000 login off, or no connection) stops the feature with
// "Connection to <provider> is off. Ask your administrator." and nothing stale is served.
// Without a link (URL unset: standalone, or link not switched on) values are TYPED by the user.
import postgres from 'postgres';

export class ConnectionOff extends Error {
  constructor(provider) { super(`Connection to ${provider} is off. Ask your administrator.`); this.code = 503; }
}
const CUT = ['42501', '28000', '57P01', '3D000', 'ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND', 'EAI_AGAIN', 'CONNECT_TIMEOUT', 'CONNECTION_CLOSED', 'CONNECTION_ENDED', 'CONNECTION_DESTROYED'];
export const isCut = (e) => { const c = String(e?.code ?? ''); return CUT.includes(c) || c.startsWith('08'); };

// kind -> provider, view, columns kept as at saving
export const KINDS = {
  employee: { provider: 'identity', label: 'person', view: 'employee_v1' },
  room: { provider: 'master data', label: 'room / area', view: 'room_v1' },
  equipment: { provider: 'master data', label: 'equipment', view: 'equipment_v1' },
  product: { provider: 'master data', label: 'product', view: 'product_v1' },
};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export const isUuid = (s) => typeof s === 'string' && UUID.test(s);

export function coreLinks({ identityUrl, masterDataUrl }) {
  const opt = { max: 3, onnotice: () => {}, connection: { TimeZone: 'UTC' }, connect_timeout: 5 };
  const pools = { identity: identityUrl ? postgres(identityUrl, opt) : null, 'master data': masterDataUrl ? postgres(masterDataUrl, opt) : null };
  const read = async (provider, q) => {
    try { return await q(pools[provider]); } catch (e) { if (isCut(e)) throw new ConnectionOff(provider); throw e; }
  };
  const norm = (kind, r) => (kind === 'employee'
    ? { id: r.id, login: r.login, name: r.full_name, active: r.active }
    : { id: r.id, code: r.code, name: r.name, version: r.version, active: r.active });
  async function query(kind, { q = '', ids = null, activeOnly = true, limit = 30 } = {}) {
    const k = KINDS[kind]; const pv = k.provider;
    return read(pv, async (sql) => {
      const v = sql('report.' + k.view);
      const like = '%' + String(q).slice(0, 60).replace(/[\\%_]/g, (m) => '\\' + m) + '%';
      const rows = kind === 'employee'
        ? await sql`select id::text, login, full_name, active from ${v} where ${ids ? sql`id = any(${ids}::uuid[])` : sql`(full_name ilike ${like} or login ilike ${like})`}
            ${activeOnly ? sql`and active` : sql``} order by full_name limit ${ids ? 1000 : limit}`
        : await sql`select id::text, code, name, version, active from ${v} where ${ids ? sql`id = any(${ids}::uuid[])` : sql`(code ilike ${like} or name ilike ${like})`}
            ${activeOnly ? sql`and active` : sql``} order by code limit ${ids ? 1000 : limit}`;
      return rows.map((r) => norm(kind, r));
    });
  }
  return {
    linked: (kind) => !!pools[KINDS[kind].provider],
    status: () => ({ identity: !!pools.identity, master_data: !!pools['master data'] }),
    search: (kind, q) => query(kind, { q }),
    // PL-08 write-time check: the current rows for these ids (also inactive ones, so the caller can refuse them).
    byIds: (kind, ids) => query(kind, { ids, activeOnly: false }),
    async close() { for (const p of Object.values(pools)) await p?.end({ timeout: 5 }); },
  };
}
