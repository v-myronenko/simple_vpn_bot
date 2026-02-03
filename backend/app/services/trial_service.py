# backend/app/services/trial_service.py

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, Server, VPNAccount
from app.services.subscription_service import SubscriptionService
from app.services.vpn_provider_3xui import ThreeXUIProvider


class TrialError(Exception):
    """Помилка, пов'язана з trial-доступом."""

    def __init__(self, code: str, message: str) -> None:
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

    def __init__(self, db: Session) -> None:
        self.db = db
        self.subscription_service = SubscriptionService(db)

    def _get_or_create_vpn_account(self, user: User, server: Server) -> VPNAccount:
        """
        Для тріалу:
        - якщо є ХОЧ ОДИН VPNAccount для користувача+сервера -> повертаємо його,
          незалежно від is_active (нам важливі поля trial_*)
        - якщо немає жодного -> створюємо нового клієнта в 3x-ui
        """
        vpn_acc: VPNAccount | None = (
            self.db.query(VPNAccount)
            .filter(
                VPNAccount.user_id == user.id,
                VPNAccount.server_id == server.id,
            )
            .order_by(VPNAccount.id.desc())
            .first()
        )
        if vpn_acc:
            return vpn_acc

        # Клієнта ще ніколи не було -> створюємо вперше
        provider = ThreeXUIProvider(server)
        email = f"tg_{user.telegram_id}@svpn"
        client = provider.create_client(email=email)

        vpn_acc = VPNAccount(
            user_id=user.id,
            server_id=server.id,
            protocol="vless_reality",
            uuid=client.uuid,
            external_id=None,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(vpn_acc)
        return vpn_acc

    def ensure_vpn_access(self, user: User, server: Server) -> tuple[VPNAccount, bool]:
        """
        Повертає (vpn_account, is_trial).

        Логіка:
        - якщо є активна підписка -> повертаємо акаунт, is_trial=False
        - якщо немає підписки:
            - якщо тріал ще не стартував -> стартуємо
            - якщо тріал іде -> ok
            - якщо тріал закінчився / вже був -> TrialError
        """
        now = datetime.utcnow()

        active_sub = self.subscription_service.get_active_subscription(user_id=user.id)

        vpn_acc = self._get_or_create_vpn_account(user=user, server=server)

        # Підписка завжди важливіша за тріал
        if active_sub:
            return vpn_acc, False

        # Немає підписки → дивимось на тріал
        if vpn_acc.trial_started_at is not None:
            # вже стартував
            if vpn_acc.trial_end_at and now <= vpn_acc.trial_end_at:
                return vpn_acc, True

            raise TrialError(
                code="trial_expired",
                message="Trial period has already expired.",
            )

        # Ще не стартував
        if vpn_acc.trial_used:
            # прапорець каже, що вже колись був
            raise TrialError(
                code="no_trial_left",
                message="Trial has already been used.",
            )

        # Старт тріалу зараз
        vpn_acc.trial_started_at = now
        vpn_acc.trial_end_at = now + timedelta(days=self.TRIAL_DAYS)
        vpn_acc.trial_used = True

        self.db.add(vpn_acc)
        self.db.commit()
        self.db.refresh(vpn_acc)

        return vpn_acc, True
