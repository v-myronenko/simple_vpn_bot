# backend/app/routers/vpn_config.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Server
from app.schemas import VpnConfigResponse
from app.services import UserService, TrialService
from app.services.trial_service import TrialError


# Тут одразу ставимо фінальний префікс, як у user_subscription:
# /api/users/...
router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{telegram_id}/vpn/config", response_model=VpnConfigResponse)
def get_vpn_config(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    """
    Видає uuid VPN-клієнта + інфо по серверу.

    Логіка:
    - створюємо / беремо користувача
    - беремо дефолтний сервер (як у PaymentService)
    - TrialService:
      - якщо є активна підписка -> ок
      - якщо немає, але тріал ще не стартував -> старт тріалу
      - якщо тріал іде -> ок
      - якщо тріал закінчився -> 403
    """
    user_service = UserService(db)
    trial_service = TrialService(db)

    user = user_service.get_or_create_user(telegram_id=telegram_id)

    # Поки що жорстко використовуємо той самий дефолтний сервер, що й PaymentService
    server: Server | None = (
        db.query(Server)
        .filter(
            Server.name == "frankfurt-1",
            Server.is_active.is_(True),
        )
        .first()
    )
    if not server:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default server 'frankfurt-1' not found.",
        )

    try:
        vpn_account, is_trial = trial_service.ensure_vpn_access(
            user=user,
            server=server,
        )
    except TrialError as e:
        # Тріал закінчився / недоступний
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message},
        )

    if not vpn_account.uuid:
        # Це дуже малоймовірно, але на всяк випадок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VPN account UUID is missing.",
        )

    msg = (
        "VPN access granted via trial."
        if is_trial
        else "VPN access granted via active subscription."
    )

    return VpnConfigResponse(
        ok=True,
        message=msg,
        uuid=vpn_account.uuid,
        server_name=server.name,
        server_region=server.region,
        is_trial=is_trial,
        trial_end_at=vpn_account.trial_end_at if is_trial else None,
    )
