import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import settings
from backend_client import BackendClient
from keyboards import get_main_menu_keyboard


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


backend_client = BackendClient()


async def cmd_start(message: Message):
    """
    /start:
    - реєструємо / отримуємо користувача через бекенд
    - перевіряємо, чи є активна підписка
    - показуємо відповідне повідомлення + меню
    """
    tg_id = message.from_user.id

    try:
        status = await backend_client.get_subscription_status(telegram_id=tg_id)
    except Exception as e:
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


async def on_callback_placeholder(callback: CallbackQuery):
    """
    Тимчасові заглушки для кнопок.
    Потім сюди підвʼяжемо оплату, видачу доступу і т.д.
    """
    data = callback.data or ""
    if data == "buy_subscription":
        await callback.message.edit_text(
            "Тут буде оформлення підписки через Telegram Stars (ще в розробці)."
        )
    elif data == "renew_subscription":
        await callback.message.edit_text(
            "Тут буде продовження підписки (ще в розробці)."
        )
    elif data == "show_access":
        await callback.message.edit_text(
            "Тут буде показано твої VPN-налаштування (ще в розробці)."
        )
    elif data == "help":
        await callback.message.answer(
            "Якщо є питання щодо SVPN — напиши адміну: @your_username (замінимо пізніше)."
        )

    await callback.answer()


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # хендлер /start
    dp.message.register(cmd_start, CommandStart())

    # заглушки для callback-кнопок
    dp.callback_query.register(on_callback_placeholder, F.data.in_(
        ["buy_subscription", "renew_subscription", "show_access", "help"]
    ))

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
