import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()


@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")


settings = Settings()

if not settings.bot_token:
    raise RuntimeError("BOT_TOKEN is not set in .env")
