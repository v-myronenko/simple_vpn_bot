# wg_integrator.py
from __future__ import annotations

import os
import paramiko

# Налаштування з .env:
SSH_HOST = os.getenv("142.93.238.250")         # напр.: "68.183.70.136"
SSH_PORT = int(os.getenv("WG_SSH_PORT", "22"))
SSH_USER = os.getenv("WG_SSH_USER", "root")
SSH_KEY_PATH = os.getenv("WG_SSH_KEY_PATH")  # абсолютний шлях до приватного ключа (ed25519/rsa)
SSH_PASSWORD = os.getenv("WG_SSH_PASSWORD")  # якщо без ключа (небажано, але підтримуємо)

# WireGuard серверні параметри:
WG_IFACE = os.getenv("WG_IFACE", "wg0")
WG_NETWORK_CIDR = os.getenv("WG_NETWORK_CIDR", "10.7.0.0/24")  # припускаємо /24

# Bash-сніпет, який АТОМАРНО виділяє IP та додає peer
BASH_ADD_PEER = r"""
set -euo pipefail
IFACE="${1}"
NET="${2}"         # напр. 10.7.0.0/24 (припускаємо /24)
CLIENT_PUB="${3}"

LOCK="/etc/wireguard/.alloc.lock"
mkdir -p /etc/wireguard

(
  flock -w 10 9 || { echo "LOCK_FAIL"; exit 1; }

  BASE="${NET%/*}"
  IFS='.' read -r A B C D <<< "$BASE"
  PREFIX="${A}.${B}.${C}"

  # Уже зайняті останні октети
  USED=$(wg show "$IFACE" allowed-ips 2>/dev/null | awk '{print $2}' | cut -d/ -f1 | awk -F. -v p="$PREFIX" '$1"."$2"."$3==p{print $4}' | sort -n | uniq)

  # Пошук вільного IP 10.7.0.[2..254]/32
  for i in $(seq 2 254); do
    if ! echo "$USED" | grep -qx "$i"; then
      IP="${PREFIX}.${i}/32"
      # Додати peer
      wg set "$IFACE" peer "$CLIENT_PUB" allowed-ips "$IP"
      # Зберегти конфіг на диск (якщо SaveConfig=true в /etc/wireguard/${IFACE}.conf)
      wg-quick save "$IFACE" >/dev/null 2>&1 || true
      echo -n "$IP"
      exit 0
    fi
  done

  echo -n "NO_FREE_IP"
  exit 1

) 9> "$LOCK"
"""


class WGServerError(Exception):
    pass


def _ssh_client() -> paramiko.SSHClient:
    if not SSH_HOST:
        raise WGServerError("WG_SSH_HOST не задано")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if SSH_KEY_PATH and os.path.exists(SSH_KEY_PATH):
        pkey = None
        try:
            pkey = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)
        except Exception:
            try:
                pkey = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
            except Exception as e:
                raise WGServerError(f"Не вдалося завантажити SSH ключ: {e}")
        client.connect(SSH_HOST, SSH_PORT, SSH_USER, pkey=pkey, timeout=15)
    elif SSH_PASSWORD:
        client.connect(SSH_HOST, SSH_PORT, SSH_USER, password=SSH_PASSWORD, timeout=15)
    else:
        raise WGServerError("Задай або WG_SSH_KEY_PATH, або WG_SSH_PASSWORD")
    return client


def add_peer_and_get_ip(client_pubkey_b64: str) -> str:
    """
    Підключається по SSH, атомарно виділяє вільний IP у підмережі WG_NETWORK_CIDR,
    додає peer (public_key = client_pubkey_b64) у інтерфейс WG_IFACE і повертає IP/32.
    """
    cmd = f"bash -lc {repr(BASH_ADD_PEER)} && bash -lc 'WG_IF={WG_IFACE}; NET={WG_NETWORK_CIDR}; bash -c \"{BASH_ADD_PEER.replace(chr(10), ';')}\" {WG_IFACE} {WG_NETWORK_CIDR} {client_pubkey_b64}'"
    # Пояснення: спершу 'bash -lc' прогріває інтерпретатор; далі виклик із параметрами.

    client = _ssh_client()
    try:
        # Без першого 'bash -lc ...' не всі середовища завантажують PATH / wg
        cmd = f"bash -lc '{BASH_ADD_PEER}'; bash -lc 'bash -c \"{BASH_ADD_PEER.replace(chr(10), ';')}\" {WG_IFACE} {WG_NETWORK_CIDR} {client_pubkey_b64}'"
        stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if err and "warning" not in err.lower():
            # wg-quick save може виводити warnings — їх прощаємо
            pass
        if out in ("", "LOCK_FAIL", "NO_FREE_IP"):
            raise WGServerError(f"Не вдалося виділити IP / додати peer (out='{out}', err='{err}')")
        return out  # формат: 10.7.0.X/32
    finally:
        client.close()
