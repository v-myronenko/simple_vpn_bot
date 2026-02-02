# backend/app/utils/vless_config.py

from urllib.parse import urlencode, quote

from app.core.config import settings


def build_vless_reality_url(uuid: str, server_name: str | None = None) -> str:
    host = settings.VPN_REALITY_HOST
    port = settings.VPN_REALITY_PORT

    tag = server_name or "SVPN"

    params = {
        "type": "tcp",
        "security": "reality",
        "sni": settings.VPN_REALITY_SNI,
        "fp": settings.VPN_REALITY_FINGERPRINT,
        "flow": settings.VPN_REALITY_FLOW,
        "pbk": settings.VPN_REALITY_PUBLIC_KEY,
    }

    if settings.VPN_REALITY_SHORT_ID:
        params["sid"] = settings.VPN_REALITY_SHORT_ID

    query = urlencode(params)

    return f"vless://{uuid}@{host}:{port}?{query}#{quote(tag)}"
