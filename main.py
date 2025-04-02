import asyncio
from datetime import datetime, timedelta

import dp

from aiogram.filters import CommandStart
from translations import get_text, language_kb

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.command import Command, CommandObject

import config
import database
import payments
from xui_api import add_user_to_xui
from translations import get_text

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

def get_lang(user_id):
    user = database.get_user_by_telegram_id(user_id)
    return user["language"] if user and "language" in user else "en"

# ---------------- Команди ------------------ #

async def cmd_start(message: Message):
    lang = get_lang(message.from_user.id)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("get_vpn_btn", lang)),
                KeyboardButton(text=get_text("my_vpn_btn", lang)),
                KeyboardButton(text=get_text("renew_access_btn", lang))
            ],
            [
                KeyboardButton(text=get_text("instructions_btn", lang)),
                KeyboardButton(text=get_text("terms_btn", lang)),
                KeyboardButton(text=get_text("support_btn", lang)),
                KeyboardButton(text=get_text("pay_support_btn", lang))
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder=get_text("choose_action", lang)
    )

    await message.answer(
        get_text("start_text", lang),
        reply_markup=kb
    )

async def cmd_help(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(get_text("help_text", lang).format(config.HELP_URL))

async def cmd_getvpn(message: Message):
    lang = get_lang(message.from_user.id)
    user = database.get_user_by_telegram_id(message.from_user.id)
    if user and user["active"] == 1:
        await message.answer(get_text("already_active", lang))
        return

    now = datetime.now()
    end = now + timedelta(days=config.FREE_DAYS)
    uuid = database.generate_uuid()

    database.add_user(
        str(message.from_user.id),
        uuid,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )

    success = add_user_to_xui(uuid, config.INBOUND_ID)
    if not success:
        await message.answer(get_text("server_error", lang))
        return

    vmess_link = database.create_vmess_link(uuid)
    await message.answer(get_text("vpn_success", lang).format(config.FREE_DAYS, uuid, vmess_link))

async def cmd_myvpn(message: Message):
    lang = get_lang(message.from_user.id)
    user = database.get_user_by_telegram_id(message.from_user.id)
    if not user or user["active"] == 0:
        await message.answer(get_text("no_active_access", lang))
        return

    uuid = user["uuid"]
    end_date = user["end_date"]
    vmess_link = database.create_vmess_link(uuid)
    await message.answer(get_text("myvpn_text", lang).format(end_date, uuid, vmess_link))

async def cmd_renew(message: Message):
    lang = get_lang(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Pay in TON", callback_data="pay_ton"),
            InlineKeyboardButton(text="Pay in USDT", callback_data="pay_usdt")
        ]
    ])
    await message.answer(
        get_text("choose_currency", lang).format(config.PAID_DAYS),
        reply_markup=kb
    )

async def cmd_support(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(get_text("support_text", lang))

async def cmd_terms(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(get_text("terms_text", lang))

async def cmd_paysupport(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(get_text("paysupport_text", lang))

async def cmd_confirm_payment(message: Message, command: CommandObject):
    lang = get_lang(message.from_user.id)
    if message.from_user.id not in config.ADMINS:
        await message.answer(get_text("no_access", lang))
        return

    if not command.args:
        await message.answer(get_text("usage_confirm", lang))
        return

    user_id: int = int(command.args.strip())
    user = database.get_user_by_telegram_id(user_id)
    if not user:
        await message.answer(get_text("user_not_found", lang))
        return

    new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
    database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))
    await message.answer(get_text("user_extended", lang).format(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S")))
    try:
        await bot.send_message(user_id, get_text("user_notify_extended", lang).format(new_end.strftime("%Y-%m-%d %H:%M:%S")))
    except:
        pass

async def cb_pay(call: CallbackQuery):
    lang = get_lang(call.from_user.id)
    currency = "TON" if call.data == "pay_ton" else "USDT"
    amount = config.PRICE_TON if currency == "TON" else config.PRICE_USDT

    payload = str(call.from_user.id)
    invoice_id, pay_url = payments.create_invoice(currency, amount, payload)
    if not invoice_id:
        await call.message.answer(get_text("invoice_error", lang))
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text("go_to_payment", lang), url=pay_url)]
    ])
    await call.message.answer(
        get_text("payment_info", lang).format(amount, currency),
        reply_markup=kb
    )
    await call.answer()

# ---------------------- Callback через кнопки --------------------- #

async def handle_buttons(message: Message):
    lang = get_lang(message.from_user.id)
    text = message.text
    if text == get_text("get_vpn_btn", lang): await cmd_getvpn(message)
    elif text == get_text("my_vpn_btn", lang): await cmd_myvpn(message)
    elif text == get_text("renew_access_btn", lang): await cmd_renew(message)
    elif text == get_text("instructions_btn", lang): await cmd_help(message)
    elif text == get_text("terms_btn", lang): await cmd_terms(message)
    elif text == get_text("support_btn", lang): await cmd_support(message)
    elif text == get_text("pay_support_btn", lang): await cmd_paysupport(message)

# ------------------------- Фонова перевірка ------------------------- #

async def check_subscriptions():
    while True:
        users = database.get_all_active_users()
        now = datetime.now()
        for u in users:
            end_date = datetime.strptime(u["end_date"], "%Y-%m-%d %H:%M:%S")
            if now > end_date:
                database.deactivate_user(u["id"])
                try:
                    await bot.send_message(u["telegram_id"], get_text("expired_access", get_lang(u["telegram_id"])))
                except:
                    pass
        await asyncio.sleep(3600)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = database.get_user_by_telegram_id(message.from_user.id)
    lang = user["language"] if user and user["language"] else "uk"
    await message.answer(get_text("start", lang), reply_markup=language_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    database.set_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(get_text("language_saved", lang))


# ----------------------------- MAIN ------------------------------ #

async def main():
    database.init_db()
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_getvpn, Command("getvpn"))
    dp.message.register(cmd_myvpn, Command("myvpn"))
    dp.message.register(cmd_renew, Command("renew"))
    dp.message.register(cmd_support, Command("support"))
    dp.message.register(cmd_terms, Command("terms"))
    dp.message.register(cmd_paysupport, Command("paysupport"))
    dp.message.register(cmd_confirm_payment, Command("confirm_payment"))

    dp.message.register(handle_buttons, F.text)
    dp.callback_query.register(cb_pay, F.data.in_({"pay_ton", "pay_usdt"}))

    asyncio.create_task(check_subscriptions())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
