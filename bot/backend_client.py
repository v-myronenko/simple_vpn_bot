from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from config import settings


class BackendClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.backend_base_url.rstrip("/")

    async def get_subscription_status(self, telegram_id: int) -> Dict[str, Any]:
        """
        Викликає бекенд-ендпоінт:
        GET /api/users/{telegram_id}/subscription/status
        """
        url = f"{self.base_url}/api/users/{telegram_id}/subscription/status"

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def complete_telegram_stars_payment(
            self,
            telegram_id: int,
            payload: str,
            stars_amount: int,
            currency: str,
            telegram_payment_charge_id: str,
            provider_payment_charge_id: str | None,
    ) -> Dict[str, Any]:
        """
        Викликає бекенд-ендпоінт:
        POST /api/payments/telegram-stars/complete
        """
        url = f"{self.base_url}/api/payments/telegram-stars/complete"
        data = {
            "telegram_id": telegram_id,
            "payload": payload,
            "stars_amount": stars_amount,
            "currency": currency,
            "telegram_payment_charge_id": telegram_payment_charge_id,
            "provider_payment_charge_id": provider_payment_charge_id,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=data)
            resp.raise_for_status()
            return resp.json()

