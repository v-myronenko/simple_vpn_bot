import io
import ipaddress
import subprocess
from typing import Tuple, Optional

import qrcode


class WGManager:
    """
    Працює ЛОКАЛЬНО на тому ж сервері, де крутиться WireGuard.
    Для виконання команд потрібні sudo-права (NOPASSWD) для:
      - wg show / wg set
      - cat /etc/wireguard/server_public.key (або просто wg show <iface> public-key)
    """

    def __init__(self, interface: str = "wg0", network_cidr: str = "10.8.0.0/24", endpoint: Optional[str] = None):
        self.interface = interface
        self.network = ipaddress.ip_network(network_cidr, strict=False)
        self.endpoint = endpoint  # "host:port"

    # -------- utils --------

    def _run(self, cmd: str, *, text: bool = True) -> str:
        """
        Виконує bash-команду з sudo; повертає stdout (str).
        Піднімає CalledProcessError при ненульовому коді.
        """
        res = subprocess.run(
            ["bash", "-lc", cmd],
            check=True,
            capture_output=True,
            text=text,
        )
        return res.stdout.strip()

    # -------- server info --------

    def get_server_public_key(self) -> str:
        """
        Повертає публічний ключ сервера.
        Спочатку через `wg show`, якщо недоступно — читаємо файл ключа.
        """
        # 1) пробуємо wg show
        try:
            return self._run(f"sudo wg show {self.interface} public-key")
        except subprocess.CalledProcessError:
            pass

        # 2) файл ключа (може бути інший шлях у твоїй інсталяції)
        try:
            return self._run("sudo cat /etc/wireguard/server_public.key")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "Не вдалося отримати ключ сервера: немає доступу до `wg show` або файлу server_public.key"
            ) from e

    # -------- IP management --------

    def _list_used_ips(self) -> set[str]:
        """
        Повертає множину IP (рядки), вже виданих пірів wg0.
        Беремо з `wg show <iface> allowed-ips`.
        """
        out = self._run(f"sudo wg show {self.interface} allowed-ips")
        used: set[str] = set()
        if not out:
            return used
        # формат рядка: "<peerpub>    <ip1/32, ip6/128>"
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            ips_chunk = parts[-1]
            for ip_mask in ips_chunk.split(","):
                ip_mask = ip_mask.strip()
                if "/" in ip_mask:
                    ip = ip_mask.split("/", 1)[0]
                    used.add(ip)
        return used

    def _next_free_ip(self) -> str:
        """
        Повертає наступну вільну IPv4-адресу з підмережі.
        Резервуємо першу адресу (зазвичай .1) під сервер.
        """
        used = self._list_used_ips()
        for i, host in enumerate(self.network.hosts(), start=1):
            # пропускаємо перший хост (ймовірно, це адреса сервера)
            if i == 1:
                continue
            ip = str(host)
            if ip not in used:
                return ip
        raise RuntimeError("Вільні IP у пулі закінчилися")

    # -------- keys --------

    def _gen_keypair(self) -> Tuple[str, str]:
        """
        Генерує (priv, pub) ключі клієнта через wg.
        """
        priv = self._run("wg genkey")
        pub = self._run(f"bash -lc 'printf %s {priv} | wg pubkey'")
        return priv, pub

    # -------- peer create --------

    def create_peer(self, name: str) -> Tuple[bytes, Optional[bytes]]:
        """
        Створює пір:
          - генерує ключі
          - видає IP
          - додає peer у wg
          - повертає (конфіг .conf у bytes, PNG із QR у bytes)
        """
        client_priv, client_pub = self._gen_keypair()
        client_ip = self._next_free_ip()
        server_pub = self.get_server_public_key()
        endpoint = self.endpoint
        if not endpoint:
            raise RuntimeError("Не вказано endpoint (host:port) для WireGuard")

        # додаємо піра в інтерфейс
        self._run(
            f"sudo wg set {self.interface} peer {client_pub} allowed-ips {client_ip}/32"
        )

        # готуємо текст конфігу
        conf_str = f"""[Interface]
PrivateKey = {client_priv}
Address = {client_ip}/32
DNS = 1.1.1.1

[Peer]
PublicKey = {server_pub}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {endpoint}
PersistentKeepalive = 25
"""
        conf_bytes = conf_str.encode("utf-8")

        # генеруємо QR з ТЕКСТУ конфігу (а не з bytes)
        qr_buf = io.BytesIO()
        qrcode.make(conf_str).save(qr_buf)  # не передаємо format=...
        png_bytes = qr_buf.getvalue()

        return conf_bytes, png_bytes
