#!/usr/bin/env bash
# Stop the local dev processes started by dev.sh (backend + Mini App). Leaves PostgreSQL running.
# Pass --db to also stop the database container.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT/.dev-pids"

if [ -f "$PID_FILE" ]; then
  while read -r name pid; do
    if kill "$pid" >/dev/null 2>&1; then echo "stopped $name ($pid)"; fi
  done < "$PID_FILE"
  rm -f "$PID_FILE"
fi

# Fallback: kill by pattern in case the pid file is stale
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "stopped stray backend" || true
pkill -f "vite" 2>/dev/null && echo "stopped stray vite" || true
pkill -f "ngrok http 5173" 2>/dev/null && echo "stopped stray ngrok" || true

if [ "${1:-}" = "--db" ]; then
  COMPOSE="$(docker compose version >/dev/null 2>&1 && echo 'docker compose' || echo 'docker-compose')"
  (cd "$ROOT" && $COMPOSE stop db) && echo "stopped db"
fi
echo "done"
