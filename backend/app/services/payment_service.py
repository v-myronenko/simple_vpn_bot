from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Plan, Server, Subscription, Payment
from app.services.subscription_service import SubscriptionService


class PaymentService:
    """Сервіс для роботи з оплатами та створенням підписок."""

    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    # --- Внутрішні хелпери ---

    def _get_or_create_user(self, telegram_id: int) -> User:
        user: User | None = (
            self.db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )
        if user:
            return user

        # Створюємо нового юзера (мову поки не знаємо)
        user = User(
            telegram_id=telegram_id,
            language=None,
            created_at=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _get_basic_plan(self) -> Plan:
        plan: Plan | None = (
            self.db.query(Plan)
                .filter(
                    Plan.code == "basic_30d",
                    Plan.is_active.is_(True),
                )
                .first()
        )
        if not plan:
            raise ValueError("Plan 'basic_30d' not found. Run seed or create this plan.")
        return plan

    def _get_default_server(self) -> Server:
        server: Server | None = (
            self.db.query(Server)
                .filter(
                    Server.name == "frankfurt-1",
                    Server.is_active.is_(True),
                )
                .first()
        )
        if not server:
            raise ValueError("Default server 'frankfurt-1' not found. Run seed or create server.")
        return server

    # --- Публічний метод ---

    def process_telegram_stars_payment(self, telegram_id: int) -> tuple[Subscription, Payment]:
        """
        Обробка успішної оплати через Telegram Stars.

        MVP-логіка:
        - беремо/створюємо юзера по telegram_id
        - беремо дефолтний план (basic_30d)
        - беремо дефолтний сервер (frankfurt-1)
        - якщо вже є активна підписка:
            - продовжуємо її: створюємо НОВУ підписку зі start_at = max(now, end_at старої)
        - якщо немає — створюємо першу підписку
        - створюємо запис у payments зі статусом 'success'
        """

        now = datetime.utcnow()  # naive UTC, як і у моделях

        # 1. Юзер
        user = self._get_or_create_user(telegram_id=telegram_id)

        # 2. План і сервер
        plan = self._get_basic_plan()
        server = self._get_default_server()

        # 3. Перевірити, чи є вже активна підписка
        active_sub = self.subscription_service.get_active_subscription(user_id=user.id)

        duration = timedelta(days=plan.duration_days)

        if active_sub:
            # Якщо вже є активна — продовжуємо з кінця поточної
            start_at = max(now, active_sub.end_at)
        else:
            # Інакше починаємо з "зараз"
            start_at = now

        end_at = start_at + duration

        # 4. Створюємо нову підписку
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
        self.db.flush()  # щоб зʼявився new_sub.id

        # 5. Створюємо платіж (спрощено: сума = планова ціна в Stars)
        payment = Payment(
            user_id=user.id,
            subscription_id=new_sub.id,
            provider="telegram_stars",
            amount_stars=plan.price_stars,
            currency="XTR",
            status="success",
            provider_charge_id=None,  # поки не використовуємо конкретний charge_id
            created_at=now,
            paid_at=now,
        )
        self.db.add(payment)

        # 6. Фіксуємо все
        self.db.commit()
        self.db.refresh(new_sub)
        self.db.refresh(payment)

        return new_sub, payment
