import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from services.wg_manager import WGManager
from db.crud import get_or_create_user
from config import settings

wg = WGManager(interface="wg0", network_cidr="10.8.0.0/24")

def make_wg() -> WGManager:
    if not (settings.WG_HOST and settings.WG_SSH_USER and settings.WG_SSH_KEY):
        # Для локального WGManager це не обовʼязково; залишу перевірку як є, якщо треба — прибери
        pass
    return WGManager(interface="wg0", network_cidr="10.8.0.0/24")

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        wg = make_wg()
        conf_text, png = wg.add_peer(peer_name)

        # ---- ПРИЙМАЄ і str, і bytes ----
        doc_bytes = conf_text if isinstance(conf_text, (bytes, bytearray)) else conf_text.encode("utf-8")

        await update.message.reply_document(
            document=InputFile(io.BytesIO(doc_bytes), filename=f"{peer_name}.conf"),
            caption="Твій WireGuard конфіг. Імпортуй його у додаток WireGuard."
        )

        if png:
            await update.message.reply_photo(
                photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
                caption="Скануй цей QR у додатку WireGuard (Android/iOS)."
            )

    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
