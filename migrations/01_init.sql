-- users: один запис на telegram_id
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY,
    telegram_id  INTEGER NOT NULL UNIQUE,
    username     TEXT,
    created_at   TIMESTAMP NOT NULL DEFAULT (datetime('now'))
);

-- subscriptions: історія підписок; остання з найбільшим expires_at є актуальною
CREATE TABLE IF NOT EXISTS subscriptions (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    starts_at    TIMESTAMP NOT NULL,
    expires_at   TIMESTAMP NOT NULL,
    is_trial     INTEGER NOT NULL DEFAULT 0, -- 0/1
    created_at   TIMESTAMP NOT NULL DEFAULT (datetime('now'))
);

-- індекси для швидких перевірок
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_expires_at ON subscriptions(expires_at);
