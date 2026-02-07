from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.locale_service import LocaleService
from backend_client import backend_client


class I18nMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        lang: str | None = None

        if user:
            tg_id = user.id

            # 1) пробуємо забрати мову з бекенда
            try:
                lang = await backend_client.get_user_language(tg_id)
            except Exception:
                # логіку логування/алерту можна додати пізніше
                lang = None

            # 2) якщо на бекенді нічого немає — падаємо до мови Telegram
            if not lang:
                tg_lang = (user.language_code or "").split("-")[0] if user.language_code else None
                lang = tg_lang

        data["i18n"] = LocaleService(lang)
        return await handler(event, data)
