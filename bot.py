# bot.py
import asyncio
import logging
import os
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from db.models import init_models
from db.repo import get_or_create_user, grant_trial_if_needed, is_active
from howto import howto_router
from myvpn import myvpn_router

logging.basicConfig(level=logging.INFO)

# ------------------------- ENV -------------------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не заданий у .env")

# --------------------- BOT/DP/ROUTER -------------------
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
router = Router(name="root")

# підключаємо модулі
router.include_router(howto_router)
router.include_router(myvpn_router)

# --------------------- HANDLERS ------------------------
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        granted = await grant_trial_if_needed(user_id=user.id)
        if granted:
            await message.answer(
                "👋 Вітаю! Створив акаунт і активував <b>7 днів trial</b>.\n\n"
                "• Статус підписки: /status\n"
                "• Інструкція підключення: /howto\n"
                "• Конфіг і QR: /myvpn"
            )
        else:
            await message.answer(
                "👋 Вітаю з поверненням!\n"
                "• Статус підписки: /status\n"
                "• Інструкція підключення: /howto\n"
                "• Конфіг і QR: /myvpn"
            )
    except Exception as e:
        print(f"[/start] ERROR: {e}")
        await message.answer("⚠️ Помилка при створенні акаунта. Напиши мені лог з консолі — швидко пофіксимо.")

@router.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        active, sub = await is_active(telegram_id=message.from_user.id)
        if not sub:
            await message.answer("У тебе поки немає підписок. Надішли /start, щоб створити акаунт.")
            return

        now = datetime.now(timezone.utc)
        left_days = (sub.expires_at - now).days if sub.expires_at else None
        trial_mark = " (trial)" if getattr(sub, "is_trial", False) else ""

        if active:
            await message.answer(
                f"✅ Підписка активна{trial_mark}\n"
                f"Діє до: <b>{sub.expires_at:%Y-%m-%d %H:%M UTC}</b>\n"
                f"Залишилось: <b>{left_days} дн.</b>"
            )
        else:
            await message.answer(
                f"⛔ Підписка неактивна{trial_mark}\n"
                f"Закінчилась: <b>{sub.expires_at:%Y-%m-%d %H:%M UTC}</b>\n"
                f"Оформи підписку, і я продовжу доступ."
            )
    except Exception as e:
        print(f"[/status] ERROR: {e}")
        await message.answer("⚠️ Не вдалося отримати статус. Скинь, будь ласка, лог із консолі.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступні команди:\n"
        "/start — створити акаунт і отримати trial (1 раз)\n"
        "/status — перевірити стан підписки\n"
        "/howto — інструкція з підключення WireGuard\n"
        "/myvpn — згенерувати конфіг і QR"
    )

# ---------------- BOT MENU (optional) ------------------
async def setup_bot_commands(b: Bot):
    await b.set_my_commands([
        BotCommand(command="start", description="Старт і trial"),
        BotCommand(command="status", description="Статус підписки"),
        BotCommand(command="howto", description="Інструкція підключення"),
        BotCommand(command="myvpn", description="Конфіг і QR"),
        BotCommand(command="help", description="Допомога"),
    ])

# ---------------------- MAIN --------------------------
async def main():
    # 1) створюємо таблиці, якщо їх ще нема
    await init_models()

    # 2) підключаємо кореневий роутер у диспетчер
    dp.include_router(router)

    # 3) команди в меню
    await setup_bot_commands(bot)

    # 4) запускаємо поллінг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
