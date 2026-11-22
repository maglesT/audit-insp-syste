# Medhanta Audit Checklist, platform image (build from the repo root: docker build -f ops/Dockerfile .).
# Runs as the platform installation: AUDIT_DATABASE_URL, OIDC_ISSUER, OIDC_CLIENT_SECRET, OIDC_REDIRECT_URI, PORT=3000;
# optional IDENTITY_DATABASE_URL, MASTER_DATA_DATABASE_URL (links), SITE_NAME. The platform's apply runs
# db/migrations as audit_owner. Ask (RAG) is off: no API key and no rag/ code in the image. Only the built library
# data/items.json is copied (no WHO / PIC/S text, no internal source files).
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.js ./
COPY src ./src
COPY public ./public
COPY brand ./brand
COPY fonts ./fonts
COPY data/items.json ./data/items.json
COPY db/migrate.js ./db/migrate.js
COPY db/migrations ./db/migrations
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://127.0.0.1:3000/api/health >/dev/null || exit 1
CMD ["node", "--no-warnings", "server.js"]
