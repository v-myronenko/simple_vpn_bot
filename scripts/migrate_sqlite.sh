#!/usr/bin/env bash
set -Eeuo pipefail

DB="${1:-/home/bot/data/vpn_users.db}"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 is required"; exit 1
fi

echo "Migrating DB at: $DB"

# ensure tables exist (create minimal schema if база пуста)
sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  telegram_id INTEGER NOT NULL UNIQUE,
  username TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);"

sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  starts_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME NOT NULL,
  is_trial INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);"

# users.telegram_id (ідемпотентно)
if ! sqlite3 "$DB" "PRAGMA table_info(users);" | awk -F'|' '{print $2}' | grep -qx telegram_id; then
  sqlite3 "$DB" "ALTER TABLE users ADD COLUMN telegram_id INTEGER;"
  sqlite3 "$DB" "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);"
fi

# subscriptions.is_trial
if ! sqlite3 "$DB" "PRAGMA table_info(subscriptions);" | awk -F'|' '{print $2}' | grep -qx is_trial; then
  sqlite3 "$DB" "ALTER TABLE subscriptions ADD COLUMN is_trial INTEGER NOT NULL DEFAULT 0;"
fi

# subscriptions.created_at
if ! sqlite3 "$DB" "PRAGMA table_info(subscriptions);" | awk -F'|' '{print $2}' | grep -qx created_at; then
  sqlite3 "$DB" "ALTER TABLE subscriptions ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;"
fi

echo "Done."
