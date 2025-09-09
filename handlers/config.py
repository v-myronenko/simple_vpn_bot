import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes

from db.crud import get_or_create_user
from services.wg_manager import WGManager
from config import settings


def make_wg() -> WGManager:
    """
    Створюємо локальний менеджер WireGuard.
    Параметри читаємо з .env через settings.
    """
    interface = getattr(settings, "WG_INTERFACE", "wg0")
    network_cidr = getattr(settings, "WG_CIDR", "10.8.0.0/24")
    # endpoint для клієнта: або готовий WG_ENDPOINT ("host:port"), або збираємо з WG_HOST + WG_PORT
    endpoint = getattr(settings, "WG_ENDPOINT", None)
    if not endpoint:
        host = getattr(settings, "WG_HOST", None)
        port = getattr(settings, "WG_PORT", 51820)
        if not host:
            raise RuntimeError("Вкажи WG_ENDPOINT або WG_HOST у .env")
        endpoint = f"{host}:{port}"

    return WGManager(interface=interface, network_cidr=network_cidr, endpoint=endpoint)


async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /config — створює peer, відправляє .conf і QR (PNG).
    """
    user = update.effective_user
    get_or_create_user(user.id, user.username)
    peer_name = f"tg_{user.id}"

    try:
        wg = make_wg()
        conf_bytes, png_bytes = wg.create_peer(peer_name)
    except Exception as e:
        # показуємо текст помилки користувачу
        await update.message.reply_text(f"Помилка: {e}")
        return

    # Захист від типів: очікуємо bytes; якщо прийшов str – закодуємо
    if isinstance(conf_bytes, str):
        conf_bytes = conf_bytes.encode("utf-8")
    if png_bytes is not None and isinstance(png_bytes, str):
        png_bytes = png_bytes.encode("utf-8")

    # Відправляємо .conf
    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_bytes), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй його у додаток WireGuard."
    )

    # Відправляємо QR (якщо він згенерувався)
    if png_bytes:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png_bytes), filename=f"{peer_name}.png"),
            caption="Скани цей QR у додатку WireGuard (Android/iOS)."
        )
