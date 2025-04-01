import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.command import Command, CommandObject

import config
import database
import payments
from xui_api import add_user_to_xui

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

# ---------------- Команди ------------------ #

async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔐 Отримати VPN"),
                KeyboardButton(text="📦 Мій доступ"),
                KeyboardButton(text="🔁 Продовжити доступ")
            ],
            [
                KeyboardButton(text="📘 Інструкція"),
                KeyboardButton(text="📋 Terms"),
                KeyboardButton(text="⚙️ Support"),
                KeyboardButton(text="💸 Pay support")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію нижче 👇"
    )

    await message.answer(
        "Привіт! Це SVPN Bot. Обери опцію нижче:",
        reply_markup=kb
    )

async def cmd_help(message: Message):
    await message.answer(f"""Повна інструкція: {config.HELP_URL}

Коротка інструкція:
1. Завантаж Qv2ray
2. Запусти
3. Натисни Import > From Link > встав Vmess
4. Підключись 😎""")

async def cmd_getvpn(message: Message):
    user = database.get_user_by_telegram_id(message.from_user.id)
    if user and user["active"] == 1:
        await message.answer("У тебе вже є активний доступ. Перевір /myvpn")
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
        await message.answer("⚠️ Не вдалося додати доступ на сервер. Зверніться в підтримку.")
        return

    vmess_link = database.create_vmess_link(uuid)
    await message.answer(
        f"Тримай свій VPN на {config.FREE_DAYS} дні!\n\n"
        f"UUID: <code>{uuid}</code>\n"
        f"Vmess: <code>{vmess_link}</code>"
    )

async def cmd_myvpn(message: Message):
    user = database.get_user_by_telegram_id(message.from_user.id)
    if not user or user["active"] == 0:
        await message.answer("У тебе немає активного доступу. Спробуй /getvpn")
        return

    uuid = user["uuid"]
    end_date = user["end_date"]
    vmess_link = database.create_vmess_link(uuid)
    await message.answer(
        f"Твій доступ дійсний до <b>{end_date}</b>\n\n"
        f"UUID: <code>{uuid}</code>\n"
        f"Vmess: <code>{vmess_link}</code>"
    )

async def cmd_renew(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплатити TON", callback_data="pay_ton"),
            InlineKeyboardButton(text="Оплатити USDT", callback_data="pay_usdt")
        ]
    ])
    await message.answer(
        f"Оберіть валюту для оплати. Після успішної транзакції ваш доступ буде продовжено на {config.PAID_DAYS} днів",
        reply_markup=kb
    )

async def cmd_support(message: Message):
    await message.answer("Підтримка:@SimpleVpnSupport або напишіть сюди для допомоги")

async def cmd_terms(message: Message):
    await message.answer("Terms of service: Ви отримуєте доступ до сервісу як є. Адміністрація не гарантує 100% аптайм і не несе відповідальності за ваш трафік.")

async def cmd_paysupport(message: Message):
    await message.answer("For billing or donation-related questions, contact @SimpleVpnSupport")

async def cmd_confirm_payment(message: Message, command: CommandObject):
    if message.from_user.id not in config.ADMINS:
        await message.answer("⛔ У вас немає доступу до цієї команди.")
        return

    if not command.args:
        await message.answer("Використання: /confirm_payment user_id")
        return

    user_id: int = int(command.args.strip())
    user = database.get_user_by_telegram_id(user_id)
    if not user:
        await message.answer("Користувача не знайдено.")
        return

    new_end = datetime.now() + timedelta(days=config.PAID_DAYS)
    database.extend_subscription(user_id, new_end.strftime("%Y-%m-%d %H:%M:%S"))
    await message.answer(f"✅ Доступ користувачу {user_id} продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        await bot.send_message(user_id, f"✅ Ваш доступ продовжено до {new_end.strftime('%Y-%m-%d %H:%M:%S')}. Дякуємо за оплату!")
    except:
        pass

async def cb_pay(call: CallbackQuery):
    currency = "TON" if call.data == "pay_ton" else "USDT"
    amount = config.PRICE_TON if currency == "TON" else config.PRICE_USDT

    payload = str(call.from_user.id)
    invoice_id, pay_url = payments.create_invoice(currency, amount, payload)
    if not invoice_id:
        await call.message.answer("Помилка при створенні інвойсу")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти до оплати", url=pay_url)]
    ])
    await call.message.answer(
        f"Сума: {amount} {currency}\nНатисни кнопку:",
        reply_markup=kb
    )
    await call.answer()

# ---------------------- Callback через кнопки --------------------- #

async def handle_buttons(message: Message):
    match message.text:
        case "🔐 Отримати VPN": await cmd_getvpn(message)
        case "📦 Мій доступ": await cmd_myvpn(message)
        case "🔁 Продовжити доступ": await cmd_renew(message)
        case "📘 Інструкція": await cmd_help(message)
        case "📋 Terms": await cmd_terms(message)
        case "⚙️ Support": await cmd_support(message)
        case "💸 Pay support": await cmd_paysupport(message)


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
                    await bot.send_message(u["telegram_id"], "Термін дії доступу скінчився. /renew для продовження.")
                except:
                    pass
        await asyncio.sleep(3600)


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

    dp.message.register(handle_buttons, F.text.in_({
        "🔐 Отримати VPN",
        "📦 Мій доступ",
        "🔁 Продовжити доступ",
        "📘 Інструкція",
        "📋 Terms",
        "⚙️ Support",
        "💸 Pay support"
    }))
    dp.callback_query.register(cb_pay, F.data.in_({"pay_ton", "pay_usdt"}))

    asyncio.create_task(check_subscriptions())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
