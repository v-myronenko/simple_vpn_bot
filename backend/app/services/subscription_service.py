from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Subscription


class SubscriptionService:
    """Сервіс для роботи з підписками."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_subscription(self, user_id: int) -> Subscription | None:
        """
        Повертає активну підписку користувача або None.

        Активна = статус 'active' + end_at > now.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)  # порівнюємо naive

        sub = (
            self.db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == "active",
                Subscription.end_at > now,
            )
            .order_by(Subscription.end_at.desc())
            .first()
        )

        return sub
