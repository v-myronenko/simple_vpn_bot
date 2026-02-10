from __future__ import annotations

from datetime import datetime

import logging
from sqlalchemy.orm import Session

from app.models import VPNAccount, Subscription
from app.services.subscription_service import SubscriptionService
from app.services.vpn_provider_3xui import ThreeXUIProvider, VpnProviderError
from app.services.audit_service import AuditService


logger = logging.getLogger(__name__)


class DeactivationService:
    """
    Сервіс, який:
    - відрубує VPN-акаунт у 3x-ui та ставить is_active = False
    - відключає прострочені trial-доступи
    - відключає прострочені підписки
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.sub_service = SubscriptionService(db)
        self.audit = AuditService(db)

    def deactivate_vpn_account(self, vpn: VPNAccount, reason: str = "manual_from_service") -> None:
        """
        Вимикає клієнта в 3x-ui (якщо можливо) і ставить is_active=False у БД.
        """
        provider = ThreeXUIProvider(vpn.server)

        try:
            provider.disable_client(uuid=vpn.uuid)
        except VpnProviderError as e:
            # Логуємо, але базу все одно оновлюємо, щоб не застрягло назавжди
            logger.warning(
                "Failed to disable client in 3x-ui",
                extra={
                    "extra": {
                        "uuid": vpn.uuid,
                        "server_id": vpn.server_id,
                        "error": str(e),
                    }
                },
            )

        vpn.is_active = False
        self.db.add(vpn)

        # Аудит
        self.audit.log(
            event_type="vpn_account.deactivated",
            source="script",
            level="info",
            user=vpn.user,
            telegram_id=vpn.user.telegram_id if vpn.user else None,
            object_type="vpn_account",
            object_id=vpn.id,
            description="VPN account deactivated",
            meta={
                "server_id": vpn.server_id,
                "reason": reason,
            },
        )

    def deactivate_expired_trials(self) -> None:
        """
        Відключає trial-доступи, в яких:
        - trial_used = True
        - trial_end_at < now
        - is_active = True
        - немає активної підписки (якщо є — НЕ чіпаємо)
        """
        now = datetime.utcnow()

        vpn_accounts = (
            self.db.query(VPNAccount)
            .filter(
                VPNAccount.trial_used.is_(True),
                VPNAccount.trial_end_at.isnot(None),
                VPNAccount.trial_end_at < now,
                VPNAccount.is_active.is_(True),
            )
            .all()
        )

        for vpn in vpn_accounts:
            # Якщо зʼявилась активна підписка — не відрубуємо
            active_sub = self.sub_service.get_active_subscription(vpn.user_id)
            if active_sub:
                continue

            self.deactivate_vpn_account(vpn, reason="trial_expired")

            self.audit.log(
                event_type="trial.auto_deactivated",
                source="script",
                level="info",
                user=vpn.user,
                telegram_id=vpn.user.telegram_id if vpn.user else None,
                object_type="vpn_account",
                object_id=vpn.id,
                description="Trial expired and VPN account deactivated by cron.",
                meta={
                    "trial_end_at": vpn.trial_end_at.isoformat() if vpn.trial_end_at else None,
                },
            )

        self.db.commit()

    def deactivate_expired_subscriptions(self) -> None:
        """
        Відключає VPN-доступи для прострочених підписок:
        - subscription.status = 'active'
        - subscription.end_at < now
        """
        now = datetime.utcnow()

        expired_subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.status == "active",
                Subscription.end_at.isnot(None),
                Subscription.end_at < now,
            )
            .all()
        )

        for sub in expired_subs:
            sub.status = "expired"
            self.db.add(sub)

            vpn_accounts = (
                self.db.query(VPNAccount)
                .filter(
                    VPNAccount.user_id == sub.user_id,
                    VPNAccount.server_id == sub.server_id,
                    VPNAccount.is_active.is_(True),
                )
                .all()
            )

            for vpn in vpn_accounts:
                self.deactivate_vpn_account(vpn, reason="subscription_expired")

            self.audit.log(
                event_type="subscription.deactivated_expired",
                source="script",
                level="info",
                user=sub.user,
                telegram_id=sub.user.telegram_id if sub.user else None,
                object_type="subscription",
                object_id=sub.id,
                description="Subscription expired and VPN access deactivated by cron.",
                meta={
                    "subscription_end_at": sub.end_at.isoformat() if sub.end_at else None,
                    "server_id": sub.server_id,
                },
            )

        self.db.commit()
