# myvpn.py
import base64
import io
import os
import re
from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

import qrcode
from nacl.public import PrivateKey as X25519PrivateKey  # PyNaCl

from wg_integrator import add_peer_and_get_ip

myvpn_router = Router(name="myvpn")


def _get_wg_env():
    return {
        "ENDPOINT": os.getenv("WG_ENDPOINT"),
        "SERVER_PUB": os.getenv("WG_PUBLIC_KEY_SERVER"),
        "DNS": os.getenv("WG_DNS", "1.1.1.1"),
        "ALLOWED": os.getenv("WG_ALLOWED_IPS", "0.0.0.0/0, ::/0").replace(" ", ""),
    }


def _validate_server_env() -> tuple[bool, str, dict]:
    cfg = _get_wg_env()
    if not cfg["ENDPOINT"]:
        return False, "В .env не задано WG_ENDPOINT (приклад: 203.0.113.10:51820)", cfg
    if not cfg["SERVER_PUB"]:
        return False, "В .env не задано WG_PUBLIC_KEY_SERVER (base64(32 байт))", cfg
    try:
        raw = base64.b64decode(cfg["SERVER_PUB"], validate=True)
        if len(raw) != 32:
            return False, "WG_PUBLIC_KEY_SERVER має бути base64(32 байт)", cfg
    except Exception:
        return False, "WG_PUBLIC_KEY_SERVER не схожий на валідний base64", cfg
    return True, "", cfg


def _gen_keypair() -> tuple[str, str]:
    priv = X25519PrivateKey.generate()
    pub = priv.public_key
    return base64.b64encode(bytes(priv)).decode(), base64.b64encode(bytes(pub)).decode()


def _make_conf(private_key_b64: str, client_ip_cidr: str, cfg: dict) -> str:
    return (
        "[Interface]\n"
        f"PrivateKey = {private_key_b64}\n"
        f"Address = {client_ip_cidr}\n"
        f"DNS = {cfg['DNS']}\n\n"
        "[Peer]\n"
        f"PublicKey = {cfg['SERVER_PUB']}\n"
        f"AllowedIPs = {cfg['ALLOWED']}\n"
        f"Endpoint = {cfg['ENDPOINT']}\n"
        "PersistentKeepalive = 25\n"
    )


def _make_qr_png_bytes(text: str) -> bytes:
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_=+\.\-]+")


def _safe_tunnel_name(base: str) -> str:
    """
    Робить назву тунелю, валідну для WireGuard (Windows):
    - дозволені символи: A-Z a-z 0-9 _ = + . -
    - макс. довжина 32 символи
    """
    # приберемо заборонені
    name = SAFE_NAME_PATTERN.sub("", base)
    # запасний варіант
    if not name:
        name = "vpn"
    # обрізати до 32 символів
    if len(name) > 32:
        name = name[:32]
    return name


@myvpn_router.message(Command("myvpn"))
async def cmd_myvpn(message: types.Message):
    ok, why, cfg = _validate_server_env()
    if not ok:
        await message.answer(
            "⚠️ Налаштування сервера WireGuard відсутні або некоректні.\n"
            f"{why}\n\n"
            "Адмін, задай WG_ENDPOINT та WG_PUBLIC_KEY_SERVER у .env і перезапусти бота."
        )
        return

    try:
        # 1) ключі
        priv_b64, pub_b64 = _gen_keypair()
        # 2) додаємо peer на сервері, отримуємо IP/32
        client_ip_cidr = add_peer_and_get_ip(pub_b64)
        # 3) конфіг
        conf_text = _make_conf(priv_b64, client_ip_cidr, cfg)

        # 4) безпечні ім'я файлів (Windows WireGuard використовує ім'я файлу як назву тунелю)
        username = message.from_user.username or f"user{message.from_user.id}"
        # базове ім'я коротке: частина юзернейма + суфікс
        base = f"{username}-vpn"
        safe_base = _safe_tunnel_name(base)
        # якщо після санітизації коротке — додамо короткий час, але так, щоб не перевищити 32
        ts = datetime.now(timezone.utc).strftime("%y%m%d%H%M")
        remain = 32 - len(safe_base) - 1  # під дефіс
        if remain > 0:
            safe_base = _safe_tunnel_name(f"{safe_base}-{ts[:remain]}")

        conf_name = f"{safe_base}.conf"
        png_name = f"{safe_base}.png"

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
