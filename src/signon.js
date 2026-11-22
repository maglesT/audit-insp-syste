// Sign-on through Medhanta core (platform PL-01): OIDC code flow with PKCE, scope "openid profile permissions".
// Who someone is and which Audit Checklist permissions they hold come from core's token and nothing else.
// Ported from the Pharma Logbook (server/signon.ts) to plain JS.
import { createHash, createPublicKey, randomBytes, verify } from 'node:crypto';

export const PERMISSIONS = {
  'audit.view': 'See templates, audits and exports',
  'audit.template.edit': 'Create, edit and delete checklist templates',
  'audit.audit.perform': 'Start audits and record answers, observations and findings',
  'audit.audit.close': 'Close, re-open and delete audits',
};
export const CODES = Object.keys(PERMISSIONS);
// Only this product's known codes count; anything else in the claim is ignored.
export const asPermissions = (codes) => CODES.filter((c) => Array.isArray(codes) && codes.includes(c));

export const BACKCHANNEL_EVENT = 'http://schemas.openid.net/event/backchannel-logout';
const LOGOUT_TOKEN_MAX_AGE_S = 300;

/** The claims a logout token must carry (Back-Channel Logout 1.0 section 2.6), after its signature was checked. */
export function checkLogoutClaims(c, issuer, clientId, nowS = Math.floor(Date.now() / 1000)) {
  const aud = Array.isArray(c.aud) ? c.aud : [c.aud];
  if (c.iss !== issuer) throw new Error('logout token: wrong issuer');
  if (!aud.includes(clientId)) throw new Error('logout token: not for this product');
  if (typeof c.iat !== 'number' || Math.abs(nowS - c.iat) > LOGOUT_TOKEN_MAX_AGE_S) throw new Error('logout token: too old');
  if (c.exp !== undefined && (typeof c.exp !== 'number' || c.exp < nowS)) throw new Error('logout token: expired');
  if (!c.events || typeof c.events !== 'object' || !(BACKCHANNEL_EVENT in c.events)) throw new Error('logout token: not a logout event');
  if (c.nonce !== undefined) throw new Error('logout token: carries a nonce');
  if (typeof c.sub !== 'string' || !c.sub) throw new Error('logout token: names nobody');
  return { sub: c.sub };
}

export const newVerifier = () => randomBytes(32).toString('base64url');
export const challengeOf = (verifier) => createHash('sha256').update(verifier).digest('base64url');

export function oidcSignOn(s) {
  const basic = `Basic ${Buffer.from(`${encodeURIComponent(s.clientId)}:${encodeURIComponent(s.clientSecret)}`).toString('base64')}`;
  async function tokens(body) {
    const res = await fetch(`${s.issuer}/token`, {
      method: 'POST', headers: { authorization: basic, 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(body), signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) throw new Error(`sign-on refused (${res.status})`);
    const t = await res.json();
    const me = await fetch(`${s.issuer}/me`, { headers: { authorization: `Bearer ${t.access_token}` }, signal: AbortSignal.timeout(10_000) });
    if (!me.ok) throw new Error(`sign-on refused (${me.status})`);
    const c = await me.json();
    // The ID token comes straight from core's token endpoint over TLS (OIDC Core 3.1.3.7): its claims are read as is.
    const id = t.id_token ? JSON.parse(Buffer.from(t.id_token.split('.')[1] ?? '', 'base64url').toString('utf8')) : {};
    if (id.sub !== undefined && id.sub !== c.sub) throw new Error('sign-on refused (token mismatch)');
    return { sub: c.sub, login: c.preferred_username ?? '', name: c.name ?? '', permissions: c.permissions ?? [], refreshToken: t.refresh_token, idToken: t.id_token };
  }
  // Core's public signing keys (JWKS), kept for an hour; an unknown key id fetches them again once.
  let jwks = null;
  async function signingKey(kid) {
    for (const fresh of [false, true]) {
      if (fresh || !jwks || Date.now() - jwks.at > 3_600_000) {
        const res = await fetch(`${s.issuer}/jwks`, { signal: AbortSignal.timeout(10_000) });
        if (!res.ok) throw new Error(`logout token: core keys unavailable (${res.status})`);
        jwks = { at: Date.now(), keys: (await res.json()).keys ?? [] };
      }
      const k = jwks.keys.find((x) => x.kty === 'RSA' && (kid === undefined || x.kid === kid));
      if (k) return createPublicKey({ key: k, format: 'jwk' });
    }
    throw new Error('logout token: unknown key');
  }
  return {
    authUrl: ({ state, challenge }) => `${s.issuer}/auth?${new URLSearchParams({
      client_id: s.clientId, response_type: 'code', redirect_uri: s.redirectUri, scope: 'openid profile permissions', state,
      code_challenge: challenge, code_challenge_method: 'S256' })}`,
    exchange: (code, verifier) => tokens({ grant_type: 'authorization_code', code, code_verifier: verifier, redirect_uri: s.redirectUri }),
    refresh: (refreshToken) => tokens({ grant_type: 'refresh_token', refresh_token: refreshToken }),
    logoutUrl: (idToken) => `${s.issuer}/session/end${idToken ? `?${new URLSearchParams({ id_token_hint: idToken, client_id: s.clientId })}` : ''}`,
    async verifyLogoutToken(token) {
      const [h, p, signature] = String(token).split('.');
      if (!h || !p || !signature) throw new Error('logout token: malformed');
      const header = JSON.parse(Buffer.from(h, 'base64url').toString('utf8'));
      if (header.alg !== 'RS256') throw new Error('logout token: unexpected algorithm');
      const key = await signingKey(header.kid);
      if (!verify('sha256', Buffer.from(`${h}.${p}`), key, Buffer.from(signature, 'base64url'))) throw new Error('logout token: bad signature');
      return checkLogoutClaims(JSON.parse(Buffer.from(p, 'base64url').toString('utf8')), s.issuer, s.clientId);
    },
  };
}
