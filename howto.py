# howto.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

howto_router = Router(name="howto")

# --- Контент інструкцій -------------------------------------------------------

INTRO = (
    "🛠️ <b>Як підключитись до VPN (WireGuard)</b>\n\n"
    "Обери платформу нижче, я покажу кроки з нуля: встановити застосунок, "
    "імпортувати .conf або відсканувати QR, та перевірити з’єднання.\n\n"
    "Порада: після генерації конфігу в боті командою <code>/myvpn</code> "
    "ти отримаєш файл і QR-код."
)

PLATFORMS = [
    ("Android", "android"),
    ("iOS / iPadOS", "ios"),
    ("Windows", "windows"),
    ("macOS", "macos"),
    ("Linux", "linux"),
]

HOWTO = {
    "android": (
        "📱 <b>Android — WireGuard</b>\n\n"
        "1) Встанови застосунок <b>WireGuard</b> з Google Play.\n"
        "2) У боті виконай <code>/myvpn</code> та отримай свій конфіг (.conf) і QR.\n"
        "3) У WireGuard натисни <i>+</i> → <b>Scan from QR code</b> і наведи камеру на QR, "
        "або <b>Import from file</b> та вибери .conf.\n"
        "4) Увімкни тумблер профілю, дай дозвіл на VPN.\n"
        "5) Перевір: відкрий https://ipinfo.io (має бути інша країна/IP).\n\n"
        "Якщо не підключається: перевір час/дату, режим економії енергії, спробуй мобільний інтернет/іншу Wi-Fi мережу."
    ),
    "ios": (
        "🍎 <b>iOS / iPadOS — WireGuard</b>\n\n"
        "1) Встанови <b>WireGuard</b> з App Store.\n"
        "2) Отримай конфіг через <code>/myvpn</code>.\n"
        "3) У WireGuard: <i>Додати</i> → <b>Scan QR Code</b> (або імпорт .conf із «Файлів»).\n"
        "4) Увімкни тумблер профілю, підтвердь додавання VPN-конфігурації.\n"
        "5) Перевір IP на https://ipinfo.io.\n\n"
        "Проблеми: якщо немає інтернету після підключення — перезапусти тунель, перевір Параметри → VPN → дозволи для WireGuard."
    ),
    "windows": (
        "🪟 <b>Windows — WireGuard</b>\n\n"
        "1) Завантаж інсталятор з https://www.wireguard.com/install/ (Windows) і встанови.\n"
        "2) У боті <code>/myvpn</code> → завантаж .conf на ПК.\n"
        "3) Відкрий WireGuard → <b>Import tunnel(s) from file</b> → обери .conf.\n"
        "4) Натисни <b>Activate</b> для підключення.\n"
        "5) Перевір IP на https://ipinfo.io.\n\n"
        "Якщо не конектиться: перевір час/дату системи, антивірус/фаєрвол (дозволь WireGuard), спробуй іншу мережу (мобільний хот-спот)."
    ),
    "macos": (
        "🖥️ <b>macOS — WireGuard</b>\n\n"
        "1) Встанови застосунок <b>WireGuard</b> з App Store (або з офсайту для macOS).\n"
        "2) Отримай .conf / QR через <code>/myvpn</code>.\n"
        "3) WireGuard → <b>Import tunnel(s) from file</b> або <b>Import tunnel(s) from QR code</b>.\n"
        "4) Увімкни тумблер профілю (може попросити пароль/Touch ID).\n"
        "5) Перевір IP на https://ipinfo.io.\n\n"
        "Порада: якщо після сну Mac немає інтернету, вимкни/ввімкни тунель."
    ),
    "linux": (
        "🐧 <b>Linux — WireGuard</b>\n\n"
        "Варіант A (GUI — NetworkManager):\n"
        "1) Встанови підтримку WireGuard для NetworkManager (залежить від дистро).\n"
        "2) «Налаштування мережі» → VPN → Імпорт з файлу → обери .conf з <code>/myvpn</code>.\n"
        "3) Увімкни VPN-профіль.\n\n"
        "Варіант B (CLI — wg-quick):\n"
        "1) Встанови wireguard-tools (wg/wg-quick).\n"
        "2) Скопіюй .conf до <code>/etc/wireguard/myvpn.conf</code> (права 600).\n"
        "3) Запуск: <code>sudo wg-quick up myvpn</code>\n"
        "4) Зупинка: <code>sudo wg-quick down myvpn</code>\n"
        "5) Перевір IP: <code>curl https://ipinfo.io/ip</code>\n\n"
        "Якщо немає маршрутизації: перевір <code>AllowedIPs</code> (0.0.0.0/0, ::/0) та DNS (наприклад, 1.1.1.1)."
    ),
}

# --- Клавіатури ---------------------------------------------------------------

def menu_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for title, slug in PLATFORMS:
        kb.button(text=title, callback_data=f"howto:platform:{slug}")
    kb.adjust(1, 1)
    return kb.as_markup()

def back_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад до меню", callback_data="howto:menu")
    return kb.as_markup()

# --- Хендлери -----------------------------------------------------------------

@howto_router.message(Command("howto"))
async def cmd_howto(message: types.Message):
    await message.answer(INTRO, reply_markup=menu_kb())

@howto_router.callback_query(F.data == "howto:menu")
async def cb_menu(call: types.CallbackQuery):
    await call.message.edit_text(INTRO, reply_markup=menu_kb())
    await call.answer()

@howto_router.callback_query(F.data.startswith("howto:platform:"))
async def cb_platform(call: types.CallbackQuery):
    slug = call.data.split(":")[-1]
    text = HOWTO.get(slug)
    if not text:
        await call.answer("Невідома платформа", show_alert=True)
        return
    await call.message.edit_text(text, reply_markup=back_kb(), disable_web_page_preview=True)
    await call.answer()
