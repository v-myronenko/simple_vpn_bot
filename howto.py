# howto.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

howto_router = Router(name="howto")

INTRO = (
    "🛠️ <b>Як підключитись до VPN (WireGuard)</b>\n\n"
    "Обери платформу нижче: встановлення застосунка, імпорт .conf або QR, перевірка з’єднання.\n\n"
    "Порада: згенеруй конфіг у боті командою <code>/myvpn</code> — отримаєш файл і QR."
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
        "1) Встанови <b>WireGuard</b> з Google Play.\n"
        "2) У боті виконай <code>/myvpn</code> і отримай .conf + QR.\n"
        "3) У WireGuard: + → <b>Scan from QR code</b> або <b>Import from file</b>.\n"
        "4) Увімкни профіль (дозвіл на VPN).\n"
        "5) Перевір IP: https://ipinfo.io\n\n"
        "Якщо не конектиться: час/дата, енергозбереження, інша мережа (мобільний інет/інший Wi-Fi)."
    ),
    "ios": (
        "🍎 <b>iOS / iPadOS — WireGuard</b>\n\n"
        "1) Встанови <b>WireGuard</b> з App Store.\n"
        "2) Отримай конфіг через <code>/myvpn</code>.\n"
        "3) <b>Scan QR Code</b> або імпорт .conf із «Файлів».\n"
        "4) Увімкни тунель (підтверди додавання VPN-профілю).\n"
        "5) Перевір IP: https://ipinfo.io\n\n"
        "Проблеми: перезапусти тунель, перевір Параметри → VPN → дозволи для WireGuard."
    ),
    "windows": (
        "🪟 <b>Windows — WireGuard</b>\n\n"
        "1) Завантаж з https://www.wireguard.com/install/ (Windows) та встанови.\n"
        "2) Збережи .conf із <code>/myvpn</code> на ПК.\n"
        "3) WireGuard → <b>Import tunnel(s) from file</b> → обери .conf.\n"
        "4) Натисни <b>Activate</b>.\n"
        "5) Перевір IP: https://ipinfo.io\n\n"
        "Не конектиться: час/дата, фаєрвол/антивірус (дозволь WireGuard), спробуй іншу мережу."
    ),
    "macos": (
        "🖥️ <b>macOS — WireGuard</b>\n\n"
        "1) Встанови з App Store або офсайту.\n"
        "2) Імпортуй .conf / QR з <code>/myvpn</code>.\n"
        "3) Увімкни тунель (може попросити пароль/Touch ID).\n"
        "4) Перевір IP: https://ipinfo.io\n\n"
        "Після сну немає інтернету? Вимк/увімкни тунель."
    ),
    "linux": (
        "🐧 <b>Linux — WireGuard</b>\n\n"
        "A) GUI (NetworkManager): Імпортуй .conf у «Налаштування мережі» → VPN.\n"
        "B) CLI (wg-quick):\n"
        "   1) Встанови wireguard-tools.\n"
        "   2) /etc/wireguard/myvpn.conf (права 600).\n"
        "   3) Запуск: <code>sudo wg-quick up myvpn</code>\n"
        "      Стоп:   <code>sudo wg-quick down myvpn</code>\n"
        "   4) Перевір: <code>curl https://ipinfo.io/ip</code>\n\n"
        "Немає маршруту? <code>AllowedIPs = 0.0.0.0/0, ::/0</code> і коректний DNS (1.1.1.1)."
    ),
}

def menu_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=title, callback_data=f"howto:platform:{slug}")]
            for title, slug in PLATFORMS]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад до меню", callback_data="howto:menu")
    ]])

@howto_router.message(Command("howto"))
async def cmd_howto(message: types.Message):
    await message.answer(INTRO, reply_markup=menu_kb())

@howto_router.callback_query(F.data == "howto:menu")
async def cb_menu(call: types.CallbackQuery):
    try:
        await call.message.edit_text(INTRO, reply_markup=menu_kb(), disable_web_page_preview=True)
    except TelegramBadRequest:
        pass
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
