import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    # WG
    WG_INTERFACE: str = os.getenv("WG_INTERFACE", "wg0")
    WG_NETWORK: str = os.getenv("WG_NETWORK", "10.8.0.0/24")
    WG_ENDPOINT_HOST: str = os.getenv("WG_ENDPOINT_HOST", "").strip()  # РЕКОМЕНДОВАНО задати явно
    WG_ENDPOINT_PORT: int = int(os.getenv("WG_ENDPOINT_PORT", "51820"))
    WG_DNS: str = os.getenv("WG_DNS", "1.1.1.1")
    WG_KEEPALIVE: int = int(os.getenv("WG_KEEPALIVE", "25"))
    WG_MTU: int = int(os.getenv("WG_MTU", "1280"))

settings = Settings()

if not settings.TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set in .env")
