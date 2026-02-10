from i18n import LANGUAGES, DEFAULT_LANG
from i18n.keys import I18nKey

# Пам'ять мови по користувачу всередині процесу бота
_user_lang_overrides: dict[int, str] = {}


def set_user_lang_override(telegram_id: int, lang: str) -> None:
    """
    Зберігаємо обрану мову юзера (тільки в пам'яті поточного процесу).
    """
    _user_lang_overrides[telegram_id] = lang


def get_user_lang_override(telegram_id: int) -> str | None:
    """
    Повертаємо збережену мову юзера, якщо є.
    """
    return _user_lang_overrides.get(telegram_id)


class LocaleService:
    def __init__(self, lang: str | None):
        # якщо мови нема або вона невідома — беремо дефолтну
        self.lang = lang if lang in LANGUAGES else DEFAULT_LANG

    def t(self, key: I18nKey, **kwargs) -> str:
        lang_dict = LANGUAGES.get(self.lang, {})
        text = lang_dict.get(key)

        if not text:
            text = LANGUAGES[DEFAULT_LANG].get(key, key)

        if kwargs:
            text = text.format(**kwargs)

        return text
