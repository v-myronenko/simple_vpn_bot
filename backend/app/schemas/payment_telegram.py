from __future__ import annotations

from pydantic import BaseModel

from .subscription_status import SubscriptionInfo


class TelegramStarsCompleteRequest(BaseModel):
    """
    Запит від бота до бекенду після успішної оплати Stars.
    MVP-варіант: нам потрібен тільки telegram_id,
    а всі інші дані (сума, валюта) ми беремо з плану.
    """
    telegram_id: int


class TelegramStarsCompleteResponse(BaseModel):
    """
    Відповідь після обробки оплати:
    - ok: чи все пройшло добре
    - message: текстове повідомлення
    - subscription: деталі активної/оновленої підписки (якщо є)
    """
    ok: bool
    message: str
    subscription: SubscriptionInfo | None = None
