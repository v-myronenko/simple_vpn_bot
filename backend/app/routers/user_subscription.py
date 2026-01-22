from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import SubscriptionStatusResponse, SubscriptionInfo
from app.services import UserService, SubscriptionService


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{telegram_id}/subscription/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    """
    Повертає статус підписки користувача по telegram_id.

    Використання з боку бота:
    - якщо користувача немає — створюємо (через UserService.get_or_create_user)
    - якщо підписки немає — has_active_subscription = false
    """
    user_service = UserService(db)
    sub_service = SubscriptionService(db)

    # створюємо або отримуємо користувача
    user = user_service.get_or_create_user(telegram_id=telegram_id)

    if not user:
        # теоретично не станеться через get_or_create, але лишимо перевірку
        raise HTTPException(status_code=500, detail="Cannot create or get user")

    subscription = sub_service.get_active_subscription(user_id=user.id)

    if not subscription:
        return SubscriptionStatusResponse(
            user_exists=True,
            has_active_subscription=False,
            subscription=None,
        )

    # тут нам потрібні план і сервер
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
