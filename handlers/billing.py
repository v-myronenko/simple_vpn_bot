from telegram import Update
from telegram.ext import ContextTypes
from db.crud import get_or_create_user, create_payment

async def buy_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user = get_or_create_user(q.from_user.id, q.from_user.username)
    payment = create_payment(user_id=user.id, provider="stars", amount=100)
    await q.edit_message_text(
        "Оплата через Stars поки заглушка.\n"
        "Після інтеграції натискання кнопки тут відкриватиме інвойс, а після оплати — активується підписка."
    )
