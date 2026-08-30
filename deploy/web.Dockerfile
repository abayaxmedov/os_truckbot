# Build the Mini App, then serve it (with auto-HTTPS) via Caddy.
# Build context is the repo root (see docker-compose.prod.yml).

# --- stage 1: build the React Mini App ---
FROM node:20-alpine AS build
WORKDIR /app
COPY miniapp/package.json miniapp/package-lock.json* ./
RUN npm ci || npm install
COPY miniapp/ ./
RUN npm run build

# --- stage 2: Caddy serves static files + reverse-proxies the API ---
FROM caddy:2-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
