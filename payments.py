# payments.py
from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from db.repo import get_or_create_user, extend_subscription

payments_router = Router(name="payments")

STARS_PRICE = 500  # amount in smallest units of XTR

async def buy_kb(bot: Bot) -> InlineKeyboardMarkup:
    stars_link = await bot.create_invoice_link(
        title="VPN subscription",
        description="Підписка на 31 день",
        payload="sub_31",
        currency="XTR",
        prices=[types.LabeledPrice(label="31 days", amount=STARS_PRICE)],
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатити Stars", url=stars_link)],
        [InlineKeyboardButton(text="💠 Crypto (USDT)", callback_data="buy:usdt")],
        [InlineKeyboardButton(text="💳 Card (Stripe/LiqPay)", callback_data="buy:card")],
    ])

MENU_TEXT = (
    "💳 <b>Оплата / продовження підписки</b>\n\n"
    "Обери спосіб оплати. Після успіху — підписка автоматично подовжиться на 31 день.\n"
    "Почнемо з Telegram Stars і USDT (як MVP)."
)

@payments_router.message(Command("buy"))
async def cmd_buy(message: types.Message, bot: Bot):
    await message.answer(MENU_TEXT, reply_markup=await buy_kb(bot))

@payments_router.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: types.CallbackQuery, bot: Bot):
    action = call.data.split(":")[1]

    if action == "usdt":
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
        await call.message.edit_text(
            text, reply_markup=await buy_kb(bot), disable_web_page_preview=True
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@payments_router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    await extend_subscription(user.id, days=31)
    await message.answer(
        "Дякуємо за оплату! Підписка подовжена на 31 день."
    )