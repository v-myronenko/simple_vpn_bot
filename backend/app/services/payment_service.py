from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Plan, Server, Subscription, Payment
from app.services.subscription_service import SubscriptionService


class PaymentService:
    """Сервіс для роботи з оплатами та створенням підписок."""

    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    def process_telegram_stars_payment(self, telegram_id: int) -> tuple[Subscription, Payment]:
        """
        Обробка успішної оплати через Telegram Stars.

        Спрощений MVP-варіант:
        - беремо юзера по telegram_id (створити якщо немає)
        - беремо дефолтний план (basic_30d)
        - беремо дефолтний сервер (frankfurt-1)
        - якщо вже є активна підписка:
            - продовжуємо її, створюючи НОВУ підписку з датою start_at = max(now, end_at старої)
        - створюємо запис у payments зі статусом 'success'
        """

        # 1. Юзер
        user: User | None = (
            self.db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )
        if not user:
            # імпорт тут, щоб уникнути циклічної залежності на рівні імпортів
            from app.services.user_service import UserService
            user = UserService(self.db).get_or_create_user(telegram_id=telegram_id)

        # 2. План (дефолтний: basic_30d)
        plan: Plan | None = (
            self.db.query(Plan)
            .filter(Plan.code == "basic_30d", Plan.is_active.is_(True))
            .first()
        )
        if not plan:
            raise ValueError("Active plan 'basic_30d' not found")

        duration_days = plan.duration_days or 30
        amount_stars = plan.price_stars or 1000

        # 3. Сервер (дефолтний: frankfurt-1)
        server: Server | None = (
            self.db.query(Server)
            .filter(Server.name == "frankfurt-1", Server.is_active.is_(True))
            .first()
        )
        if not server:
            # fallback: беремо будь-який активний
            server = (
                self.db.query(Server)
                .filter(Server.is_active.is_(True))
                .first()
            )
        if not server:
            raise ValueError("No active VPN server found")

        now = datetime.utcnow()

        # 4. Діюча підписка (для продовження)
        active_sub = self.subscription_service.get_active_subscription(user_id=user.id)

        if active_sub:
            # стару можна позначити неактивною (якщо хочеш)
            active_sub.status = "expired"

            # нова підписка починається з моменту закінчення старої або з now, що більше
            start_at = active_sub.end_at if active_sub.end_at > now else now
        else:
            start_at = now

        end_at = start_at + timedelta(days=duration_days)

        # 5. Створюємо нову підписку
        new_sub = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            server_id=server.id,
            status="active",
            start_at=start_at,
            end_at=end_at,
            created_at=now,
        )
        self.db.add(new_sub)
        self.db.flush()  # щоб new_sub.id зʼявився

        # 6. Записуємо платіж
        payment = Payment(
            user_id=user.id,
            subscription_id=new_sub.id,
            provider="telegram_stars",
            amount_stars=amount_stars,
            currency="XTR",
            status="success",
            provider_charge_id=None,  # поки що не використовуємо
            created_at=now,
            paid_at=now,
        )
        self.db.add(payment)

        self.db.commit()
        self.db.refresh(new_sub)
        self.db.refresh(payment)

        return new_sub, payment
