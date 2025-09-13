from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from db.session_async import get_session
from db.repo import get_or_create_user, is_active


def _fmt_status(active: bool, expires_at) -> str:
    if not expires_at:
        return "Статус: неактивний.\nНатисни /start, щоб активувати безкоштовний 7-денний доступ."
    if active:
        return f"✅ Статус: активний\nДоступ діє до: {expires_at:%Y-%m-%d %H:%M UTC}"
    else:
        return f"⛔️ Статус: неактивний\nОстання підписка закінчилась: {expires_at:%Y-%m-%d %H:%M UTC}"


async def cmd_myvpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показує поточний статус підписки користувача:
    - активна/неактивна
    - дата закінчення доступу (UTC)
    """
    tg = update.effective_user

    async with await get_session() as session:
        user = await get_or_create_user(session, telegram_id=tg.id, username=tg.username)
        active, expires_at = await is_active(session, user.id)

    text = _fmt_status(active, expires_at)
    text += "\n\nℹ️ Команди:\n" \
            "• /start — отримати/поновити доступ (trial для нових)\n" \
            "• /buy — купити 1 / 3 / 6 міс. (Stars / crypto)\n" \
            "• /howto — інструкція підключення WireGuard"

    await update.message.reply_text(text)
