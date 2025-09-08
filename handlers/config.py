# handlers/config.py
import io
import os

from telegram import Update, InputFile
from telegram.ext import ContextTypes
from services.wg_manage import WGManager
from db.crud import get_or_create_user

# Заповни у .env і прочитай у config.py
# WG_HOST=1.2.3.4
# WG_SSH_USER=wgsvc
# WG_SSH_KEY=/absolute/path/to/id_ed25519
from config import settings

WG_HOST = os.getenv("WG_HOST")
WG_SSH_USER = os.getenv("WG_SSH_USER", "wgsvc")
WG_SSH_KEY = os.getenv("WG_SSH_KEY")  # абсолютний шлях до приватного ключа

wg = WGManager(settings.WG_HOST, settings.WG_SSH_USER, settings.WG_SSH_KEY)

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    dbu = get_or_create_user(u.id, u.username)

    # ім'я для peer: tg_<id>
    peer_name = f"tg_{u.id}"

    try:
        conf_text, png = wg.add_peer(peer_name)
    except Exception as e:
        return await update.message.reply_text(f"Помилка створення конфігу: {e}")

    # відправимо конфіг як файл
    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_text.encode()), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй у додаток WireGuard."
    )

    # якщо є QR — надішлемо
    if png:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
            caption="Сквінь QR у додатку WireGuard (Android/iOS)."
        )
