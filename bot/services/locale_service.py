from i18n import LANGUAGES, DEFAULT_LANG
from i18n.keys import I18nKey

_user_lang_overrides: dict[int, str] = {}


def set_user_lang_override(telegram_id: int, lang: str) -> None:
    _user_lang_overrides[telegram_id] = lang


def get_user_lang_override(telegram_id: int) -> str | None:
    return _user_lang_overrides.get(telegram_id)

def format_date(date_str: str | None) -> str:
    """
    '2026-04-15T18:30:15.462809' → '15 Apr 2026 18:30 UTC'
    Повертає оригінал якщо не вдалось розпарсити.
    """
    if not date_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%-d %b %Y %H:%M UTC")
    except Exception:
        return date_str

class LocaleService:
    def __init__(self, lang: str | None):
        self.lang = lang if lang in LANGUAGES else DEFAULT_LANG

    def t(self, key: I18nKey, **kwargs) -> str:
        lang_dict = LANGUAGES.get(self.lang, {})
        text = lang_dict.get(key)
        if not text:
            text = LANGUAGES[DEFAULT_LANG].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text