# backend/app/services/trial_service.py

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Server, VPNAccount
from app.services.subscription_service import SubscriptionService
from app.services.vpn_provider_3xui import ThreeXUIProvider, VpnProviderError


class TrialError(Exception):
    """Помилка, пов'язана з trial-доступом."""

    def __init__(self, code: str, message: str):
        """
        code:
          - "trial_expired"   — тріал вже був і закінчився
          - "no_trial_left"   — тріал уже використовувався
        """
        self.code = code
        self.message = message
        super().__init__(message)


class TrialService:
    """
    Відповідає за:
    - старт тріалу при першому запиті конфігу
    - перевірку, чи тріал ще активний
    - пріоритет активної підписки над тріалом
    """

    TRIAL_DAYS = 3

    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    # ⚙️ окремий хелпер, щоб не чіпати PaymentService
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
            external_id=client.email,  # або інший external_id, якщо потім захочеш
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(vpn_acc)
        # commit робимо в публічному методі, щоб усе було атомарно
        return vpn_acc

    def ensure_vpn_access(self, user: User, server: Server) -> tuple[VPNAccount, bool]:
        """
        Головний метод.

        Повертає:
          (vpn_account, is_trial)

        Можливі сценарії:
        - є активна підписка -> повертаємо акаунт, is_trial = False
        - немає підписки, тріал ще не стартував -> стартуємо тріал, is_trial = True
        - немає підписки, тріал іде -> is_trial = True
        - немає підписки, тріал закінчився -> TrialError
        """
        now = datetime.utcnow()  # naive UTC, як у моделях

        # 1. Перевіряємо активну підписку
        active_sub = self.subscription_service.get_active_subscription(user_id=user.id)

        # 2. Гарантуємо наявність VPN-акаунта (створюємо клієнта в 3x-ui, якщо треба)
        vpn_acc = self._get_or_create_vpn_account(user=user, server=server)

        # Якщо є активна підписка — тріал нас не цікавить
        if active_sub:
            return vpn_acc, False

        # 3. Немає активної підписки — працюємо з тріалом

        # Якщо тріал уже колись стартував
        if vpn_acc.trial_started_at is not None:
            # якщо час ще не вийшов — ок, це "живий" тріал
            if vpn_acc.trial_end_at and now <= vpn_acc.trial_end_at:
                return vpn_acc, True

            # якщо час вийшов — тріал закінчився
            raise TrialError(
                code="trial_expired",
                message="Trial period has already expired.",
            )

        # Тут тріал ще не стартував.
        # Якщо при цьому trial_used = True — значить, щось вже колись пробували / мігрували.
        if getattr(vpn_acc, "trial_used", False):
            raise TrialError(
                code="no_trial_left",
                message="Trial has already been used.",
            )

        # 4. Стартуємо тріал ПРЯМО ЗАРАЗ (first use)
        vpn_acc.trial_started_at = now
        vpn_acc.trial_end_at = now + timedelta(days=self.TRIAL_DAYS)
        vpn_acc.trial_used = True

        self.db.add(vpn_acc)
        self.db.commit()
        self.db.refresh(vpn_acc)

        return vpn_acc, True
