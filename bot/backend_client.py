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
