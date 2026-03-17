from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from services.locale_service import LocaleService, get_user_lang_override, set_user_lang_override
from backend_client import BackendClient

_backend = BackendClient()


class I18nMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        lang = None

        if user:
            # 1. RAM-кеш
            lang = get_user_lang_override(user.id)

            # 2. БД (один раз, потім кешується в RAM)
            if not lang:
                try:
                    lang = await _backend.get_user_language(user.id)
                    if lang:
                        set_user_lang_override(user.id, lang)  # кешуємо
                except Exception:
                    pass

            # 3. Мова Telegram як фолбек
            if not lang and getattr(user, "language_code", None):
                lang = user.language_code.split("-")[0]

        data["i18n"] = LocaleService(lang)
        return await handler(event, data)