from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator
import base64, ipaddress, io, os

import dp
from aiogram import Dispatcher
from nacl.public import PrivateKey
import qrcode
from telegram import InputFile

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from howto import howto_router
from db.models import Base
from db.repo import get_or_create_user, get_active_subscription, grant_trial_if_needed

from dotenv import load_dotenv
load_dotenv()


# ----------- Config -----------

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
RAW_DB_URL = os.environ.get("DATABASE_URL", "sqlite:////home/bot/data/vpn_users.db").strip()

# ensure aiosqlite driver for async SQLAlchemy
if RAW_DB_URL.startswith("sqlite:"):
    # convert sqlite:////path -> sqlite+aiosqlite:////path
    DB_URL = RAW_DB_URL.replace("sqlite:", "sqlite+aiosqlite:", 1)
else:
    DB_URL = RAW_DB_URL  # e.g. postgres+asyncpg://... (не використовуємо зараз)

engine = create_async_engine(DB_URL, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# ----------- Bot Handlers -----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        return
    tg = update.effective_user

    # DB work
    async for session in get_session():
        user = await get_or_create_user(
            session,
            telegram_id=tg.id,
            username=tg.username,
        )
        # видати триал, якщо зовсім порожньо
        trial = await grant_trial_if_needed(session, user.id, days=7)

        sub = await get_active_subscription(session, user.id)

    parts = [f"Привіт, *{tg.first_name or 'користувачу'}*!"]
    if trial:
        until = trial.expires_at.replace(tzinfo=timezone.utc)
        parts.append(f"Тобі нараховано пробний доступ на 7 днів, до *{until:%Y-%m-%d %H:%M UTC}*. Щоб отримати конфіг, надішліть /config")
    if sub:
        until = sub.expires_at.replace(tzinfo=timezone.utc)
        parts.append(f"Поточна підписка активна до *{until:%Y-%m-%d %H:%M UTC}*.")
        parts.append("Надрукуй /myvpn щоб побачити деталі.")
    else:
        parts.append("Поки активної підписки немає. Надрукуй /myvpn.")

    await update.effective_chat.send_message(
        "\n\n".join(parts),
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg = update.effective_user
    if not tg:
        return
    # якщо хочеш — перевір будь-які умови активності/триалу тут

    cfg = build_wg_config(user_id=tg.id)

    # 1) як файл
    cfg_bytes = cfg.encode()
    await update.effective_chat.send_document(
        document=InputFile(io.BytesIO(cfg_bytes), filename="wg-client.conf"),
        caption="Ваш WireGuard конфіг (збережіть як wg-client.conf)"
    )

    # 2) QR
    qr_bytes = config_qr_png_bytes(cfg)
    await update.effective_chat.send_photo(
        photo=InputFile(io.BytesIO(qr_bytes), filename="wg-client-qr.png"),
        caption="QR-код для імпорту в мобільний WireGuard"
    )

async def cmd_myvpn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        return
    tg = update.effective_user

    async for session in get_session():
        user = await get_or_create_user(session, telegram_id=tg.id, username=tg.username)
        sub = await get_active_subscription(session, user.id)

    if not sub:
        await update.effective_chat.send_message(
            "Активної підписки не знайдено. Спробуй /start — воно нарахує пробний період, якщо його ще не було."
        )
        return

    until = sub.expires_at.replace(tzinfo=timezone.utc)
    text_out = (
        "🔐 *Мій VPN*\n\n"
        f"Статус: *активна*\n"
        f"Початок: {sub.starts_at:%Y-%m-%d %H:%M UTC}\n"
        f"Закінчення: *{until:%Y-%m-%d %H:%M UTC}*\n"
        f"Тріал: {'так' if sub.is_trial else 'ні'}"
    )
    await update.effective_chat.send_message(text_out, parse_mode=ParseMode.MARKDOWN)

    dp = Dispatcher()
    dp.include_router(howto_router)

# ---- helpers for WG ----
def _gen_wg_keypair():
    sk = PrivateKey.generate()
    priv_b64 = base64.b64encode(bytes(sk)).decode()
    pub_b64  = base64.b64encode(bytes(sk.public_key)).decode()
    return priv_b64, pub_b64

def _pick_client_ip(user_id: int, cidr: str = None) -> str:
    # детерміновано, без БД: 10.8.0.(100 + user_id % 1000)
    net = ipaddress.ip_network(os.getenv("WG_NETWORK", "10.8.0.0/24"))
    host_octet = 100 + (user_id % (net.num_addresses - 200))
    ip = ipaddress.ip_address(int(net.network_address) + host_octet)
    return f"{ip}/32"

def build_wg_config(user_id: int):
    client_priv, client_pub = _gen_wg_keypair()
    address = _pick_client_ip(user_id, os.getenv("WG_NETWORK", "10.8.0.0/24"))

    server_pub = os.getenv("WG_PUBLIC_KEY", "").strip()
    endpoint   = f'{os.getenv("WG_ENDPOINT_HOST","127.0.0.1")}:{os.getenv("WG_ENDPOINT_PORT","51820")}'
    dns        = os.getenv("WG_DNS", "1.1.1.1,8.8.8.8")
    mtu        = os.getenv("WG_MTU", "1280")
    keepalive  = os.getenv("WG_KEEPALIVE", "25")

    if not server_pub:
        # для локального демо можна поставити плейсхолдер, але краще заповнити в .env
        server_pub = "SERVER_PUBLIC_KEY_REQUIRED"

    cfg = f"""[Interface]
PrivateKey = {client_priv}
Address = {address}
DNS = {dns}
MTU = {mtu}

[Peer]
PublicKey = {server_pub}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {endpoint}
PersistentKeepalive = {keepalive}
"""
    return cfg

def config_qr_png_bytes(config_text: str) -> bytes:
    # QR з повним конфігом — WireGuard for iOS/Android читає з QR
    img = qrcode.make(config_text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ----------- App Bootstrap -----------

async def prepare_db() -> None:
    # створити таблиці, якщо їх ще немає (не трогає існуючі)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # невеличка перевірка доступності
        await conn.execute(text("SELECT 1"))


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is empty. Set it in environment.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myvpn", cmd_myvpn))
    app.add_handler(CommandHandler("config", cmd_config))

    async def run():
        await prepare_db()
        print("Bot is starting…")
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        try:
            await asyncio.Event().wait()
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    asyncio.run(run())


if __name__ == "__main__":
    main()
