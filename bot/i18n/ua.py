from .keys import I18nKey

TRANSLATIONS = {
    I18nKey.START_WELCOME: "Ласкаво просимо до SVPN 👋",
    I18nKey.START_TRIAL_INFO: "Ви отримуєте 3-денну пробну версію після першого використання.",
    I18nKey.BTN_LANGUAGE: "Мова інтерфейсу",
    I18nKey.LANG_SELECT_PROMPT: "Оберіть мову інтерфейсу SVPN:",
    I18nKey.LANG_UPDATED: "Мову змінено. Якщо щось не оновилось — натисни /start.",
    I18nKey.BTN_INSTRUCTION: "📖 Інструкція",
    I18nKey.INSTRUCTION_CHOOSE_DEVICE: "Оберіть ваш пристрій:",

    I18nKey.INSTRUCTION_ANDROID: (
        "📱 <b>Android</b>\n\n"
        "1️⃣ Встановіть VPN-клієнт\n"
        "2️⃣ Імпортуйте конфігурацію\n"
        "3️⃣ Натисніть «Підключитися»"
    ),

    I18nKey.INSTRUCTION_IOS: (
        "🍎 <b>iOS</b>\n\n"
        "1️⃣ Встановіть VPN-клієнт\n"
        "2️⃣ Імпортуйте конфігурацію\n"
        "3️⃣ Натисніть «Connect»"
    ),

    I18nKey.INSTRUCTION_WINDOWS: (
        "💻 <b>Windows</b>\n\n"
        "1️⃣ Завантажте клієнт\n"
        "2️⃣ Імпортуйте конфіг\n"
        "3️⃣ Запустіть VPN"
    ),

    I18nKey.INSTRUCTION_MACOS: (
        "🖥 <b>macOS</b>\n\n"
        "1️⃣ Завантажте клієнт\n"
        "2️⃣ Імпортуйте конфіг\n"
        "3️⃣ Активуйте підключення"
    ),

    I18nKey.START_ACTIVE_SUB: (
        "✅ У тебе є активна підписка.\n\n"
        "Тариф: <b>{plan_name}</b>\n"
        "До: <b>{end_at}</b>\n"
        "Сервер: <b>{server_name} ({server_region})</b>\n\n"
        "Натисни кнопку нижче, щоб отримати / оновити налаштування підключення."
    ),
    I18nKey.START_NO_SUB: (
        "У тебе поки що немає активної підписки на SVPN.\n\n"
        "Натисни кнопку нижче, щоб вибрати тариф і оформити підписку."
    ),

    I18nKey.BTN_GET_VPN: "Отримати VPN",
    I18nKey.BTN_BUY: "Купити підписку",
    I18nKey.BTN_PROFILE: "Мій профіль",
    I18nKey.BTN_SHOW_ACCESS_ACTIVE: "Мій VPN доступ",
    I18nKey.BTN_RENEW: "Продовжити підписку",
    I18nKey.BTN_TRIAL: "Отримати пробний доступ",
    I18nKey.BTN_HELP: "Допомога",

    I18nKey.SUB_EXPIRED: "Термін дії вашої підписки закінчився.",
    I18nKey.ERR_GENERIC: "Щось пішло не так. Спробуйте ще раз.",
    I18nKey.ERR_BACKEND: "Сталася помилка при зверненні до сервера. Спробуйте ще раз пізніше.",

    I18nKey.INVOICE_TITLE: "SVPN — підписка на 30 днів",
    I18nKey.INVOICE_DESCRIPTION: (
        "Доступ до SVPN на 30 днів. Після оплати підписка активується автоматично."
    ),
    I18nKey.PAYMENT_ACTIVATING: "✅ Оплата пройшла! Активую підписку...",
    I18nKey.PAYMENT_BACKEND_FAIL: (
        "⚠️ Оплата пройшла, але не вдалося підтвердити активацію підписки.\n"
        "Напиши в підтримку — ми швидко розберемося."
    ),
    I18nKey.PAYMENT_SUCCESS_WITH_END: (
        "🎉 Підписка активна!\n\n"
        "Дійсна до: <b>{end_at}</b>"
    ),
    I18nKey.PAYMENT_SUCCESS_GENERIC: (
        "🎉 Підписка активована! (Деталі оновляться в /start)"
    ),

    I18nKey.TRIAL_EXPIRED: (
        "Твій пробний доступ уже недоступний.\n\n"
        "Щоб продовжити користування SVPN, оформіть підписку через меню."
    ),
    I18nKey.VPN_FETCH_ERROR: (
        "Не вдалося отримати VPN-налаштування. "
        "Спробуй пізніше або напиши в підтримку."
    ),
    I18nKey.VPN_SETTINGS_TITLE: "<b>Твої налаштування SVPN:</b>",
    I18nKey.VPN_TRIAL_INFO: "Це пробний доступ до: <b>{trial_end_at}</b> (UTC).",

    I18nKey.HELP_TEXT: (
        "Якщо є питання щодо SVPN — напиши адміну: @your_username (замінимо пізніше)."
    ),
}
