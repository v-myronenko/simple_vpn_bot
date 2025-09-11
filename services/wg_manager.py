import base64
import io, qrcode
import ipaddress
import os
import subprocess
from qrcode.image.pil import PilImage
from dataclasses import dataclass
from typing import Optional, Tuple

import qrcode
from qrcode.image.pil import PilImage


def _run(cmd: str) -> str:
    """Запускає команду в bash і повертає stdout як str (падає з помилкою, якщо код != 0)."""
    proc = subprocess.run(["bash", "-lc", cmd], check=True, text=True, capture_output=True)
    return proc.stdout.strip()


def _read_file(path: str, binary: bool = False):
    mode = "rb" if binary else "r"
    with open(path, mode) as f:
        return f.read()


@dataclass
class Peer:
    name: str
    private_key: str
    public_key: str
    ip: str  # 10.8.0.X


class WGManager:
    """
    Працює локально на сервері з піднятим wg0.
    Видає peer'ам адреси з підмережі, додає їх у wg, будує клієнтські конфіги.
    """

    def __init__(
        self,
        interface: str = "wg0",
        network_cidr: str = "10.8.0.0/24",
        endpoint_host: Optional[str] = None,   # <--- НОВЕ
        endpoint_port: int = 51820,            # <--- НОВЕ
        dns: str = "1.1.1.1",
        keepalive: int = 25,
        mtu: Optional[int] = 1280,
    ):
        self.interface = interface
        self.network = ipaddress.ip_network(network_cidr)
        self.dns = dns
        self.keepalive = keepalive
        self.mtu = mtu
        self.endpoint_host = endpoint_host
        self.endpoint_port = endpoint_port

        # Зчитуємо server public key з живого інтерфейсу, а не з файлу.
        self.server_public_key = _run(f"wg show {self.interface} public-key")

        # IP сервера (Address у [Interface]) беремо з конфігу wg0
        # Спроба витягти першу адресу з `ip addr show`.
        self.server_ips = self._read_interface_ips()

    def _read_interface_ips(self):
        out = _run(f"ip -4 addr show {self.interface} | awk '/inet / {{print $2}}'")
        v4 = out.splitlines()
        out6 = _run(f"ip -6 addr show {self.interface} | awk '/inet6 / {{print $2}}'") or ""
        v6 = out6.splitlines() if out6 else []
        return {"v4": v4, "v6": v6}

    def _used_ips(self) -> set:
        """Повертає вже видані /32 для peers."""
        out = _run(f"wg show {self.interface} allowed-ips")
        used = set()
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 3 and parts[-1].endswith("/32"):
                used.add(parts[-1].split("/")[0])
        return used

    def _next_free_ip(self) -> str:
        """Шукає наступну вільну IP у підмережі (пропускає network/broadcast/першу адресу сервера)."""
        used = self._used_ips()
        # починаємо з .2
        for host in list(self.network.hosts())[1:]:
            ip = str(host)
            if ip not in used:
                return ip
        raise RuntimeError("Немає вільних IP у підмережі")

    @staticmethod
    def _gen_keypair() -> Tuple[str, str]:
        priv = _run("wg genkey")
        pub = _run(f"echo '{priv}' | wg pubkey")
        return priv, pub

    def _add_peer_to_wg(self, peer_pub: str, peer_ip: str):
        # додати peer і його allowed-ips
        _run(f"sudo wg set {self.interface} peer {peer_pub} allowed-ips {peer_ip}/32")

    def _build_client_config_text(
        self,
        peer: Peer,
        endpoint_host: Optional[str],
        endpoint_port: int,
    ) -> str:
        # endpoint_host: якщо не задано явно — пробуємо взяти публічну IPv4
        if not endpoint_host:
            endpoint_host = _run("curl -4 -s ifconfig.me || curl -4 -s ipinfo.io/ip || echo ''").strip()
            if not endpoint_host:
                # як крайній варіант — піднімемо помилку, щоб не генерувати 127.0.0.1
                raise RuntimeError("Не вдалося визначити публічну IP сервера. Задай WG_ENDPOINT_HOST у .env")

        lines = []
        lines.append("[Interface]")
        lines.append(f"PrivateKey = {peer.private_key}")
        lines.append(f"Address = {peer.ip}/32")
        lines.append(f"DNS = {self.dns}")
        if self.mtu:
            lines.append(f"MTU = {self.mtu}")
        lines.append("")

        lines.append("[Peer]")
        lines.append(f"PublicKey = {self.server_public_key}")
        lines.append(f"AllowedIPs = 0.0.0.0/0, ::/0")
        lines.append(f"Endpoint = {endpoint_host}:{endpoint_port}")
        lines.append(f"PersistentKeepalive = {self.keepalive}")

        return "\n".join(lines)

    @staticmethod
    def _png_from_text(text: str) -> bytes:
        img: PilImage = qrcode.make(text, image_factory=PilImage)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()

    def add_peer(self, peer_name: str) -> Tuple[bytes, Optional[bytes]]:
        """Створює peer, додає у wg, повертає (конфіг як bytes, PNG QR як bytes)."""
        priv, pub = self._gen_keypair()
        ip = self._next_free_ip()
        self._add_peer_to_wg(pub, ip)

        peer = Peer(name=peer_name, private_key=priv, public_key=pub, ip=ip)

        conf_text = self._build_client_config_text(
            peer=peer,
            endpoint_host=self.endpoint_host,
            endpoint_port=self.endpoint_port,
        )
        png = self._png_from_text(conf_text)
        return conf_text.encode("utf-8"), png
