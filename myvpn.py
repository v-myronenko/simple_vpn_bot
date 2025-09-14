# myvpn.py
import base64
import io
import os
import secrets
from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

import qrcode

myvpn_router = Router(name="myvpn")

# ---- MOCK СЕРВЕРНІ НАЛАШТУВАННЯ (тимчасово) ---------------------------------
WG_ENDPOINT = os.getenv("WG_ENDPOINT", "vpn.example.com:51820")
WG_DNS = os.getenv("WG_DNS", "1.1.1.1")
WG_ALLOWED_IPS = os.getenv("WG_ALLOWED_IPS", "0.0.0.0/0, ::/0")
WG_PUBLIC_KEY_SERVER = os.getenv("WG_PUBLIC_KEY_SERVER", "SERVER_PUBLIC_KEY_BASE64")
WG_PRESHARED_KEY = os.getenv("WG_PSK")  # не обовʼязково

def _gen_wg_key() -> str:
    # валідний за форматом: base64(32 байти)
    return base64.b64encode(secrets.token_bytes(32)).decode()

def _gen_client_config(private_key: str, client_ip: str = "10.7.0.2/32") -> str:
    lines = [
        "[Interface]",
        f"PrivateKey = {private_key}",
        f"Address = {client_ip}",
        f"DNS = {WG_DNS}",
        "",
        "[Peer]",
        f"PublicKey = {WG_PUBLIC_KEY_SERVER}",
        f"AllowedIPs = {WG_ALLOWED_IPS}",
        f"Endpoint = {WG_ENDPOINT}",
        "PersistentKeepalive = 25",
    ]
    if WG_PRESHARED_KEY:
        lines.insert(-1, f"PresharedKey = {WG_PRESHARED_KEY}")
    return "\n".join(lines) + "\n"

def _make_qr_png_bytes(text: str) -> bytes:
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@myvpn_router.message(Command("myvpn"))
async def cmd_myvpn(message: types.Message):
    try:
        private_key = _gen_wg_key()
        conf_text = _gen_client_config(private_key=private_key)

        # Імена файлів
        username = message.from_user.username or f"user{message.from_user.id}"
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        conf_name = f"{username}-vpn-{ts}.conf"
        png_name = f"{username}-vpn-{ts}.png"

        # Готуємо байти (без диску!)
        conf_bytes = conf_text.encode("utf-8")
        png_bytes = _make_qr_png_bytes(conf_text)

        # Надсилаємо QR
        await message.answer_photo(
            BufferedInputFile(png_bytes, filename=png_name),
            caption="Ось твій QR для WireGuard. Можеш також імпортувати .conf:",
        )
        # Надсилаємо .conf
        await message.answer_document(
            BufferedInputFile(conf_bytes, filename=conf_name)
        )
    except Exception as e:
        # Щоб ти бачив у консолі, а користувачу не було тиші
        print(f"[/myvpn] ERROR: {e}")
        await message.answer("⚠️ Сталася помилка при генерації конфігу. Спробуй ще раз або напиши мені лог з консолі.")
