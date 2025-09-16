#!/usr/bin/env bash
set -euo pipefail

WG_IFACE="${WG_IFACE:-wg0}"
WG_NET_CIDR="${WG_NETWORK_CIDR:-10.8.0.0/24}"

# Знайти зовнішній інтерфейс (те, чим сервер ходить в інтернет)
OUT_IF="$(ip -4 route get 8.8.8.8 | awk '{for(i=1;i<=NF;i++) if($i=="dev"){print $(i+1); exit}}')"
if [[ -z "${OUT_IF}" ]]; then
  echo "Не вдалося визначити зовнішній інтерфейс"; exit 1
fi
echo "Зовнішній інтерфейс: ${OUT_IF}"
echo "WG інтерфейс: ${WG_IFACE}"
echo "WG підмережа: ${WG_NET_CIDR}"

# 1) Увімкнути форвардинг
sysctl -w net.ipv4.ip_forward=1 >/dev/null
sysctl -w net.ipv6.conf.all.forwarding=1 >/dev/null
grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf || echo "net.ipv4.ip_forward=1" >>/etc/sysctl.conf
grep -q "net.ipv6.conf.all.forwarding=1" /etc/sysctl.conf || echo "net.ipv6.conf.all.forwarding=1" >>/etc/sysctl.conf

# 2) Відкрити порт 51820/udp у iptables (якщо UFW не використовується)
iptables -C INPUT -p udp --dport 51820 -j ACCEPT 2>/dev/null || iptables -A INPUT -p udp --dport 51820 -j ACCEPT

# 3) NAT (SNAT/MASQUERADE) тільки для нашої WG-підмережі
iptables -t nat -C POSTROUTING -s "${WG_NET_CIDR}" -o "${OUT_IF}" -j MASQUERADE 2>/dev/null \
  || iptables -t nat -A POSTROUTING -s "${WG_NET_CIDR}" -o "${OUT_IF}" -j MASQUERADE

# 4) Дозволити форвардинг через wg0
iptables -C FORWARD -i "${WG_IFACE}" -j ACCEPT 2>/dev/null || iptables -A FORWARD -i "${WG_IFACE}" -j ACCEPT
iptables -C FORWARD -o "${WG_IFACE}" -j ACCEPT 2>/dev/null || iptables -A FORWARD -o "${WG_IFACE}" -j ACCEPT

# 5) Якщо увімкнений UFW — дозволити роутинг
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow 51820/udp || true
  # дозволити транзит між wg0 та зовнішнім інтерфейсом
  ufw route allow in on "${WG_IFACE}" out on "${OUT_IF}" || true
  ufw reload || true
fi

# 6) Зберегти правила
if command -v netfilter-persistent >/dev/null 2>&1; then
  netfilter-persistent save || true
else
  apt-get update && apt-get install -y iptables-persistent
  netfilter-persistent save || true
fi

# 7) Перезапустити wg0
systemctl restart wg-quick@"${WG_IFACE}"

echo "Готово. Діагностика:"
echo "------------------------------------"
ip addr show "${WG_IFACE}" | sed 's/^/  /'
echo
wg show | sed 's/^/  /'
echo
echo "iptables -t nat -S:"
iptables -t nat -S | sed 's/^/  /'
