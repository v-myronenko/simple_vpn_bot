def get_text(key, lang):
    from translations import translations
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", ""))