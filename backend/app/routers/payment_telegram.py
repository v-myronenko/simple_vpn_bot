from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    TelegramStarsCompleteRequest,
    SubscriptionStatusResponse,
    SubscriptionInfo,
)
from app.services import PaymentService

router = APIRouter(prefix="/api/payments", tags=["payments"])

@router.post("/telegram-stars/complete", response_model=SubscriptionStatusResponse)
def telegram_stars_complete(
    payload: TelegramStarsCompleteRequest,
    db: Session = Depends(get_db),
):
    """
    Викликається ботом після успішної оплати Telegram Stars.

    MVP-логіка:
    - створюємо/продовжуємо підписку
    - створюємо запис payment зі статусом 'success'
    - повертаємо актуальний статус підписки в тому ж форматі, що й /subscription/status
    """
    service = PaymentService(db)

    try:
        subscription, payment = service.process_telegram_stars_payment(
            telegram_id=payload.telegram_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    plan = subscription.plan
    server = subscription.server

    sub_info = SubscriptionInfo(
        plan_code=plan.code,
        plan_name=plan.name,
        end_at=subscription.end_at,
        server_name=server.name,
        server_region=server.region,
    )

    return SubscriptionStatusResponse(
        user_exists=True,
        has_active_subscription=True,
        subscription=sub_info,
    )
