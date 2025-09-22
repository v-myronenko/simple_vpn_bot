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

from wg_integrator import add_peer_and_get_ip, get_server_pubkey

myvpn_router = Router(name="myvpn")


class ServerPublicKeyUnavailableError(RuntimeError):
    """Raised when the WireGuard server public key cannot be located."""


def _load_server_pubkey() -> str:
    try:
        return get_server_pubkey()
    except RuntimeError as exc:
        raise ServerPublicKeyUnavailableError(
            "⚠️ Не вдалося отримати публічний ключ сервера WireGuard.\n"
            "Адмін, переконайся, що ключ доступний через одну з опцій:\n"
            "• працює інтерфейс (wg show wg0 public-key);\n"
            "• ключ збережено у /etc/wireguard/server_public.key або wg0.pub;\n"
            "• задано змінну середовища WG_PUBLIC_KEY."
        ) from exc

def _get_wg_env():
    return {
        "ENDPOINT": os.getenv("WG_ENDPOINT"),
        "DNS": os.getenv("WG_DNS", "1.1.1.1"),
        "ALLOWED": os.getenv("WG_ALLOWED_IPS", "0.0.0.0/0, ::/0").replace(" ", ""),
    }

def _validate_server_env() -> tuple[bool, str, dict]:
    cfg = _get_wg_env()
    if not cfg["ENDPOINT"]:
        return False, "В .env не задано WG_ENDPOINT (приклад: 203.0.113.10:51820)", cfg
    # Публічний ключ сервера читаємо з системи через get_server_pubkey()
    return True, "", cfg



def _gen_keypair() -> tuple[str, str]:
    priv = X25519PrivateKey.generate()
    pub = priv.public_key
    return base64.b64encode(bytes(priv)).decode(), base64.b64encode(bytes(pub)).decode()


def _make_conf(private_key_b64: str, client_ip_cidr: str, cfg: dict) -> str:
    # читаємо актуальний публічний ключ сервера на момент генерації
    spub = _load_server_pubkey()
    return (
        "[Interface]\n"
        f"PrivateKey = {private_key_b64}\n"
        f"Address = {client_ip_cidr}\n"
        f"DNS = {cfg['DNS']}\n\n"
        "[Peer]\n"
        f"PublicKey = {spub}\n"
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
            "Адмін, задай WG_ENDPOINT у .env і перезапусти бота.\n"
            "Публічний ключ серверного інтерфейсу бот отримує автоматично через "
            "`wg show`, резервні файли або змінну WG_PUBLIC_KEY."
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
    except ServerPublicKeyUnavailableError as e:
        await message.answer(str(e))
    except Exception as e:
        print(f"[/myvpn] ERROR: {e}")
        await message.answer("⚠️ Не вдалося згенерувати робочий конфіг. Надішли, будь ласка, лог із консолі.")
