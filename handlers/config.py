# handlers/config.py
import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes

from services.wg_manager import WGManager
from db.crud import get_or_create_user

# Один інстанс локального менеджера WG (працюємо напряму на цьому ж сервері)
wg = WGManager(interface="wg0", network_cidr="10.8.0.0/24")

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        conf, png = wg.add_peer(peer_name)  # conf -> bytes або str

        # Приводимо до bytes, але НЕ викликаємо .encode(), якщо це вже bytes
        if isinstance(conf, str):
            conf_bytes = conf.encode("utf-8")
        else:
            conf_bytes = conf

        await update.message.reply_document(
            document=InputFile(io.BytesIO(conf_bytes), filename=f"{peer_name}.conf"),
            caption="Твій WireGuard конфіг. Імпортуй у додаток WireGuard."
        )

        if png:  # png вже bytes
            await update.message.reply_photo(
                photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
                caption="Скануй цей QR у додатку WireGuard."
            )

    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
