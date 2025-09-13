from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from db.session_async import get_session
from db.repo import get_or_create_user, grant_trial_if_needed, is_active

# Якщо маєш готові функції для видачі конфіга — розкоментуй:
# from services.wg_manager import ensure_peer_for_user, get_client_config_bytes, get_client_qr_bytes


def _status_text(active: bool, expires_at) -> str:
    if not expires_at:
        return (
            "⛔️ Доступ неактивний.\n"
            "Натисни /buy, щоб оформити підписку, або /myvpn для перегляду статусу."
        )
    if active:
        return f"✅ Доступ активний до: {expires_at:%Y-%m-%d %H:%M UTC}"
    return f"⛔️ Доступ неактивний. Остання підписка закінчилась: {expires_at:%Y-%m-%d %H:%M UTC}"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start:
    - створює користувача (якщо вперше),
    - надає trial 7 днів, якщо підписок раніше не було,
    - показує статус і дату закінчення,
    - (опційно) одразу видає WireGuard-конфіг/QR.
    """
    tg = update.effective_user
    chat = update.effective_chat
    if not tg or not chat:
        return

    # Створення/оновлення користувача + trial при першому старті
    async with await get_session() as session:
        user = await get_or_create_user(session, telegram_id=tg.id, username=tg.username)
        trial = await grant_trial_if_needed(session, user.id, days=7)
        await session.commit()

        active, expires_at = await is_active(session, user.id)

    # Повідомлення користувачу
    if trial:
        text = (
            "🎉 Вітаю! Твій безкоштовний доступ активовано на 7 днів.\n"
            f"Діє до: {trial.expires_at:%Y-%m-%d %H:%M UTC}\n\n"
            "Команди:\n"
            "• /myvpn — статус і отримання конфіга\n"
            "• /buy — купити 1 / 3 / 6 міс. (Stars / crypto)\n"
            "• /howto — інструкція підключення WireGuard"
        )
        await update.message.reply_text(text)

        # (опційно) одразу видати конфіг/QR
        # try:
        #     await ensure_peer_for_user(user_id=user.id)  # створює peer, якщо нема
        #     cfg_bytes = await get_client_config_bytes(user_id=user.id)
        #     qr_bytes = await get_client_qr_bytes(user_id=user.id)
        #     await context.bot.send_document(chat_id=chat.id, filename="svpn.conf", document=cfg_bytes)
        #     await context.bot.send_photo(chat_id=chat.id, photo=qr_bytes)
        # except Exception as e:
        #     await update.message.reply_text(f"⚠️ Не вдалось видати конфіг автоматично: {e}\nСпробуй /myvpn.")

    else:
        await update.message.reply_text(_status_text(active, expires_at) + "\n\nКоманди: /myvpn, /buy, /howto")
