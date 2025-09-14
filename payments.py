# payments.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

payments_router = Router(name="payments")

def buy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="buy:stars")],
        [InlineKeyboardButton(text="💠 Crypto (USDT)", callback_data="buy:usdt")],
        [InlineKeyboardButton(text="💳 Card (Stripe/LiqPay)", callback_data="buy:card")],
    ])

MENU_TEXT = (
    "💳 <b>Оплата / продовження підписки</b>\n\n"
    "Обери спосіб оплати. Після успіху — підписка автоматично подовжиться на 31 день.\n"
    "Почнемо з Telegram Stars і USDT (як MVP)."
)

@payments_router.message(Command("buy"))
async def cmd_buy(message: types.Message):
    await message.answer(MENU_TEXT, reply_markup=buy_kb())

@payments_router.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: types.CallbackQuery):
    action = call.data.split(":")[1]

    if action == "stars":
        text = (
            "⭐ <b>Telegram Stars</b>\n\n"
            "Готуємо інтеграцію. Тут з’явиться кнопка оплати, а підписка подовжиться на 31 день автоматично."
        )
    elif action == "usdt":
        text = (
            "💠 <b>USDT (MVP)</b>\n\n"
            "Надішли TXID у відповідь на це повідомлення.\n"
            "Після підтвердження — продовжимо доступ на 31 день.\n"
            "Далі додамо автопідтвердження через вебхук."
        )
    elif action == "card":
        text = (
            "💳 <b>Оплата карткою</b>\n\n"
            "Підключимо Stripe/LiqPay після Stars/USDT. Кнопка оплати з’явиться тут."
        )
    else:
        await call.answer("Невідома дія", show_alert=True)
        return

    try:
        await call.message.edit_text(text, reply_markup=buy_kb(), disable_web_page_preview=True)
    except TelegramBadRequest:
        pass
    await call.answer()
