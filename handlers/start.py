from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.crud import get_or_create_user
from .account import my_account
from .billing import buy_stars

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_or_create_user(tg_id=u.id, username=u.username)
    kb = [
        [InlineKeyboardButton("Купити підписку ⭐", callback_data="buy_stars")],
        [InlineKeyboardButton("Мій акаунт", callback_data="my_account")]
    ]
    await (update.message or update.callback_query.message).reply_text(
        "Привіт! Це VPN-бот. Обери дію:", reply_markup=InlineKeyboardMarkup(kb)
    )

async def cb_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    if data == "buy_stars":
        await buy_stars(update, context)
    elif data == "my_account":
        await my_account(update, context)
    else:
        await q.answer()
