from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_text(key, lang="uk"):
    return translations.get(key, {}).get(lang, "")

def language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="UA 🇺🇦", callback_data="lang_uk")],
        [InlineKeyboardButton(text="RU 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="EN 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="ES 🇪🇸", callback_data="lang_es")]
    ])

translations = {
    "start": {
        "uk": "👋 Привіт! Ласкаво просимо до VPN сервісу!",
        "ru": "👋 Привет! Добро пожаловать в VPN сервис!",
        "en": "👋 Hello! Welcome to the VPN service!",
        "es": "👋 Hola! Bienvenido al servicio de VPN!"
    },
    "choose_language": {
        "uk": "Оберіть мову 🌍",
        "ru": "Выберите язык 🌍",
        "en": "Choose your language 🌍",
        "es": "Elige tu idioma 🌍"
    },
    "language_saved": {
        "uk": "🌍 Мову збережено!",
        "ru": "🌍 Язык сохранен!",
        "en": "🌍 Language saved!",
        "es": "🌍 Idioma guardado!"
    },

    # Кнопки головного меню
    "get_vpn_btn": {
        "uk": "🔐 Отримати VPN",
        "ru": "🔐 Получить VPN",
        "en": "🔐 Get VPN",
        "es": "🔐 Obtener VPN"
    },
    "my_vpn_btn": {
        "uk": "📦 Мій доступ",
        "ru": "📦 Мой доступ",
        "en": "📦 My VPN",
        "es": "📦 Mi acceso"
    },
    "renew_access_btn": {
        "uk": "🔁 Продовжити доступ",
        "ru": "🔁 Продлить доступ",
        "en": "🔁 Renew access",
        "es": "🔁 Renovar acceso"
    },
    "instructions_btn": {
        "uk": "📘 Інструкція",
        "ru": "📘 Инструкция",
        "en": "📘 Instructions",
        "es": "📘 Instrucciones"
    },
    "terms_btn": {
        "uk": "📋 Умови",
        "ru": "📋 Условия",
        "en": "📋 Terms",
        "es": "📋 Términos"
    },
    "support_btn": {
        "uk": "⚙️ Підтримка",
        "ru": "⚙️ Поддержка",
        "en": "⚙️ Support",
        "es": "⚙️ Soporte"
    },
    "pay_support_btn": {
        "uk": "💸 Підтримати проєкт",
        "ru": "💸 Поддержать проект",
        "en": "💸 Pay support",
        "es": "💸 Apoyar el proyecto"
    },
    "choose_action": {
        "uk": "Оберіть дію нижче 👇",
        "ru": "Выберите действие ниже 👇",
        "en": "Choose action below 👇",
        "es": "Elige una opción abajo 👇"
    },

    # Інші повідомлення
    "help_text": {
        "uk": "Вся інструкція: {url}\n\n1. Завантаж Fair VPN\n2. Додай посилання з бота\n3. Підключись!",
        "ru": "Вся инструкция: {url}\n\n1. Скачай Fair VPN\n2. Добавь ссылку из бота\n3. Подключись!",
        "en": "Full guide: {url}\n\n1. Download Fair VPN\n2. Add link from bot\n3. Connect!",
        "es": "Guía completa: {url}\n\n1. Descarga Fair VPN\n2. Agrega el enlace\n3. ¡Conéctate!"
    },
    "already_active": {
        "uk": "У вас вже є активний доступ. Перевірте його через /myvpn",
        "ru": "У вас уже есть активный доступ. Проверьте через /myvpn",
        "en": "You already have active access. Check it via /myvpn",
        "es": "Ya tienes acceso activo. Verifícalo con /myvpn"
    },
    "server_error": {
        "uk": "⚠️ Не вдалося отримати доступ до сервера. Спробуйте пізніше або зверніться в підтримку.",
        "ru": "⚠️ Не удалось подключиться к серверу. Попробуйте позже или напишите в поддержку.",
        "en": "⚠️ Couldn't get access to server. Try later or contact support.",
        "es": "⚠️ No se pudo conectar al servidor. Intenta más tarde o contacta soporte."
    },
    "vpn_success": {
        "uk": "Ось ваш VPN на {days} днів!\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "ru": "Вот ваш VPN на {days} дней!\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "en": "Here is your VPN for {days} days!\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "es": "¡Aquí está tu VPN por {days} días!\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>"
    },
    "terms_text": {
        "uk": "Умови використання: Ви отримуєте доступ до сервісу як є. Адміністрація не гарантує 100% безперервну роботу та не несе відповідальності за ваш трафік.",
        "ru": "Условия использования: Вы получаете доступ к сервису как есть. Администрация не гарантирует 100% аптайм и не несёт ответственности за ваш трафик.",
        "en": "Terms of service: You get access to the service as is. The administration does not guarantee 100% uptime and is not responsible for your traffic.",
        "es": "Términos del servicio: Usted accede al servicio tal cual. La administración no garantiza una disponibilidad del 100% y no se hace responsable de su tráfico."
    },
    "support_text": {
        "uk": "Підтримка: зв'яжіться з @SimpleVpnSupport",
        "ru": "Поддержка: свяжитесь с @SimpleVpnSupport",
        "en": "Support: contact @SimpleVpnSupport",
        "es": "Soporte: contacte con @SimpleVpnSupport"
    },
    "user_extended": {
        "uk": "✅ Доступ користувача продовжено до {date}",
        "ru": "✅ Доступ пользователя продлён до {date}",
        "en": "✅ User access extended until {date}",
        "es": "✅ Acceso del usuario extendido hasta {date}"
    },
    "user_notify_extended": {
        "uk": "✅ Ваш доступ продовжено до {date}. Дякуємо за оплату!",
        "ru": "✅ Ваш доступ продлён до {date}. Спасибо за оплату!",
        "en": "✅ Your access has been extended to {date}. Thank you for your payment!",
        "es": "✅ Su acceso ha sido extendido hasta {date}. ¡Gracias por su pago!"
    },
    "no_access": {
        "uk": "⛔ У вас немає доступу до цієї команди.",
        "ru": "⛔ У вас нет доступа к этой команде.",
        "en": "⛔ You do not have access to this command.",
        "es": "⛔ No tienes acceso a este comando."
    },
    "user_not_found": {
        "uk": "Користувача не знайдено.",
        "ru": "Пользователь не найден.",
        "en": "User not found.",
        "es": "Usuario no encontrado."
    },
    "usage_confirm": {
        "uk": "Використання: /confirm_payment user_id",
        "ru": "Использование: /confirm_payment user_id",
        "en": "Usage: /confirm_payment user_id",
        "es": "Uso: /confirm_payment user_id"
    }
}