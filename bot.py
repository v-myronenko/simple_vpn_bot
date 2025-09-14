from __future__ import annotations

import asyncio
import logging
import os
from typing import Sequence

from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# Хендлери
from handlers.myvpn import cmd_myvpn

# БД/репозиторій для /start (trial + статус)
from db.session_async import get_session
from db.repo import get_or_create_user, grant_trial_if_needed, is_active

# Якщо є ваш менеджер WireGuard — можна одразу активувати peer при trial/оплаті
# from services.wg_manager import ensure_peer_for_user, get_client_config_qr  # приклад


# -----------------------
# Логування
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
log = logging.getLogger("vpn-bot")


# -----------------------
# Команди
# -----------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start:
    - реєструє користувача,
    - якщо це перший старт — дає trial 7 днів,
    - показує статус і дату закінчення,
    - (опційно) одразу генерує/видає WireGuard-конфіг.
    """
    tg = update.effective_user
    chat = update.effective_chat
    if not chat or not tg:
        return

    async with await get_session() as session:
        user = await get_or_create_user(session, telegram_id=tg.id, username=tg.username)
        trial = await grant_trial_if_needed(session, user.id, days=7)
        await session.commit()

        active, expires_at = await is_active(session, user.id)

    if trial:
        text = (
            "🎉 Вітаю! Твій безкоштовний доступ активовано на 7 днів.\n"
            f"Діє до: {trial.expires_at:%Y-%m-%d %H:%M UTC}\n\n"
            "Натисни /myvpn, щоб переглянути статус або отримати інструкції.\n"
            "Для купівлі підписки: /buy"
        )
        await update.message.reply_text(text)

        # (необов'язково) одразу видати конфіг / QR
        # cfg_text, qr_image_bytes = await ensure_peer_for_user(user_id=user.id)
        # await context.bot.send_document(chat_id=chat.id, filename="svpn.conf", document=cfg_text.encode())
        # await context.bot.send_photo(chat_id=chat.id, photo=qr_image_bytes)

    else:
        msg = "✅ Доступ активний до: {:%Y-%m-%d %H:%M UTC}".format(expires_at) if active else "⛔️ Доступ не активний."
        await update.message.reply_text(msg + "\nДля покупки підписки натисни /buy або дивись інструкції /howto.")


async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заготовка під покупку:
    - Пізніше додамо Telegram Stars інвойс і вибір способу оплати.
    """
    text = (
        "🛒 Оберіть підписку:\n"
        "• 1 місяць\n"
        "• 3 місяці\n"
        "• 6 місяців\n\n"
        "Способи оплати: Telegram Stars або crypto (USDT/TON/USDC).\n"
        "Функціонал оплати додамо на наступному кроці."
    )
    await update.message.reply_text(text)


async def cmd_howto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Коротка інструкція підключення (можна доповнити картинками/посиланнями).
    """
    text = (
        "📘 Як підключитись до SVPN (WireGuard):\n\n"
        "1) Встановіть WireGuard:\n"
        "   • iOS/Android — з App Store / Google Play\n"
        "   • Windows/Mac/Linux — з офіційного сайту WireGuard\n\n"
        "2) Отримайте свій конфіг у боті (QR або .conf) — команда /myvpn.\n"
        "3) Імпортуйте конфіг у застосунок WireGuard та увімкніть тунель.\n\n"
        "Питання? Пишіть у підтримку."
    )
    await update.message.reply_text(text)


# -----------------------
# Побудова Application
# -----------------------
def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()

    # Хендлери
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myvpn", cmd_myvpn))
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(CommandHandler("howto", cmd_howto))

    return app


def main():
    token = os.environ["TELEGRAM_TOKEN"]
    log.info("Starting bot…")
    app = build_app(token)

    # PTB v21: run_polling блокує потік, сам піднімає asyncio-loop
    app.run_polling(
        allowed_updates=None,   # стандартний набір апдейтів
        stop_signals=None       # systemd/kill -15 коректно завершить
    )


if __name__ == "__main__":
    main()
