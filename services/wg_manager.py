# services/wg_manager.py
import subprocess
import base64
import qrcode
from io import BytesIO

class WGManager:
    """Локальний менеджер WireGuard без SSH. Використовує sudo wg / wg-quick."""
    def __init__(self, interface: str = "wg0", network_cidr: str = "10.8.0.0/24"):
        self.interface = interface
        self.network = network_cidr

    def _sudo(self, *args: str) -> str:
        res = subprocess.run(["sudo", "-n", *args], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(args)}\n{res.stderr}")
        return res.stdout.strip()

    def next_ip(self) -> str:
        # Простий спосіб знайти вільну IP у 10.8.0.0/24 (пробігаємось по 2..254)
        used = set()
        out = self._sudo("wg", "show", self.interface, "peers")
        peers = out.splitlines() if out else []
        for p in peers:
            conf = self._sudo("wg", "show", self.interface, "allowed-ips", p)
            for line in conf.splitlines():
                if line.strip():
                    used.add(line.split()[0].split('/')[0])
        # 10.8.0.1 — сервер; почнемо з 10.8.0.2
        for last in range(2, 255):
            candidate = f"10.8.0.{last}"
            if candidate not in used:
                return candidate
        raise RuntimeError("No free IPs left in 10.8.0.0/24")

    def create_peer(self, name: str) -> tuple[str, bytes]:
        # генеруємо ключі клієнта
        priv = subprocess.check_output(["wg", "genkey"]).decode().strip()
        pub = subprocess.check_output(["bash", "-lc", f"printf %s '{priv}' | wg pubkey"]).decode().strip()
        ip = self.next_ip()
        allowed_ip = f"{ip}/32"

        # додаємо peer на сервер
        self._sudo("wg", "set", self.interface, "peer", pub, "allowed-ips", allowed_ip)
        self._sudo("wg-quick", "save", self.interface)

        # читаємо серверні параметри
        server_pub = subprocess.check_output(["bash", "-lc", "cat /etc/wireguard/server_public.key"]).decode().strip()
        endpoint = self._detect_endpoint()
        config_text = f"""[Interface]
PrivateKey = {priv}
Address = {allowed_ip}
DNS = 1.1.1.1

[Peer]
PublicKey = {server_pub}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

        # QR як PNG
        qr_buf = BytesIO()
        qrcode.make(config_text).save(qr_buf, format="PNG")
        png_bytes = qr_buf.getvalue()

        return config_text, png_bytes

    def _detect_endpoint(self) -> str:
        # Зроби простіше: вкажи домен/айпі вручну у .env або підстав IP сервера
        # Тут — читаємо публічний IP із хоста
        ip = subprocess.check_output(["bash", "-lc", "curl -s ifconfig.me || curl -s ipinfo.io/ip"]).decode().strip()
        return f"{ip}:51820"
