translations = {
    "start": {
        "uk": "Привіт 👋 Ласкаво просимо до VPN сервісу!",
        "ru": "Привет 👋 Добро пожаловать в VPN сервис!",
        "en": "Hello 👋 Welcome to the VPN service!",
        "es": "Hola 👋 ¡Bienvenido al servicio VPN!"
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
        "es": "🌍 ¡Idioma guardado!"
    }
}

# database.py — додай нову колонку, якщо ще не існує
import sqlite3

def ensure_language_column():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uk'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # already exists
    conn.close()

ensure_language_column()

# main.py — приклад оновлення /start і вибору мови
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_text

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = database.get_user_by_telegram_id(user_id)
    lang = user["language"] if user else "uk"

    await message.answer(
        get_text("start", lang),
        reply_markup=language_kb()
    )

def language_kb():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("UA 🇺🇦", callback_data="lang_uk"),
        InlineKeyboardButton("RU 🇷🇺", callback_data="lang_ru"),
        InlineKeyboardButton("EN 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("ES 🇪🇸", callback_data="lang_es")
    )
    return kb

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: CallbackQuery):
    lang = callback_query.data.split("_")[1]
    database.set_user_language(callback_query.from_user.id, lang)
    await callback_query.message.edit_text(get_text("language_saved", lang))

# database.py — додай:
def set_user_language(user_id, lang):
    conn = sqlite3.connect("/opt/vpn_data/vpn_users.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, user_id))
    conn.commit()
    conn.close()
