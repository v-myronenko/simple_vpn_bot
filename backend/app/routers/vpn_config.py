# backend/app/routers/vpn_config.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Server
from app.schemas import VpnConfigResponse
from app.services import UserService, TrialService
from app.services.trial_service import TrialError
from app.utils.vless_config import build_vless_reality_url
from app.utils.vpn_qr import generate_qr_png_base64


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{telegram_id}/vpn/config", response_model=VpnConfigResponse)
def get_vpn_config(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    trial_service = TrialService(db)

    user = user_service.get_or_create_user(telegram_id=telegram_id)

    # Поки що — жорстко frankfurt-1 (як у PaymentService)
    server: Server | None = (
        db.query(Server)
        .filter(Server.name == "frankfurt-1", Server.is_active.is_(True))
        .first()
    )
    if not server:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default server 'frankfurt-1' not found.",
        )

    try:
        vpn_account, is_trial = trial_service.ensure_vpn_access(user=user, server=server)
    except TrialError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message},
        )

    if not vpn_account.uuid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VPN account UUID is missing.",
        )

    vless_url = build_vless_reality_url(uuid=vpn_account.uuid, server_name=server.name)
    qr_b64 = generate_qr_png_base64(vless_url)

    msg = (
        "VPN access granted via trial."
        if is_trial
        else "VPN access granted via active subscription."
    )

    return VpnConfigResponse(
        ok=True,
        message=msg,
        vless_url=vless_url,
        uuid=vpn_account.uuid,
        server_name=server.name,
        server_region=server.region,
        is_trial=is_trial,
        trial_end_at=vpn_account.trial_end_at if is_trial else None,
        qr_png_base64=qr_b64,
    )
