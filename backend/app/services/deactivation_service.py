from datetime import datetime

from sqlalchemy.orm import Session

from app.models import VPNAccount, Subscription
from app.services.subscription_service import SubscriptionService
from app.services.vpn_provider_3xui import ThreeXUIProvider


class DeactivationService:
    def __init__(self, db: Session):
        self.db = db
        self.sub_service = SubscriptionService(db)

    def deactivate_vpn_account(self, vpn: VPNAccount):
        provider = ThreeXUIProvider(vpn.server)

        try:
            provider.disable_client(uuid=vpn.uuid)
        except VpnProviderError as e:
            # Логуємо, але базу все одно оновлюємо, щоб не застрягло назавжди
            logger.warning(
                "Failed to disable client in 3x-ui (uuid=%s, server=%s): %s",
                vpn.uuid,
                vpn.server_id,
                e,
            )

        vpn.is_active = False
        self.db.add(vpn)

    def deactivate_expired_trials(self):
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
            # якщо зʼявилась активна підписка — НЕ відрубаємо
            active_sub = self.sub_service.get_active_subscription(vpn.user_id)
            if active_sub:
                continue

            self.deactivate_vpn_account(vpn)

        self.db.commit()

    def deactivate_expired_subscriptions(self):
        now = datetime.utcnow()

        subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.end_at < now,
                Subscription.status == "active",
            )
            .all()
        )

        for sub in subs:
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
                self.deactivate_vpn_account(vpn)

        self.db.commit()
