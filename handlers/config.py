# handlers/config.py
import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from services.wg_manager import WGManager
from db.crud import get_or_create_user

# локальний менеджер без SSH
wg = WGManager(interface="wg0", network_cidr="10.8.0.0/24")

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        # НОВЕ: метод create_peer повертає (текст конфігу, PNG-байти QR)
        conf_text, png = wg.add_peer(peer_name)
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
        return

    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_text.encode("utf-8")), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй його у застосунок WireGuard."
    )
    if png:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
            caption="Або відскануй цей QR у застосунку WireGuard."
        )
