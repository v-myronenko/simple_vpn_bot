from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_text(key, lang="uk"):
    value = translations.get(key, {}).get(lang)
    if value is None:
        print(f"[❌] Переклад для ключа '{key}' мовою '{lang}' відсутній")
    return value or "[translation missing]"


def language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="UA 🇺🇦", callback_data="lang_uk")],
        [InlineKeyboardButton(text="RU 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="EN 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="ES 🇪🇸", callback_data="lang_es")]
    ])

translations = {
    "start_text": {
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
    "change_language_btn": {
        "uk": "🌍 Змінити мову",
        "ru": "🌍 Сменить язык",
        "en": "🌍 Change language",
        "es": "🌍 Cambiar idioma"
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
    "choose_currency": {
        "uk": "Оберіть валюту для оплати. Після успішної оплати доступ буде продовжено на 31 день.",
        "ru": "Выберите валюту для оплаты. После успешной оплаты доступ будет продлён на 31 день.",
        "en": "Choose currency to pay. After successful payment your access will be extended for 31 days.",
        "es": "Elige la moneda para pagar. Después del pago exitoso tu acceso se extenderá por 31 días."
    },
    "my_vpn_btn": {
        "uk": "📦 Мій доступ",
        "ru": "📦 Мой доступ",
        "en": "📦 My VPN",
        "es": "📦 Mi acceso"
    },
    "myvpn_text": {
        "uk": "Ваш доступ активний до <b>{end_date}</b>\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "ru": "Ваш доступ активен до <b>{end_date}</b>\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "en": "Your access is active until <b>{end_date}</b>\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>",
        "es": "Tu acceso está activo hasta <b>{end_date}</b>\n\nUUID: <code>{uuid}</code>\nVmess: <code>{vmess}</code>"
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
    "paysupport_text": {
        "uk": "З питань оплати або донатів — напишіть @SimpleVpnSupport",
        "ru": "По вопросам оплаты или донатов — напишите @SimpleVpnSupport",
        "en": "For billing or donation-related questions, contact @SimpleVpnSupport",
        "es": "Para preguntas sobre pagos o donaciones, contacta a @SimpleVpnSupport"
    },
    "help_text": {
        "uk": "Усі інструкції: {url}\n\nЗавантажте Fair VPN\n👉 https://apps.apple.com/app/fair-vpn/id1533873488\nУ застосунку:\n1. Перейдіть на вкладку “VPN”\n2. Натисніть “Add VPN by Link...”\n3. Вставте vmess-посилання з бота\n4. Збережіть та активуйте з'єднання",
        "ru": "Все инструкции: {url}\n\nСкачайте Fair VPN\n👉 https://apps.apple.com/app/fair-vpn/id1533873488\nВ приложении:\n1. Перейдите во вкладку “VPN”\n2. Нажмите “Add VPN by Link...”\n3. Вставьте ссылку vmess из бота\n4. Сохраните и подключитесь",
        "en": "All instructions: {url}\n\nDownload Fair VPN\n👉 https://apps.apple.com/app/fair-vpn/id1533873488\nIn the app:\n1. Go to “VPN” tab\n2. Tap “Add VPN by Link...”\n3. Paste vmess link from bot\n4. Save and set Status to “Connected”",
        "es": "Todas las instrucciones: {url}\n\nDescarga Fair VPN\n👉 https://apps.apple.com/app/fair-vpn/id1533873488\nEn la aplicación:\n1. Ve a la pestaña “VPN”\n2. Pulsa “Add VPN by Link...”\n3. Pega el enlace vmess del bot\n4. Guarda y conéctate"
    }
    ,
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