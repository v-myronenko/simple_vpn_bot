# backend/app/services/vpn_provider_3xui.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import json
import uuid

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

        self.base_url = server.api_url.rstrip("/")
        self.username = server.api_user or settings.THREEXUI_USERNAME
        self.password = server.api_password or settings.THREEXUI_PASSWORD
        self.inbound_id = settings.THREEXUI_INBOUND_ID
        self._cookies: Optional[httpx.Cookies] = None

    def _login(self) -> None:
        """Логін у 3x-ui, збереження cookies для сесії."""
        with httpx.Client(verify=False, timeout=10.0) as client:
            resp = client.post(
                f"{self.base_url}/login",
                data={
                    "username": self.username,
                    "password": self.password,
                },
            )
            if resp.status_code != 200:
                raise VpnProviderError(
                    f"3x-ui login failed: {resp.status_code} {resp.text}"
                )
            self._cookies = resp.cookies

    def _get_client(self) -> httpx.Client:
        if self._cookies is None:
            self._login()
        return httpx.Client(verify=False, timeout=15.0, cookies=self._cookies)

    def create_client(self, email: str) -> VpnClient:
        """
        Створює нового клієнта в inbound через /panel/api/inbounds/addClient.

        Формат згідно офіційної Postman-колекції 3x-ui:
        - POST /panel/api/inbounds/addClient
        - form-data:
            id: inboundId
            settings: JSON-рядок з ключем "clients"
        """
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
            "id": str(self.inbound_id),  # має бути "1"
            "settings": json.dumps({"clients": [client_obj]}),
        }

        with self._get_client() as client:
            resp = client.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                data=form_data,
            )

        if resp.status_code != 200:
            # Тут спеціально лишаємо текст відповіді, щоб бачити,
            # що саме каже 3x-ui
            raise VpnProviderError(
                f"addClient failed: {resp.status_code} {resp.text}"
            )

        data = resp.json()
        if not data.get("success", False):
            raise VpnProviderError(
                f"addClient returned error: {data.get('msg')}"
            )

        return VpnClient(uuid=client_uuid, email=email)
