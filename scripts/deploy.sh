#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/home/bot/apps/simple_vpn_bot"
VENV="$APP_DIR/.venv"
DB="/home/bot/data/vpn_users.db"

cd "$APP_DIR"
echo "[deploy] pulling code…"
git fetch --all
git reset --hard origin/main

echo "[deploy] venv + deps…"
[ -d "$VENV" ] || python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -U pip
pip install -r requirements.txt

echo "[deploy] migrate sqlite…"
bash "$APP_DIR/scripts/migrate_sqlite.sh" "$DB"

echo "[deploy] restart service…"
sudo systemctl restart vpn-bot.service
sleep 1
sudo journalctl -u vpn-bot.service -n 50 --no-pager
