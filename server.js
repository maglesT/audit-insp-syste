// Medhanta CLEAR: starts the app. Two installations, chosen by the environment:
//  - platform (AUDIT_DATABASE_URL set, as the Medhanta platform's apply writes it): PostgreSQL + sign-on through
//    core (OIDC_ISSUER, OIDC_CLIENT_SECRET, OIDC_REDIRECT_URI; OIDC_CLIENT_ID default "audit"), PORT 3000 on 0.0.0.0;
//    links: IDENTITY_DATABASE_URL (employee_v1), MASTER_DATA_DATABASE_URL (room_v1, equipment_v1, product_v1),
//    each optional (unset = link off = typed values). SITE_NAME: the site's name shown in audits. Ask is off.
//  - standalone (no AUDIT_DATABASE_URL): SQLite at AUDIT_DB (default db/audit.sqlite) + local logins (adduser.js),
//    127.0.0.1:8790. Ask only while the file ask-enabled exists.
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createApp, VERSION } from './src/app.js';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const env = process.env;
const nz = (v) => (v === undefined || v === '' ? undefined : v);

export async function start() {
  let deps;
  if (nz(env.AUDIT_DATABASE_URL)) {
    for (const k of ['OIDC_ISSUER', 'OIDC_CLIENT_SECRET', 'OIDC_REDIRECT_URI']) if (!nz(env[k])) throw new Error(`${k} is required`);
    const { pgStore } = await import('./src/store-pg.js');
    const { oidcSignOn } = await import('./src/signon.js');
    const { coreLinks } = await import('./src/core-links.js');
    const links = coreLinks({ identityUrl: nz(env.IDENTITY_DATABASE_URL), masterDataUrl: nz(env.MASTER_DATA_DATABASE_URL) });
    deps = { mode: 'platform', store: pgStore(env.AUDIT_DATABASE_URL), links, siteName: nz(env.SITE_NAME),
      signOn: oidcSignOn({ issuer: env.OIDC_ISSUER.replace(/\/$/, ''), clientId: nz(env.OIDC_CLIENT_ID) || 'audit', clientSecret: env.OIDC_CLIENT_SECRET, redirectUri: env.OIDC_REDIRECT_URI }),
      cookieSecure: env.COOKIE_SECURE !== 'false', host: nz(env.HOST) || '0.0.0.0', port: Number(env.PORT || 3000) };
  } else {
    const { sqliteStore } = await import('./src/store-sqlite.js');
    const dbFile = env.AUDIT_DB || path.join(DIR, 'db', 'audit.sqlite');
    deps = { mode: 'standalone', store: sqliteStore(dbFile), askFlag: env.WEB_ASK_FLAG || path.join(DIR, 'ask-enabled'), askCmd: env.WEB_ASK_CMD,
      askLog: path.join(path.dirname(dbFile), 'ask-log.jsonl'), host: nz(env.HOST) || '127.0.0.1', port: Number(env.PORT || 8790) };
  }
  const app = createApp({ ...deps, dataFile: env.WEB_DATA });
  const server = http.createServer(app.handler);
  const prune = deps.mode === 'platform' ? setInterval(() => deps.store.pruneSessions(15).catch(() => {}), 10 * 60e3) : null;
  prune?.unref();
  server.on('close', () => { clearInterval(prune); deps.store.close(); deps.links?.close(); });
  return { server, deps, app };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const { server, deps, app } = await start();
  server.listen(deps.port, deps.host, () => console.log(`Medhanta CLEAR ${VERSION} (${deps.mode}) on http://${deps.host}:${deps.port} (data ${app.DATA.version}, ${app.DATA.items.length} items)`));
  for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => server.close(() => process.exit(0)));
}
