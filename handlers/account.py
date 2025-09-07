from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from db.crud import get_active_subscription_by_tg

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    sub = get_active_subscription_by_tg(q.from_user.id)
    if not sub:
        await q.edit_message_text("У тебе немає активної підписки.")
    else:
        days_left = (sub.expires_at - datetime.utcnow()).days
        await q.edit_message_text(f"Підписка активна до: {sub.expires_at:%Y-%m-%d} (залишилось ~{days_left} дн.)")
