import asyncio
import logging
from uuid import uuid4

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    LabeledPrice,
)

from config import settings
from backend_client import BackendClient
from keyboards import get_main_menu_keyboard


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

backend_client = BackendClient()

# ✅ MVP: ціна у Stars (ціле число). Винесеш потім у бекенд/плани.
BASIC_30D_STARS_PRICE = 199
PLAN_CODE = "basic_30d"


async def cmd_start(message: Message):
    """
    /start:
    - перевіряємо, чи є активна підписка
    - показуємо відповідне повідомлення + меню
    """
    tg_id = message.from_user.id

    try:
        status = await backend_client.get_subscription_status(telegram_id=tg_id)
    except Exception:
        logger.exception("Error calling backend")
        await message.answer(
            "Сталася помилка при зверненні до сервера. Спробуйте ще раз пізніше."
        )
        return

    has_sub = status.get("has_active_subscription", False)
    sub_info = status.get("subscription")

    if has_sub and sub_info:
        text = (
            "✅ У тебе є активна підписка.\n\n"
            f"Тариф: <b>{sub_info.get('plan_name')}</b>\n"
            f"До: <b>{sub_info.get('end_at')}</b>\n"
            f"Сервер: <b>{sub_info.get('server_name')} ({sub_info.get('server_region')})</b>\n\n"
            "Натисни кнопку нижче, щоб отримати / оновити налаштування підключення."
        )
    else:
        text = (
            "У тебе поки що немає активної підписки на SVPN.\n\n"
            "Натисни кнопку нижче, щоб вибрати тариф і оформити підписку."
        )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(has_active_subscription=has_sub),
        parse_mode="HTML",
    )


async def send_stars_invoice(callback: CallbackQuery, bot: Bot, mode: str):
    """
    mode: 'buy' або 'renew' (для логіки/аналітики, в payload просто позначимо)
    """
    tg_id = callback.from_user.id

    # payload буде потім ключем ідемпотентності на бекенді (можна зберігати)
    payload = f"{mode}:{PLAN_CODE}:{tg_id}:{uuid4()}"

    title = "SVPN — підписка на 30 днів"
    description = "Доступ до SVPN на 30 днів. Після оплати підписка активується автоматично."

    prices = [LabeledPrice(label="SVPN Basic 30 days", amount=BASIC_30D_STARS_PRICE)]

    await callback.answer()  # прибрати "loading" у кнопці

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=title,
        description=description,
        payload=payload,
        currency="XTR",  # ✅ Telegram Stars
        prices=prices,
        start_parameter="svpn-basic-30d",
    )


async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    """
    ✅ ОБОВʼЯЗКОВО: відповісти ok=True, інакше оплата не завершиться
    """
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception:
        logger.exception("Failed to answer pre_checkout_query")


async def on_successful_payment(message: Message):
    """
    Приходить після успішної оплати. Тут викликаємо бекенд, щоб активувати/продовжити підписку.
    """
    sp = message.successful_payment
    tg_id = message.from_u
