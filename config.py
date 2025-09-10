# config.py
import os

def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    try:
        return int(v) if (v and v.strip()) else int(default)
    except (TypeError, ValueError):
        return int(default)

class Settings:
    TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
    WG_INTERFACE     = os.getenv("WG_INTERFACE", "wg0")
    WG_NETWORK       = os.getenv("WG_NETWORK", "10.8.0.0/24")
    WG_ENDPOINT_HOST = os.getenv("WG_ENDPOINT_HOST", "")
    WG_ENDPOINT_PORT = env_int("WG_ENDPOINT_PORT", 51820)
    WG_DNS           = os.getenv("WG_DNS", "1.1.1.1,8.8.8.8")
    WG_KEEPALIVE     = env_int("WG_KEEPALIVE", 25)
    WG_MTU           = env_int("WG_MTU", 1380)
    # ⬇️ ВАЖЛИВО: додали DATABASE_URL
    DATABASE_URL     = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////home/bot/data/vpn_users.db")

settings = Settings()
