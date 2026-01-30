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
    level=logging.DEBUG,  # ставимо DEBUG, щоб бачити максимум
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

backend_client = BackendClient()

# ✅ MVP: ціна у Stars (ціле число). Винесеш потім у бекенд/плани.
BASIC_30D_STARS_PRICE = 1
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
    tg_id = message.from_user.id

    payload = sp.invoice_payload
    currency = sp.currency
    total_amount = sp.total_amount  # для XTR — кількість Stars (ціле число)

    telegram_charge_id = sp.telegram_payment_charge_id
    provider_charge_id = sp.provider_payment_charge_id  # може бути None

    await message.answer("✅ Оплата пройшла! Активую підписку...")

    try:
        result = await backend_client.complete_telegram_stars_payment(
            telegram_id=tg_id,
            payload=payload,
            stars_amount=total_amount,
            currency=currency,
            telegram_payment_charge_id=telegram_charge_id,
            provider_payment_charge_id=provider_charge_id,
        )
    except Exception:
        logger.exception("Backend activation failed after successful payment")
        await message.answer(
            "⚠️ Оплата пройшла, але не вдалося підтвердити активацію підписки.\n"
            "Напиши в підтримку — ми швидко розберемося."
        )
        return

    # Очікуємо, що бекенд поверне end_at (або subscription)
    end_at = result.get("end_at") or result.get("subscription", {}).get("end_at")

    if end_at:
        await message.answer(
            f"🎉 Підписка активна!\n\n"
            f"Дійсна до: <b>{end_at}</b>",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "🎉 Підписка активована! (Деталі оновляться в /start)"
        )


async def on_callback(callback: CallbackQuery, bot: Bot):
    """
    Callback-кнопки меню.
    """
    data = callback.data or ""

    if data == "buy_subscription":
        await send_stars_invoice(callback, bot, mode="buy")

    elif data == "renew_subscription":
        await send_stars_invoice(callback, bot, mode="renew")

    elif data == "show_access":
        await callback.message.edit_text(
            "Тут буде показано твої VPN-налаштування (ще в розробці)."
        )
        await callback.answer()

    elif data == "help":
        await callback.message.answer(
            "Якщо є питання щодо SVPN — напиши адміну: @your_username (замінимо пізніше)."
        )
        await callback.answer()


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # /start
    dp.message.register(cmd_start, CommandStart())

    # callback-кнопки
    dp.callback_query.register(
        on_callback,
        F.data.in_(["buy_subscription", "renew_subscription", "show_access", "help"]),
    )

    # платежі через Telegram Stars
    dp.pre_checkout_query.register(on_pre_checkout_query)
    dp.message.register(on_successful_payment, F.successful_payment)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logger.info("Launching bot via asyncio.run(main())")
        asyncio.run(main())
    except Exception:
        logger.exception("Bot crashed with an unhandled exception")
