import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from db.crud import get_or_create_user
from config import settings
from services.wg_manager import WGManager

# ініціалізуємо менеджер з правильним endpoint
wg = WGManager(
    interface=settings.WG_INTERFACE,
    network_cidr=settings.WG_NETWORK,
    endpoint_host=settings.WG_ENDPOINT_HOST,  # якщо порожній — менеджер спробує визначити сам
    endpoint_port=settings.WG_ENDPOINT_PORT,
    dns=settings.WG_DNS,
    keepalive=settings.WG_KEEPALIVE,
    mtu=settings.WG_MTU,
)

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(u.id, u.username)
    peer_name = f"tg_{u.id}"

    try:
        conf_bytes, png_bytes = wg.add_peer(peer_name)
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
        return

    await update.message.reply_document(
        document=InputFile(io.BytesIO(conf_bytes), filename=f"{peer_name}.conf"),
        caption="Твій WireGuard конфіг. Імпортуй у додаток WireGuard.",
    )

    if png_bytes:
        await update.message.reply_photo(
            photo=InputFile(io.BytesIO(png_bytes), filename=f"{peer_name}.png"),
            caption="Або відскануй QR у додатку WireGuard.",
        )
