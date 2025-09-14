# bot.py
import asyncio
import logging
import os
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from dotenv import load_dotenv

from db.repo import get_or_create_user, grant_trial_if_needed, is_active
from howto import howto_router  # 👈 Підключаємо роутер /howto

logging.basicConfig(level=logging.INFO)

# --- env ----------------------------------------------------------------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не заданий у .env")

# --- bot/dispatcher/router ----------------------------------------------------
bot = Bot(token=TELEGRAM_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Головний роутер проєкту
router = Router(name="root")
# Під’єднуємо /howto
router.include_router(howto_router)

# --- існуючі команди ----------------------------------------------------------
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await get_or_create_user(telegram_id=message.from_user.id,
                                    username=message.from_user.username)
    # Видати trial, якщо ще не було
    granted = await grant_trial_if_needed(user_id=user.id)
    if granted:
        await message.answer(
            "👋 Вітаю! Створив твій акаунт і активував <b>7 днів trial</b>.\n\n"
            "• Статус підписки: /status\n"
            "• Інструкція підключення: /howto\n"
            "• Конфіг і QR (скоро): /myvpn"
        )
    else:
        await message.answer(
            "👋 Вітаю з поверненням!\n"
            "• Статус підписки: /status\n"
            "• Інструкція підключення: /howto\n"
            "• Конфіг і QR (скоро): /myvpn"
        )

@router.message(Command("status"))
async def cmd_status(message: types.Message):
    active, sub = await is_active(telegram_id=message.from_user.id)
    if not sub:
        await message.answer("У тебе поки немає підписок. Надішли /start, щоб створити акаунт.")
        return

    now = datetime.now(timezone.utc)
    left = (sub.expires_at - now).days if sub.expires_at else None
    trial_mark = " (trial)" if getattr(sub, "is_trial", False) else ""

    if active:
        await message.answer(
            f"✅ Підписка активна{trial_mark}\n"
            f"Діє до: <b>{sub.expires_at:%Y-%m-%d %H:%M UTC}</b>\n"
            f"Залишилось: <b>{left} дн.</b>"
        )
    else:
        await message.answer(
            f"⛔ Підписка неактивна{trial_mark}\n"
            f"Закінчилась: <b>{sub.expires_at:%Y-%m-%d %H:%M UTC}</b>\n"
            f"Онови підписку, і я продовжу доступ."
        )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступні команди:\n"
        "/start — створити акаунт і отримати trial (1 раз)\n"
        "/status — перевірити стан підписки\n"
        "/howto — інструкція з підключення WireGuard\n"
        "/myvpn — (скоро) згенерувати конфіг і QR"
    )

# --- реєстрація команд у меню клієнта ----------------------------------------
async def setup_bot_commands(b: Bot):
    await b.set_my_commands([
        BotCommand(command="start", description="Старт і trial"),
        BotCommand(command="status", description="Статус підписки"),
        BotCommand(command="howto", description="Інструкція підключення"),
        BotCommand(command="help", description="Допомога"),
    ])

# --- запуск -------------------------------------------------------------------
async def main():
    # Підключаємо кореневий роутер у диспетчер
    dp.include_router(router)
    await setup_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
