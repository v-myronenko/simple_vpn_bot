import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from services.wg_manager import WGManager
from db.crud import get_or_create_user
from config import settings

def make_wg() -> WGManager:
    if not (settings.WG_HOST and settings.WG_SSH_USER and settings.WG_SSH_KEY):
        raise RuntimeError("Set WG_HOST, WG_SSH_USER, WG_SSH_KEY in .env")
    return WGManager(settings.WG_HOST, settings.WG_SSH_USER, settings.WG_SSH_KEY)

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        wg = make_wg()
        conf_text, png = wg.add_peer(peer_name)
    except Exception as e:
        return await update.message.reply_text(f"Помилка: {e}")

    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_text.encode()), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй його у додаток WireGuard."
    )
    if png:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png), filename=f"{peer_name}.png"),
            caption="Скани цей QR у додатку WireGuard (Android/iOS)."
        )
