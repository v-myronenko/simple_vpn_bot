# myvpn.py
import base64
import io
import os
from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

import qrcode
from nacl.public import PrivateKey as X25519PrivateKey  # PyNaCl

from wg_integrator import add_peer_and_get_ip

myvpn_router = Router(name="myvpn")

WG_ENDPOINT = os.getenv("WG_ENDPOINT")                 # напр.: "203.0.113.10:51820"
WG_PUBLIC_KEY_SERVER = os.getenv("WG_PUBLIC_KEY_SERVER")  # base64(32 bytes)
WG_DNS = os.getenv("WG_DNS", "1.1.1.1")
WG_ALLOWED_IPS = os.getenv("WG_ALLOWED_IPS", "0.0.0.0, ::/0").replace(" ", "")

def _check_server_env() -> tuple[bool, str]:
    if not WG_ENDPOINT:
        return False, "В .env не задано WG_ENDPOINT (приклад: 203.0.113.10:51820)"
    if not WG_PUBLIC_KEY_SERVER:
        return False, "В .env не задано WG_PUBLIC_KEY_SERVER (потрібен base64 публічний ключ сервера)"
    try:
        raw = base64.b64decode(WG_PUBLIC_KEY_SERVER, validate=True)
        if len(raw) != 32:
            return False, "WG_PUBLIC_KEY_SERVER має бути base64(32 байт)"
    except Exception:
        return False, "WG_PUBLIC_KEY_SERVER не схожий на валідний base64"
    return True, ""

def _gen_keypair() -> tuple[str, str]:
    """
    Повертає (private_b64, public_b64) у форматі WireGuard (X25519, 32 байти, base64).
    """
    priv = X25519PrivateKey.generate()
    pub = priv.public_key
    priv_b64 = base64.b64encode(bytes(priv)).decode()
    pub_b64 = base64.b64encode(bytes(pub)).decode()
    return priv_b64, pub_b64

def _make_client_conf(private_key_b64: str, client_ip_cidr: str) -> str:
    return (
        "[Interface]\n"
        f"PrivateKey = {private_key_b64}\n"
        f"Address = {client_ip_cidr}\n"
        f"DNS = {WG_DNS}\n\n"
        "[Peer]\n"
        f"PublicKey = {WG_PUBLIC_KEY_SERVER}\n"
        f"AllowedIPs = {WG_ALLOWED_IPS}\n"
        f"Endpoint = {WG_ENDPOINT}\n"
        "PersistentKeepalive = 25\n"
    )

def _make_qr_png_bytes(text: str) -> bytes:
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@myvpn_router.message(Command("myvpn"))
async def cmd_myvpn(message: types.Message):
    ok, why = _check_server_env()
    if not ok:
        await message.answer(
            "⚠️ Налаштування сервера WireGuard відсутні або некоректні.\n"
            f"{why}\n\n"
            "Адмін, задай WG_ENDPOINT та WG_PUBLIC_KEY_SERVER у .env і перезапусти бота."
        )
        return

    try:
        # 1) Генеруємо ключі клієнта
        priv_b64, pub_b64 = _gen_keypair()

        # 2) Додаємо peer на сервері та отримуємо виділений IP/32
        client_ip_cidr = add_peer_and_get_ip(pub_b64)  # приклад: "10.7.0.5/32"

        # 3) Формуємо клієнтський конфіг
        conf_text = _make_client_conf(private_key_b64=priv_b64, client_ip_cidr=client_ip_cidr)

        # 4) Видаємо файл і QR
        username = message.from_user.username or f"user{message.from_user.id}"
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        conf_name = f"{username}-vpn-{ts}.conf"
        png_name = f"{username}-vpn-{ts}.png"

        await message.answer_photo(
            BufferedInputFile(_make_qr_png_bytes(conf_text), filename=png_name),
            caption="✅ Готово! Відскануй QR у WireGuard або імпортуй .conf нижче.",
        )
        await message.answer_document(
            BufferedInputFile(conf_text.encode("utf-8"), filename=conf_name)
        )
    except Exception as e:
        print(f"[/myvpn] ERROR: {e}")
        await message.answer("⚠️ Не вдалося згенерувати робочий конфіг. Надішли, будь ласка, лог із консолі.")
