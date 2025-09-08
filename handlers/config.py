# handlers/config.py
import io
import os

from telegram import Update, InputFile
from dotenv import load_dotenv
from telegram.ext import ContextTypes
from services.wg_manage import WGManager
from db.crud import get_or_create_user
from config import settings

# Заповни у .env і прочитай у config.py
# WG_HOST=1.2.3.4
# WG_SSH_USER=wgsvc
# WG_SSH_KEY=/absolute/path/to/id_ed25519
from config import settings

load_dotenv()

WG_HOST = os.getenv("WG_HOST")
WG_SSH_USER = os.getenv("WG_SSH_USER", "wgsvc")
WG_SSH_KEY = os.getenv("WG_SSH_KEY")  # абсолютний шлях до приватного ключа

wg = WGManager(settings.WG_HOST, settings.WG_SSH_USER, settings.WG_SSH_KEY)

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vpn.db")
    XUI_URL = os.getenv("XUI_URL")
    XUI_LOGIN = os.getenv("XUI_LOGIN")
    XUI_PASSWORD = os.getenv("XUI_PASSWORD")
    INBOUND_ID = int(os.getenv("INBOUND_ID", "1"))

    # >>> ДОДАЙ ОЦЕ <<<
    WG_HOST = os.getenv("WG_HOST")            # IP або домен VPS
    WG_SSH_USER = os.getenv("WG_SSH_USER")    # за гідом ми створили wgsvc
    WG_SSH_KEY = os.getenv("WG_SSH_KEY")      # абсолютний шлях до приватного ключа (id_rsa або id_ed25519)

settings = Settings()

def make_wg():
    if not (settings.WG_HOST and settings.WG_SSH_USER and settings.WG_SSH_KEY):
        raise RuntimeError("WG env missing: set WG_HOST, WG_SSH_USER, WG_SSH_KEY in .env")
    return WGManager(settings.WG_HOST, settings.WG_SSH_USER, settings.WG_SSH_KEY)

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        wg = make_wg()
    except Exception as e:
        return await update.message.reply_text(f"Конфіг не готовий: {e}")

    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        conf_text, png = wg.add_peer(peer_name)
    except Exception as e:
        return await update.message.reply_text(f"Помилка створення конфігу: {e}")

    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_text.encode()), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй у додаток WireGuard."
    )
    if png:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
            caption="Сквінь QR у додатку WireGuard (Android/iOS)."
        )
