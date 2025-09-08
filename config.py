from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vpn.db")

    # WireGuard (використовуЇтьс€ дл€ /config)
    WG_HOST = os.getenv("WG_HOST")
    WG_SSH_USER = os.getenv("WG_SSH_USER", "wgsvc")
    WG_SSH_KEY = os.getenv("WG_SSH_KEY")  # абсолютний шл€х до приватного ключа

    # x-ui Ч неактивно (залишаЇмо на майбутнЇ)
    XUI_URL = os.getenv("XUI_URL")
    XUI_LOGIN = os.getenv("XUI_LOGIN")
    XUI_PASSWORD = os.getenv("XUI_PASSWORD")
    INBOUND_ID = int(os.getenv("INBOUND_ID")) if os.getenv("INBOUND_ID") else None

settings = Settings()
