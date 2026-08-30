#!/usr/bin/env bash
# Run the whole TruckBot stack locally: PostgreSQL (docker) + backend (FastAPI+bot) + Mini App (Vite).
# Usage:  ./scripts/dev.sh        Stop:  ./scripts/stop.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOG_DIR="$ROOT/.dev-logs"
PID_FILE="$ROOT/.dev-pids"
mkdir -p "$LOG_DIR"
: > "$PID_FILE"

COMPOSE="$(docker compose version >/dev/null 2>&1 && echo 'docker compose' || echo 'docker-compose')"

echo "▶ .env"
[ -f .env ] || cp .env.example .env

echo "▶ PostgreSQL (docker)…"
$COMPOSE up -d db
for i in $(seq 1 30); do
  docker exec truckbot_db pg_isready -U truckbot >/dev/null 2>&1 && break
  sleep 1
done
echo "  db ready"

echo "▶ Backend deps + migrations + seed…"
cd backend
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -c "import fastapi" 2>/dev/null || pip install -q -e ".[dev]"
alembic upgrade head
python -m app.seed.run

echo "▶ Backend (http://localhost:8010)…"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload > "$LOG_DIR/backend.log" 2>&1 &
echo "backend $!" >> "$PID_FILE"
deactivate || true
cd "$ROOT"

echo "▶ Mini App deps…"
cd miniapp
[ -d node_modules ] || npm install
echo "▶ Mini App (http://localhost:5173)…"
nohup npm run dev > "$LOG_DIR/miniapp.log" 2>&1 &
echo "miniapp $!" >> "$PID_FILE"
cd "$ROOT"

# Optional HTTPS tunnel for Telegram (ngrok) — only if installed & authenticated.
TUNNEL=""
if command -v ngrok >/dev/null 2>&1 && ngrok config check >/dev/null 2>&1; then
  echo "▶ ngrok tunnel (Telegram)…"
  pkill -f "ngrok http 5173" 2>/dev/null || true
  sleep 1
  nohup ngrok http 5173 --traffic-policy-file "$ROOT/ngrok.policy.yml" --log stdout --log-format logfmt \
    > "$LOG_DIR/ngrok.log" 2>&1 &
  echo "ngrok $!" >> "$PID_FILE"
  sleep 6
  TUNNEL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['tunnels'][0]['public_url']) if d.get('tunnels') else print('')" 2>/dev/null || echo "")
  BOT_TOKEN=$(grep '^BOT_TOKEN=' "$ROOT/.env" | cut -d= -f2-)
  if [ -n "$TUNNEL" ] && [ -n "$BOT_TOKEN" ]; then
    # Point the bot's menu button at the current tunnel URL.
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setChatMenuButton" \
      -H "Content-Type: application/json" \
      -d "{\"menu_button\":{\"type\":\"web_app\",\"text\":\"🛒 Marketplace\",\"web_app\":{\"url\":\"${TUNNEL}\"}}}" >/dev/null || true
  fi
fi

sleep 2
cat <<EOF

✅ TruckBot is running locally:

   Mini App   →  http://localhost:5173/?dev_tg=100000004   (buyer)
                 http://localhost:5173/?dev_tg=100000002   (seller)
                 http://localhost:5173/?dev_tg=100000001   (admin)
   API / docs →  http://localhost:8010/docs
   Telegram   →  ${TUNNEL:-"(no tunnel — set BOT_TOKEN + ngrok authtoken; see README)"}
   Logs       →  .dev-logs/  (backend / miniapp / ngrok)

   Stop: ./scripts/stop.sh
EOF
