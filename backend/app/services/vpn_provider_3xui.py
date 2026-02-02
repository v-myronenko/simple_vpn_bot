# backend/app/services/vpn_provider_3xui.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import json
import uuid
import os

import httpx

from app.core.config import settings
from app.models import Server


class VpnProviderError(Exception):
    """Базова помилка VPN-провайдера (3x-ui)."""


@dataclass
class VpnClient:
    uuid: str
    email: str
    # expiryTime у 3x-ui ми поки не чіпаємо (0 = без обмеження)


class ThreeXUIProvider:
    """
    Примітивний клієнт для 3x-ui.

    Працює на рівні:
    - POST /login
    - POST /panel/api/inbounds/addClient

    MVP-логіка:
    - створюємо клієнта (uuid + email)
    - expiryTime ставимо 0 (без ліміту), контроль строку робимо на нашому боці
    """

    def __init__(self, server: Server) -> None:
        # server.api_url повинен бути типу: https://IP:PORT/randompath
        if not server.api_url:
            raise VpnProviderError("Server.api_url is not configured for 3x-ui")

        self.server = server
        self.base_url = server.api_url.rstrip("/")
        self.username = server.api_user or settings.THREEXUI_USERNAME
        self.password = server.api_password or settings.THREEXUI_PASSWORD
        self.inbound_id = int(os.getenv("THREEXUI_INBOUND_ID", "1"))
        self._cookies: Optional[httpx.Cookies] = None

    def _login(self, client: httpx.Client) -> None:
        login_url = "/login"

        resp = client.post(
            login_url,
            data={
                "username": self.server.api_user,
                "password": self.server.api_password,
            },
        )

        if resp.status_code != 200:
            raise VpnProviderError(
                f"3x-ui login failed: {resp.status_code} {resp.text!r}"
            )

        try:
            data = resp.json()
        except Exception:
            raise VpnProviderError(
                f"3x-ui login returned non-JSON response: {resp.text!r}"
            )

        if not data.get("success", False):
            raise VpnProviderError(
                f"3x-ui login error: {data.get('msg')} raw={data}"
            )

    def _get_client(self) -> httpx.Client:
        client = httpx.Client(
            base_url=self.base_url,
            timeout=10.0,
            follow_redirects=True,
        )
        self._login(client)
        return client

    def create_client(self, email: str) -> VpnClient:
        client_uuid = str(uuid.uuid4())

        client_obj = {
            "id": client_uuid,
            "flow": "xtls-rprx-vision",
            "email": email,
            "limitIp": 0,
            "totalGB": 0,
            "expiryTime": 0,
            "enable": True,
            "tgId": "",
            "subId": "",
            "comment": "",
            "reset": 0,
        }

        form_data = {
            "id": str(self.inbound_id),
            "settings": json.dumps({"clients": [client_obj]}),
        }

        client = self._get_client()
        try:
            url = f"{self.base_url.rstrip('/')}/panel/api/inbounds/addClient"
            resp = client.post(url, data=form_data)
        finally:
            client.close()

        if resp.status_code != 200:
            raise VpnProviderError(
                f"addClient failed: {resp.status_code} "
                f"url={url} inbound_id={self.inbound_id} "
                f"resp_text={resp.text!r}"
            )

        try:
            data = resp.json()
        except Exception:
            raise VpnProviderError(
                f"addClient: cannot parse JSON response: {resp.text!r}"
            )

        if not data.get("success", False):
            raise VpnProviderError(
                f"addClient returned error: {data.get('msg')} raw={data}"
            )

        return VpnClient(uuid=client_uuid, email=email)


