# backend/app/routers/payment_telegram.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Plan, Server
from app.schemas import (
    TelegramStarsCompleteRequest,
    TelegramStarsCompleteResponse,
    SubscriptionInfo,
)
from app.services import PaymentService

# У main.py цей роутер підключається з prefix="/api", тому
# фінальний шлях = /api/payment/telegram/stars-complete
router = APIRouter(
    prefix="/payment/telegram",
    tags=["payment"],
)


@router.post(
    "/stars-complete",
    response_model=TelegramStarsCompleteResponse,
    status_code=status.HTTP_200_OK,
)
def telegram_stars_complete(
    body: TelegramStarsCompleteRequest,
    db: Session = Depends(get_db),
):
    """
    Обробка успішної оплати Telegram Stars від бота.

    - Створює/продовжує підписку через PaymentService
    - Повертає короткий опис підписки (plan, end_at, server)
    """
    service = PaymentService(db)

    try:
        subscription, payment = service.process_telegram_stars_payment(
            telegram_id=body.telegram_id
        )
    except ValueError as e:
        # Помилки типу "нема плану/сервера" — це 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # Добираємо план і сервер, щоб сформувати SubscriptionInfo
    plan: Plan | None = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    server: Server | None = db.query(Server).filter(Server.id == subscription.server_id).first()

    if plan is None or server is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plan or server not found for subscription",
        )

    sub_info = SubscriptionInfo(
        plan_code=plan.code,
        plan_name=plan.name,
        end_at=subscription.end_at,
        server_name=server.name,
        server_region=server.region,
    )

    return TelegramStarsCompleteResponse(
        ok=True,
        message="Payment processed and subscription updated.",
        subscription=sub_info,
    )
