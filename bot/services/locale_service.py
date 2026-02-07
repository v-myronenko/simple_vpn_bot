from i18n import LANGUAGES, DEFAULT_LANG
from i18n.keys import I18nKey


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
