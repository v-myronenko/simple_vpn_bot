from sqlalchemy import select
from datetime import datetime, timedelta
from .base import get_session
from .models import User, Subscription, Payment, SubStatus, PaymentStatus

def get_or_create_user(tg_id: int, username: str | None = None):
    with get_session() as s:
        user = s.scalars(select(User).where(User.tg_id == tg_id)).first()
        if not user:
            user = User(tg_id=tg_id, username=username)
            s.add(user); s.commit(); s.refresh(user)
        return user

def create_payment(user_id: int, provider: str, amount: int, reference: str | None = None, meta: str | None = None):
    with get_session() as s:
        p = Payment(user_id=user_id, provider=provider, amount=amount, reference=reference, meta=meta)
        s.add(p); s.commit(); s.refresh(p)
        return p

def mark_payment_paid(payment_id: int):
    with get_session() as s:
        p = s.get(Payment, payment_id)
        if not p: return None
        p.status = PaymentStatus.PAID
        s.commit(); s.refresh(p)
        return p

def activate_or_extend_subscription(user_id: int, plan: str = "monthly", days: int = 31, server_location: str | None = None, uuid: str | None = None):
    with get_session() as s:
        sub = s.scalars(select(Subscription).where(Subscription.user_id == user_id, Subscription.status == SubStatus.ACTIVE)).first()
        now = datetime.utcnow()
        if sub:
            sub.expires_at = max(sub.expires_at, now) + timedelta(days=days)
        else:
            sub = Subscription(
                user_id=user_id, status=SubStatus.ACTIVE, plan=plan,
                server_location=server_location, uuid=uuid,
                started_at=now, expires_at=now + timedelta(days=days)
            )
            s.add(sub)
        s.commit(); s.refresh(sub)
        return sub

def get_active_subscription_by_tg(tg_id: int):
    from .base import get_session
    from sqlalchemy import select
    with get_session() as s:
        return s.execute(
            select(Subscription).join(Subscription.user).where(User.tg_id == tg_id, Subscription.status == SubStatus.ACTIVE)
        ).scalar_one_or_none()
