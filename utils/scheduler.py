from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from sqlalchemy import select
from db.base import get_session
from db.models import Subscription, SubStatus

def setup_scheduler(app):
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(_expire_subscriptions, "interval", hours=12, id="expire_subs")
    scheduler.start()
    app.job_queue  # keep reference

def _expire_subscriptions():
    now = datetime.utcnow()
    with get_session() as s:
        subs = s.scalars(select(Subscription).where(Subscription.status == SubStatus.ACTIVE)).all()
        for sub in subs:
            if sub.expires_at <= now:
                sub.status = SubStatus.EXPIRED
        s.commit()
