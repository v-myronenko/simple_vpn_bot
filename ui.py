# ui.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from datetime import datetime, timezone

# викликаємо існуючі хендлери напряму
from myvpn import cmd_myvpn
from howto import cmd_howto
from payments import cmd_buy

# для статусу використаємо репозиторій напряму
from db.repo import is_active

ui_router = Router(name="ui")

# ---- Клавіатура --------------------------------------------------------------
BTN_MYVPN = "🛡️ My VPN"
BTN_STATUS = "📊 Status"
BTN_HOWTO = "🧩 HowTo"
BTN_BUY = "💳 Buy / Extend"

def main_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MYVPN), KeyboardButton(text=BTN_STATUS)],
            [KeyboardButton(text=BTN_HOWTO), KeyboardButton(text=BTN_BUY)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Обери дію…",
    )

# ---- /menu -------------------------------------------------------------------
@ui_router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("Меню дій:", reply_markup=main_reply_kb())

# ---- Обробка натискань на кнопки --------------------------------------------
@ui_router.message(F.text == BTN_MYVPN)
async def on_myvpn_btn(message: types.Message):
    # Викликаємо існуючий хендлер /myvpn
    await cmd_myvpn(message)

@ui_router.message(F.text == BTN_STATUS)
async def on_status_btn(message: types.Message):
    # Повторюємо логіку /status без дублювання коду в bot.py
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
        print(f"[ui.status_btn] ERROR: {e}")
        await message.answer("⚠️ Не вдалося отримати статус. Скинь, будь ласка, лог із консолі.")

@ui_router.message(F.text == BTN_HOWTO)
async def on_howto_btn(message: types.Message):
    # Викликаємо існуючий хендлер /howto
    await cmd_howto(message)

@ui_router.message(F.text == BTN_BUY)
async def on_buy_btn(message: types.Message):
    # Викликаємо існуючий хендлер /buy
    await cmd_buy(message, message.bot)
