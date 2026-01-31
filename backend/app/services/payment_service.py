from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Plan, Server, Subscription, Payment, VPNAccount
from app.services.subscription_service import SubscriptionService
from app.services.vpn_provider_3xui import ThreeXUIProvider, VpnProviderError


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

    def _get_or_create_vpn_account(self, user: User, server: Server) -> VPNAccount:
        """
        Для вказаного user+server:
        - якщо вже є активний VPNAccount -> повертаємо його
        - якщо немає -> створюємо клієнта в 3x-ui + запис у vpn_accounts
        """
        vpn_acc: VPNAccount | None = (
            self.db.query(VPNAccount)
            .filter(
                VPNAccount.user_id == user.id,
                VPNAccount.server_id == server.id,
                VPNAccount.is_active.is_(True),
            )
            .first()
        )
        if vpn_acc:
            return vpn_acc

        # Створюємо нового клієнта в 3x-ui
        provider = ThreeXUIProvider(server)

        # email у 3x-ui — це просто унікальний ідентифікатор, не обов'язково реальний e-mail
        email = f"tg_{user.telegram_id}@svpn"

        client = provider.create_client(email=email)

        vpn_acc = VPNAccount(
            user_id=user.id,
            server_id=server.id,
            protocol="vless_reality",
            uuid=client.uuid,
            external_id=None,  # можна буде зберігати clientId, якщо потім будемо його діставати
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(vpn_acc)
        # commit не робимо — хай це робить основний метод
        return vpn_acc

    def process_telegram_stars_payment(self, telegram_id: int) -> tuple[Subscription, Payment]:
        """
        Обробка успішної оплати через Telegram Stars.
        """
        now = datetime.utcnow()  # naive UTC, як і у моделях

        # 1. Юзер / план / сервер
        user = self._get_or_create_user(telegram_id=telegram_id)
        plan = self._get_basic_plan()
        server = self._get_default_server()

        # 2. Гарантуємо наявність VPN-акаунта (і клієнта в 3x-ui)
        vpn_account = self._get_or_create_vpn_account(user=user, server=server)

        # 3. Перевіряємо, чи є вже активна підписка
        active_sub = self.subscription_service.get_active_subscription(user_id=user.id)

        duration = timedelta(days=plan.duration_days)

        if active_sub:
            start_at = max(now, active_sub.end_at)
        else:
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
        self.db.flush()

        # 5. Створюємо платіж (як у тебе було)
        payment = Payment(
            user_id=user.id,
            subscription_id=new_sub.id,
            provider="telegram_stars",
            amount_stars=plan.price_stars,
            currency="XTR",
            status="success",
            provider_charge_id=None,
            created_at=now,
            paid_at=now,
        )
        self.db.add(payment)

        # 6. Фіксуємо
        self.db.commit()
        self.db.refresh(new_sub)
        self.db.refresh(payment)

        return new_sub, payment

