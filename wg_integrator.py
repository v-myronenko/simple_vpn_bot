# wg_integrator.py
from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

import paramiko


def get_server_pubkey() -> str:
    """
    Повертає актуальний публічний ключ сервера WireGuard.
    Порядок спроб:
      1) wg show wg0 public-key (живий інтерфейс)
      2) /etc/wireguard/server_public.key (збережений файл)
      3) змінна середовища WG_PUBLIC_KEY (фолбек)
    """
    # 1) live-інтерфейс
    try:
        out = subprocess.check_output(["wg", "show", "wg0", "public-key"], text=True).strip()
        if out:
            return out
    except Exception:
        pass

    # 2) файл(и) із ключем
    for path in ("/etc/wireguard/server_public.key", "/etc/wireguard/wg0.pub"):
        try:
            if os.path.exists(path):
                with open(path) as f:
                    s = f.read().strip()
                    if s:
                        return s
        except Exception:
            pass

    # 3) .env фолбек (небажано, але хай буде)
    env = os.getenv("WG_PUBLIC_KEY", "").strip()
    if env:
        return env

    raise RuntimeError("Server public key not found: ні wg0, ні /etc/wireguard/server_public.key, ні WG_PUBLIC_KEY")

class WGServerError(Exception):
    pass

def _read_env():
    # читаємо .env/ENV під час виклику
    return {
        "SSH_HOST": os.getenv("WG_SSH_HOST"),
        "SSH_PORT": int(os.getenv("WG_SSH_PORT", "22")),
        "SSH_USER": os.getenv("WG_SSH_USER", "root"),
        "SSH_KEY_PATH": os.getenv("WG_SSH_KEY_PATH"),
        "SSH_PASSWORD": os.getenv("WG_SSH_PASSWORD"),
        "WG_IFACE": os.getenv("WG_IFACE", "wg0"),
        "WG_NETWORK_CIDR": os.getenv("WG_NETWORK_CIDR", "10.7.0.0/24"),
    }


# Один скрипт: атомарно виділяє IP та додає peer
BASH_ADD_PEER = r"""#!/usr/bin/env bash
set -euo pipefail

IFACE="${1}"
NET="${2}"         # напр. 10.7.0.0/24 (припускаємо /24)
CLIENT_PUB="${3}"

LOCK="/etc/wireguard/.alloc.lock"
mkdir -p /etc/wireguard

exec 9> "$LOCK"
if ! flock -w 10 9; then
  echo -n "LOCK_FAIL"
  exit 1
fi

BASE="${NET%/*}"
IFS='.' read -r A B C D <<< "$BASE"
PREFIX="${A}.${B}.${C}"

# Список зайнятих останніх октетів
USED=$(wg show "$IFACE" allowed-ips 2>/dev/null | awk '{print $2}' | cut -d/ -f1 | awk -F. -v p="$PREFIX" '$1"."$2"."$3==p{print $4}' | sort -n | uniq || true)

# Шукаємо вільну адресу 2..254
for i in $(seq 2 254); do
  if ! echo "$USED" | grep -qx "$i"; then
    IP="${PREFIX}.${i}/32"
    wg set "$IFACE" peer "$CLIENT_PUB" allowed-ips "$IP"
    # збережемо на диск, якщо SaveConfig=true
    wg-quick save "$IFACE" >/dev/null 2>&1 || true
    echo -n "$IP"
    exit 0
  fi
done

echo -n "NO_FREE_IP"
exit 1
"""


def _ssh_client():
    env = _read_env()
    host = env["SSH_HOST"]
    if not host:
        raise WGServerError("WG_SSH_HOST не задано")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key_path = env["SSH_KEY_PATH"]
    password = env["SSH_PASSWORD"]

    if key_path:
        key_file = Path(key_path).expanduser()
        if not key_file.exists():
            raise WGServerError(f"SSH ключ не знайдено: {key_file}")
        # пробуємо ed25519, далі RSA
        try:
            pkey = paramiko.Ed25519Key.from_private_key_file(str(key_file))
        except Exception:
            try:
                pkey = paramiko.RSAKey.from_private_key_file(str(key_file))
            except Exception as e:
                raise WGServerError(f"Не вдалося завантажити SSH ключ: {e}")
        client.connect(host, env["SSH_PORT"], env["SSH_USER"], pkey=pkey, timeout=25)
    elif password:
        client.connect(host, env["SSH_PORT"], env["SSH_USER"], password=password, timeout=25)
    else:
        raise WGServerError("Задай або WG_SSH_KEY_PATH, або WG_SSH_PASSWORD")

    return client


def add_peer_and_get_ip(client_pubkey_b64: str) -> str:
    """
    Завантажує скрипт через stdin та викликає його як:
      bash -s -- <iface> <cidr> <client_pub>
    Повертає виділений IP/32 або кидає WGServerError.
    """
    env = _read_env()
    iface = env["WG_IFACE"]
    cidr = env["WG_NETWORK_CIDR"]

    # готуємо команду
    cmd = f"bash -s -- {shlex.quote(iface)} {shlex.quote(cidr)} {shlex.quote(client_pubkey_b64)}"

    client = _ssh_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=40)
        # надсилаємо сам скрипт у stdin
        stdin.write(BASH_ADD_PEER)
        stdin.channel.shutdown_write()

        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()

        if out in ("", "LOCK_FAIL", "NO_FREE_IP"):
            raise WGServerError(f"Не вдалося додати peer: out='{out}', err='{err}'")
        return out
    finally:
        client.close()
