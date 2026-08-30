# Deployment (AWS EC2 + Docker + Caddy auto-HTTPS)

Production stack: **PostgreSQL + backend (FastAPI + Telegram bot, webhook) + Caddy** (serves the built
Mini App and terminates HTTPS). HTTPS domain is **`3-227-184-179.sslip.io`** (sslip.io maps it to the
server IP `3.227.184.179` — no domain purchase needed); Caddy obtains a free Let's Encrypt certificate.

## 0. Prerequisites
- EC2 instance reachable at `3.227.184.179`, SSH key `aws-key_kz.pem`.
- **Security group inbound open: 22 (SSH), 80 (HTTP/ACME), 443 (HTTPS).** Ports 80 + 443 are required for
  TLS issuance and for Telegram to reach the Mini App.
- A bot token from BotFather and your numeric Telegram id (for admin).

## 1. Connect
```bash
chmod 600 aws-key_kz.pem
ssh -i aws-key_kz.pem ec2-user@3.227.184.179      # Ubuntu AMI: user is 'ubuntu'
```

## 2. Install Docker (once)
```bash
# Amazon Linux 2023
sudo dnf -y install docker git && sudo systemctl enable --now docker
# Ubuntu:  sudo apt-get update && sudo apt-get -y install docker.io docker-compose-plugin git
sudo usermod -aG docker $USER && newgrp docker
docker compose version || sudo dnf -y install docker-compose-plugin
```

## 3. Get the code
```bash
git clone https://github.com/abayaxmedov/os_truckbot.git
cd os_truckbot
```

## 4. Configure secrets
```bash
cp .env.prod.example .env
nano .env    # set: BOT_TOKEN, TELEGRAM_ADMIN_IDS (your id), strong JWT_SECRET,
             #      strong WEBHOOK_SECRET, strong POSTGRES_PASSWORD. DEV_AUTH_BYPASS=false.
# generate strong secrets:  openssl rand -hex 32
```

## 5. Launch
```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f backend   # watch migrate + seed + start
```
Caddy fetches the TLS certificate automatically on first request (allow ~30s).

## 6. Verify
```bash
curl -I https://3-227-184-179.sslip.io/                       # 200, valid TLS
curl -s https://3-227-184-179.sslip.io/api/v1/brands | head   # 7 brands
```
In Telegram: **@onesystem_demo_bot → 🛒 Marketplace** opens the Mini App over real HTTPS (no ngrok
interstitial), login works, brand + logo show.

## 7. Point the bot at the domain
Set the Web App URL in **BotFather → Bot Settings → Menu Button** to
`https://3-227-184-179.sslip.io`, or set the menu button via the Bot API:
```bash
curl -s -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setChatMenuButton" \
  -H 'Content-Type: application/json' \
  -d '{"menu_button":{"type":"web_app","text":"🛒 Marketplace","web_app":{"url":"https://3-227-184-179.sslip.io"}}}'
```
The backend sets the Telegram **webhook** automatically on start (BOT_MODE=webhook).

## Updating a running deployment
```bash
cd os_truckbot && git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Shared server (host already runs nginx + certbot)

If the host already terminates TLS with nginx (multiple sites), don't bind 80/443 from Docker.
Run only db + backend on localhost and let host nginx serve the Mini App + proxy the API:

```bash
git clone https://github.com/abayaxmedov/os_truckbot.git && cd os_truckbot
cp .env.prod.example .env && nano .env          # real secrets; DEV_AUTH_BYPASS=false

# db + backend (backend published on 127.0.0.1:8001)
docker compose -f docker-compose.server.yml up -d --build

# build the Mini App static (served from miniapp/dist by host nginx)
docker run --rm -v "$PWD/miniapp":/app -w /app node:20-alpine sh -lc "npm ci && npm run build"

# TLS cert (skip if it already exists for the domain):
sudo certbot certonly --nginx -d 3-227-184-179.sslip.io

# install the site
sudo cp deploy/nginx-truckcenter.conf /etc/nginx/sites-available/truckcenter
sudo ln -sf /etc/nginx/sites-available/truckcenter /etc/nginx/sites-enabled/truckcenter
sudo nginx -t && sudo systemctl reload nginx
```

## Notes
- Migrations + seed run automatically on backend start (idempotent). Demo products can be moderated/removed
  from the admin panel.
- `DEV_AUTH_BYPASS=false` in prod → the `?dev_tg=` demo logins are disabled; access is via Telegram only.
- Postgres data lives in the `pgdata` volume; TLS certs in `caddy_data`. Back these up.
- If the IP changes, update the sslip.io hostname everywhere (`.env`, `Caddyfile`, bot menu button).
