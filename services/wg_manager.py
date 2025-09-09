# services/wg_manager.py
import io
import ipaddress
import subprocess
from dataclasses import dataclass
from typing import Tuple, Optional

import qrcode
from qrcode.image.pure import PyPNGImage


def sh(*args: str, input_bytes: Optional[bytes] = None) -> str:
    """
    Run a command and return stdout (decoded utf-8, stripped).
    Raises CalledProcessError on failure with readable stderr.
    """
    proc = subprocess.run(
        args,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,          # decode to str
    )
    return proc.stdout.strip()


def sh_bash(cmd: str) -> str:
    """Run a whole command line via bash -lc '...' and return stdout."""
    out = subprocess.run(
        ["bash", "-lc", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    )
    return out.stdout.strip()


@dataclass
class WGManager:
    """
    WireGuard manager that works directly on the local server via sudo.
    Requires:
      - systemd service wg-quick@wg0 running
      - user running the bot has sudoers rule:
            bot ALL=(root) NOPASSWD: /usr/bin/wg
    """
    interface: str = "wg0"
    network_cidr: str = "10.8.0.0/24"
    endpoint_host: Optional[str] = None  # if None, will be auto-detected

    # ----------------------- low-level helpers -----------------------

    def _sudo(self, *args: str) -> str:
        """Run command with sudo and return stdout."""
        return sh("sudo", *args)

    # ----------------------- server info -----------------------------

    def get_server_public_key(self) -> str:
        """Public key of server interface."""
        return self._sudo("wg", "show", self.interface, "public-key").strip()

    def get_listen_port(self) -> int:
        return int(self._sudo("wg", "show", self.interface, "listen-port"))

    def get_endpoint_host(self) -> str:
        """
        If not set explicitly, detect a public IPv4 the box uses to reach the Internet.
        Works well on typical VPS (DigitalOcean/Linode/etc).
        """
        if self.endpoint_host:
            return self.endpoint_host
        # src ip from default route to 1.1.1.1
        ip = sh_bash("ip -4 route get 1.1.1.1 | awk '{print $7; exit}'")
        return ip or "SERVER_IP"

    # ----------------------- IP planning -----------------------------

    def _used_ips(self) -> set[str]:
        """
        Parse `wg show <iface> allowed-ips` and collect used /32 IPv4 addresses.
        """
        used = set()
        try:
            out = self._sudo("wg", "show", self.interface, "allowed-ips")
            # each line like:
            # <peer_public_key> 10.8.0.2/32
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2 and "/" in parts[-1]:
                    ip = parts[-1].split("/")[0]
                    used.add(ip)
        except subprocess.CalledProcessError:
            pass
        return used

    def _next_ip(self) -> str:
        """
        Return the next free /32 host IP inside network_cidr.
        Reserves the first address (.1) for the server itself.
        """
        net = ipaddress.ip_network(self.network_cidr)
        used = self._used_ips()
        # Start from the second host (skip .1 which server uses)
        for host in list(net.hosts())[1:]:
            ip = str(host)
            if ip not in used:
                return ip
        raise RuntimeError("No free IPs left in the VPN subnet")

    # ----------------------- key generation --------------------------

    @staticmethod
    def _gen_keypair() -> Tuple[str, str]:
        """
        Generate (private, public) key pair using `wg` tool.
        """
        priv = sh("wg", "genkey")
        pub = sh("wg", "pubkey", input_bytes=(priv + "\n").encode("utf-8"))
        return priv.strip(), pub.strip()

    # ----------------------- main API --------------------------------

    def add_peer(self, peer_name: str) -> Tuple[str, Optional[bytes]]:
        """
        Create a new peer:
          - generate keys
          - pick next free 10.8.0.X
          - `wg set <iface> peer <pub> allowed-ips <ip>/32`
        Returns: (config_text, png_bytes)
        """
        client_priv, client_pub = self._gen_keypair()
        client_ip = self._next_ip()

        # Attach peer to the running interface
        self._sudo(
            "wg",
            "set",
            self.interface,
            "peer",
            client_pub,
            "allowed-ips",
            f"{client_ip}/32",
        )

        server_pub = self.get_server_public_key()
        listen_port = self.get_listen_port()
        endpoint = f"{self.get_endpoint_host()}:{listen_port}"

        conf_text = (
            "[Interface]\n"
            f"PrivateKey = {client_priv}\n"
            f"Address = {client_ip}/32\n"
            "DNS = 1.1.1.1, 9.9.9.9\n"
            "\n"
            "[Peer]\n"
            f"PublicKey = {server_pub}\n"
            f"Endpoint = {endpoint}\n"
            "AllowedIPs = 0.0.0.0/0, ::/0\n"
            "PersistentKeepalive = 25\n"
        )

        # Build QR from the full config text (WireGuard clients support it)
        try:
            img = qrcode.make(conf_text, image_factory=PyPNGImage)
            buf = io.BytesIO()
            img.save(buf)            # <- ВАЖЛИВО: без format="PNG"
            buf.seek(0)
            png_bytes = buf.getvalue()
        except Exception:
            # QR не критичний — повернемо лише конфіг
            png_bytes = None

        return conf_text, png_bytes
