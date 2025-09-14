# payments.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payments_router = Router(name="payments")

def buy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="buy:stars")],
        [InlineKeyboardButton(text="💠 Crypto (USDT)", callback_data="buy:usdt")],
        [InlineKeyboardButton(text="💳 Card (Stripe/LiqPay)", callback_data="buy:card")],
        [InlineKeyboardButton(text="⬅️ Назад у меню", callback_data="buy:menu")],
    ])

@payments_router.message(Command("buy"))
async def cmd_buy(message: types.Message):
    text = (
        "💳 <b>Оплата / продовження підписки</b>\n\n"
        "Обери спосіб оплати. Після успіху — підписка автоматично подовжиться на 31 день.\n"
        "Почнемо з Telegram Stars і USDT (як MVP)."
    )
    await message.answer(text, reply_markup=buy_kb())

@payments_router.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: types.CallbackQuery):
    action = call.data.split(":")[1]
    if action == "menu":
        await call.message.edit_text("Меню оплати:", reply_markup=buy_kb())
    elif action == "stars":
        await call.message.edit_text(
            "⭐ <b>Telegram Stars</b>\n\n"
            "Інтегруємо зараз. Після підключення з’явиться кнопка оплати прямо тут, "
            "а продовження буде автоматичним.",
            reply_markup=buy_kb()
        )
    elif action == "usdt":
        await call.message.edit_text(
            "💠 <b>USDT (MVP)</b>\n\n"
            "Тимчасовий варіант: надсилаєш TXID у чат, ми підтверджуємо — і я продовжую доступ на 31 день.\n"
            "Найближчим кроком додамо автопідтвердження через вебхук.",
            reply_markup=buy_kb()
        )
    elif action == "card":
        await call.message.edit_text(
            "💳 <b>Оплата карткою</b>\n\n"
            "Підключимо Stripe/LiqPay після Stars/USDT. Кнопка займеться автоматично.",
            reply_markup=buy_kb()
        )
    await call.answer()
