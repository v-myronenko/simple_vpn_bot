# database.py
import sqlite3
from datetime import timedelta, datetime
from uuid import uuid4

DB_FILE = "vpn_users.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT NOT NULL,
                uuid TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT NOT NULL,
                txid TEXT NOT NULL,
                confirmed INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def add_user(telegram_id, uuid, start_date, end_date):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (telegram_id, uuid, start_date, end_date, active)
            VALUES (?, ?, ?, ?, 1)
        """, (telegram_id, uuid, start_date, end_date))
        conn.commit()

def extend_subscription(user_id: int, new_end_date: str):
    conn = sqlite3.connect("vpn_users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET end_date = ?, active = 1 WHERE telegram_id = ?", (new_end_date, user_id))
    conn.commit()
    conn.close()

def get_user_by_telegram_id(telegram_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=? AND active=1 ORDER BY id DESC LIMIT 1", (telegram_id,))
        return c.fetchone()

def deactivate_user(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET active=0 WHERE id=?", (user_id,))
        conn.commit()

def get_all_active_users():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE active=1")
        return c.fetchall()

def generate_uuid():
    return str(uuid4())

def create_vmess_link(uuid):
    import base64, json
    config = {
        "v": "2",
        "ps": "svpn-server",
        "add": "68.183.70.136",
        "port": "443",
        "id": uuid,
        "aid": "0",
        "net": "tcp",
        "type": "none",
        "host": "",
        "path": "",
        "tls": ""
    }
    json_str = json.dumps(config, separators=(",", ":"))
    return "vmess://" + base64.b64encode(json_str.encode()).decode()

def add_payment(telegram_id, txid):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO payments (telegram_id, txid) VALUES (?, ?)", (telegram_id, txid))
        conn.commit()

def get_unconfirmed_payments():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM payments WHERE confirmed=0")
        return c.fetchall()

def confirm_payment(telegram_id):
    now = datetime.now()
    end = now + timedelta(days=31)
    uuid = generate_uuid()
    add_user(str(telegram_id), uuid, now.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"))
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE payments SET confirmed=1 WHERE telegram_id=?", (telegram_id,))
        conn.commit()
    return uuid
