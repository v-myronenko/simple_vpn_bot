# db/repo.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import async_session_maker, User, Subscription


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    # якщо naive — вважаємо, що це UTC і додаємо tzinfo
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def get_or_create_user(telegram_id: int, username: Optional[str]) -> User:
    async with async_session_maker() as session:  # type: AsyncSession
        res = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user: Optional[User] = res.scalar_one_or_none()

        if user:
            if username is not None and user.username != username:
                user.username = username
                await session.commit()
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            created_at=utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def grant_trial_if_needed(user_id: int, trial_days: int = 7) -> bool:
    async with async_session_maker() as session:  # type: AsyncSession
        existed = await session.execute(
            select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        )
        cnt = existed.scalar_one() or 0
        if cnt > 0:
            return False

        now = utcnow()
        trial = Subscription(
            user_id=user_id,
            starts_at=now,
            expires_at=now + timedelta(days=trial_days),
            is_trial=True,
            created_at=now,
        )
        session.add(trial)
        await session.commit()
        return True


async def is_active(telegram_id: int) -> Tuple[bool, Optional[Subscription]]:
    """
    Повертає (active, last_subscription)
    """
    async with async_session_maker() as session:  # type: AsyncSession
        res_user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user: Optional[User] = res_user.scalar_one_or_none()
        if not user:
            return False, None

        res_sub = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )
        sub: Optional[Subscription] = res_sub.scalar_one_or_none()
        if not sub:
            return False, None

        # нормалізація дат (на випадок старих записів без tzinfo)
        sub.starts_at = _as_aware_utc(sub.starts_at)
        sub.expires_at = _as_aware_utc(sub.expires_at)
        sub.created_at = _as_aware_utc(sub.created_at)

        now = utcnow()
        active = bool(sub.expires_at and sub.expires_at > now)
        return active, sub


async def extend_subscription(user_id: int, days: int = 31) -> None:
    async with async_session_maker() as session:  # type: AsyncSession
        res = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )
        sub: Optional[Subscription] = res.scalar_one_or_none()
        now = utcnow()

        if sub and sub.expires_at and sub.expires_at > now:
            sub.expires_at = sub.expires_at + timedelta(days=days)
        else:
            sub = Subscription(
                user_id=user_id,
                starts_at=now,
                expires_at=now + timedelta(days=days),
                created_at=now,
                is_trial=False,
            )
            session.add(sub)

        await session.commit()