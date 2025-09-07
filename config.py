from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vpn.db")
    XUI_URL = os.getenv("XUI_URL")
    XUI_LOGIN = os.getenv("XUI_LOGIN")
    XUI_PASSWORD = os.getenv("XUI_PASSWORD")
    INBOUND_ID = int(os.getenv("INBOUND_ID", "1"))

settings = Settings()
