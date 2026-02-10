# bot/bot.py
from middlewares.i18n import I18nMiddleware
from i18n.keys import I18nKey
from keyboards import get_main_menu_keyboard, get_language_keyboard
from services.locale_service import LocaleService, set_user_lang_override
from backend_client import BackendTrialError
from aiogram.exceptions import TelegramForbiddenError

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
from keyboards import get_main_menu_keyboard

from backend_client import BackendClient, BackendTrialError
import base64
from aiogram.types import BufferedInputFile



logging.basicConfig(
    level=logging.DEBUG,  # ставимо DEBUG, щоб бачити максимум
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

backend_client = BackendClient()

# ✅ MVP: ціна у Stars (ціле число). Винесеш потім у бекенд/плани.
BASIC_30D_STARS_PRICE = 1
PLAN_CODE = "basic_30d"


dp = Dispatcher()

async def cmd_start(message: Message, i18n):
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
            i18n.t(I18nKey.ERR_BACKEND)
        )
        return

    has_sub = status.get("has_active_subscription", False)
    sub_info = status.get("subscription")

    if has_sub and sub_info:
        text = i18n.t(
            I18nKey.START_ACTIVE_SUB,
            plan_name=sub_info.get("plan_name"),
            end_at=sub_info.get("end_at"),
            server_name=sub_info.get("server_name"),
            server_region=sub_info.get("server_region"),
        )
    else:
        text = i18n.t(I18nKey.START_NO_SUB)

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(
            has_active_subscription=has_sub,
            i18n=i18n,
        ),
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


async def on_successful_payment(message: Message, i18n):
    """
    Приходить після успішної оплати.
    """
    sp = message.successful_payment
    tg_id = message.from_user.id

    payload = sp.invoice_payload
    currency = sp.currency
    total_amount = sp.total_amount

    telegram_charge_id = sp.telegram_payment_charge_id
    provider_charge_id = sp.provider_payment_charge_id  # може бути None

    await message.answer(i18n.t(I18nKey.PAYMENT_ACTIVATING))

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
            i18n.t(I18nKey.PAYMENT_BACKEND_FAIL)
        )
        return

    end_at = result.get("end_at") or result.get("subscription", {}).get("end_at")

    if end_at:
        await message.answer(
            i18n.t(I18nKey.PAYMENT_SUCCESS_WITH_END, end_at=end_at),
            parse_mode="HTML",
        )
    else:
        await message.answer(i18n.t(I18nKey.PAYMENT_SUCCESS_GENERIC))


async def on_callback(callback: CallbackQuery, bot: Bot, i18n):
    data = callback.data or ""
    tg_id = callback.from_user.id

    if data == "buy_subscription":
        await send_stars_invoice(callback, bot, mode="buy")

    elif data == "renew_subscription":
        await send_stars_invoice(callback, bot, mode="renew")

    elif data == "show_access":
        await callback.answer()

        try:
            vpn_info = await backend_client.get_vpn_config(tg_id)
        except BackendTrialError:
            await callback.message.answer(i18n.t(I18nKey.TRIAL_EXPIRED))
            return
        except Exception:
            await callback.message.answer(i18n.t(I18nKey.VPN_FETCH_ERROR))
            return

        vless_url = vpn_info["vless_url"]
        is_trial = vpn_info.get("is_trial", False)
        trial_end_at = vpn_info.get("trial_end_at")
        qr_b64 = vpn_info.get("qr_png_base64")

        lines = [
            i18n.t(I18nKey.VPN_SETTINGS_TITLE),
            "",
            f"<code>{vless_url}</code>",
        ]

        if is_trial and trial_end_at:
            lines.append("")
            lines.append(
                i18n.t(I18nKey.VPN_TRIAL_INFO, trial_end_at=trial_end_at)
            )

        text = "\n".join(lines)

        if qr_b64:
            png_bytes = base64.b64decode(qr_b64)
            photo = BufferedInputFile(png_bytes, filename="svpn_qr.png")
            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode="HTML",
            )
        else:
            await callback.message.answer(text, parse_mode="HTML")

    elif data == "help":
        await callback.message.answer(i18n.t(I18nKey.HELP_TEXT))
        await callback.answer()

    elif data == "language":
        # показуємо список мов
        await callback.message.answer(
            i18n.t(I18nKey.LANG_SELECT_PROMPT),
            reply_markup=get_language_keyboard(),
        )
        await callback.answer()


    elif data.startswith("set_lang:"):
        # парсимо код мови
        _, lang_code = data.split(":", 1)
        lang_code = lang_code.strip()

        # зберігаємо обрану мову локально (в процесі бота)
        set_user_lang_override(tg_id, lang_code)

        # робимо локальний i18n з новою мовою, щоб відповідь вже була на ній
        new_i18n = LocaleService(lang_code)
        await callback.message.answer(new_i18n.t(I18nKey.LANG_UPDATED))
        await callback.answer()


async def main():
    bot = Bot(token=settings.bot_token)

    # i18n для всіх апдейтів
    dp.update.middleware(I18nMiddleware())

    # /start
    dp.message.register(cmd_start, CommandStart())

    # callback-кнопки
    dp.callback_query.register(on_callback)

    # платежі через Telegram Stars
    dp.pre_checkout_query.register(on_pre_checkout_query)
    dp.message.register(on_successful_payment, F.successful_payment)

    logger.info("Bot starting...")
    await dp.start_polling(bot)

@dp.errors()
async def errors_handler(exception):
    # Якщо юзер заблокував бота — просто ігноруємо
    if isinstance(exception, TelegramForbiddenError):
        # можна залогувати на debug, якщо хочеш
        return True  # сигнал aiogram: "помилка оброблена"

    # всі інші помилки нехай летять далі (щоб ми їх бачили)
    return False

if __name__ == "__main__":
    try:
        logger.info("Launching bot via asyncio.run(main())")
        asyncio.run(main())
    except Exception:
        logger.exception("Bot crashed with an unhandled exception")
