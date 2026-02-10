from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.locale_service import LocaleService, get_user_lang_override


class I18nMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        lang = None

        if user:
            # 1. Пробуємо взяти мову з наших override'ів
            lang = get_user_lang_override(user.id)

            # 2. Якщо override немає — падаємо на мову Telegram
            if not lang and getattr(user, "language_code", None):
                lang = user.language_code.split("-")[0]

        data["i18n"] = LocaleService(lang)
        return await handler(event, data)
