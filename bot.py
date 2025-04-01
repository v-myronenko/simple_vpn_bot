import asyncio
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta

import config
import database
import payments

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Запуск БД
database.init_db()


async def check_subscriptions():
    """
    Фонова перевірка кожні ~3600с (1 година).
    Хто прострочив - робимо deactivate_user().
    (Щоб ще й x-ui вимкнути - треба API x-ui, сюди додати виклики).
    """
    while True:
        users = database.get_all_active_users()
        now = datetime.now()
        for u in users:
            end_date = datetime.strptime(u["end_date"], "%Y-%m-%d %H:%M:%S")
            if now > end_date:
                # Термін скінчився, відключаємо
                database.deactivate_user(u["id"])
                # Сповіщаємо користувача
                try:
                    await bot.send_message(
                        u["telegram_id"],
                        "Твій доступ завершився. Для продовження набери /renew"
                    )
                except:
                    pass
                # TODO: виклик API x-ui, щоб видалити/деактивувати реальний акаунт
        await asyncio.sleep(3600)  # 1 година


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    text = (
        "Привіт! Це SVPN Bot\n\n"
        "🔹 /getvpn — отримати VPN доступ на 3 дні\n"
        "🔹 /myvpn — перевірити статус\n"
        "🔹 /renew — продовжити доступ\n"
        "🔹 /help — інструкція"
    )
    await message.answer(text)


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    text = f"Повна інструкція: {config.HELP_URL}\n\nЯкщо є питання, пиши /start"
    await message.answer(text)


@dp.message_handler(commands=["getvpn"])
async def cmd_getvpn(message: types.Message):
    user = database.get_user_by_telegram_id(message.from_user.id)
    if user and user["active"] == 1:
        # Вже активний
        await message.answer("У тебе вже є активний доступ, перевір командою /myvpn")
        return
    # Створюємо нового користувача
    now = datetime.now()
    end = now + timedelta(days=config.FREE_DAYS)
    uuid = generate_uuid()  # Згенерувати UUID
    # ТУТ можна створити акаунт у x-ui. Зараз лишаємо заглушку.

    database.add_user(
        str(message.from_user.id),
        uuid,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )
    # Генеруємо vmess://
    vmess_link = create_vmess_link(uuid)
    await message.answer(
        f"Тримай свій VPN на {config.FREE_DAYS} днів!\n\n"
        f"UUID: <code>{uuid}</code>\n"
        f"Посилання (для клієнта v2ray):\n<code>{vmess_link}</code>\n\n"
        "Починай користуватись!"
    )


@dp.message_handler(commands=["myvpn"])
async def cmd_myvpn(message: types.Message):
    user = database.get_user_by_telegram_id(message.from_user.id)
    if not user or user["active"] == 0:
        await message.answer("У тебе немає активного доступу. Спробуй /getvpn")
        return
    uuid = user["uuid"]
    end_date = user["end_date"]
    vmess_link = create_vmess_link(uuid)
    await message.answer(
        f"Твій доступ дійсний до <b>{end_date}</b>\n\n"
        f"UUID: <code>{uuid}</code>\n\n"
        f"Vmess: <code>{vmess_link}</code>"
    )


@dp.message_handler(commands=["renew"])
async def cmd_renew(message: types.Message):
    # Пропонуємо варіанти оплати TON/USDT
    kb = types.InlineKeyboardMarkup()
    btn_ton = types.InlineKeyboardButton("Оплатити TON", callback_data="pay_ton")
    btn_usdt = types.InlineKeyboardButton("Оплатити USDT", callback_data="pay_usdt")
    kb.add(btn_ton, btn_usdt)
    await message.answer(
        "Оберіть валюту для оплати. Після успішної транзакції ваш доступ "
        f"буде продовжено на {config.PAID_DAYS} днів",
        reply_markup=kb
    )


@dp.callback_query_handler(lambda c: c.data in ["pay_ton", "pay_usdt"])
async def process_payment_callback(call: types.CallbackQuery):
    currency = "TON" if call.data == "pay_ton" else "USDT"
    amount = config.PRICE_TON if currency == "TON" else config.PRICE_USDT
    # Створюємо інвойс
    payload = str(call.from_user.id)  # потім дізнаємось, хто оплатив
    invoice_id, pay_url = payments.create_invoice(currency, amount, payload)
    if not invoice_id:
        await call.message.answer("Помилка при створенні інвойсу 😥 Спробуйте пізніше.")
        return
    # Даємо посилання на оплату
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Перейти до оплати", url=pay_url))
    # Збережемо invoice_id у повідомлення, щоб потім відловити callback
    await call.message.answer(f"Сума: {amount} {currency}\nНатисни кнопку:", reply_markup=kb)


@dp.inline_handler()
async def inline_query(query: types.InlineQuery):
    pass
    # Не використовуємо inline-mode в цьому MVP


# (Для остаточної реалізації callback від CryptoBot треба webhook
# або періодичний check. Спрощено робимо check після натискання "Я оплатив"?)

# Якщо хочемо обробляти callback від CryptoBot офіційно –
# треба мати webhook, де CryptoBot надсилає:
# {
#   "update_id": ...
#   "invoice_payload": "123456789",
#   "invoice_id": ...,
#   "status": "paid"
# }
# і т.д.

# ------------------------------- UTILS --------------------------------#

import uuid


def generate_uuid():
    return str(uuid.uuid4())


def create_vmess_link(u):
    """
    Дуже спрощений приклад. Реально треба вшити JSON у base64.
    Припустимо, це "чистий" vmess://uuid
    """
    return f"vmess://{u}"


# ----------------------------- RUN ------------------------------------#

async def on_startup(_):
    # Запустимо фонову перевірку
    asyncio.create_task(check_subscriptions())


def main():
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()
