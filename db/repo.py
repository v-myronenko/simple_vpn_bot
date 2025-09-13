from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Subscription

UTC = timezone.utc

async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalar_one_or_none()
    if user:
        if username and user.username != username:
            user.username = username
            await session.flush()
        return user
    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.flush()
    return user

async def get_last_subscription(session: AsyncSession, user_id: int) -> Subscription | None:
    res = await session.execute(
        select(Subscription).where(Subscription.user_id == user_id).order_by(desc(Subscription.expires_at)).limit(1)
    )
    return res.scalar_one_or_none()

async def grant_trial_if_needed(session: AsyncSession, user_id: int, days: int = 7) -> Subscription | None:
    res = await session.execute(select(Subscription).where(Subscription.user_id == user_id))
    if res.first() is not None:
        return None
    now = datetime.now(UTC)
    sub = Subscription(user_id=user_id, starts_at=now, expires_at=now + timedelta(days=days), is_trial=1)
    session.add(sub)
    await session.flush()
    return sub

async def extend_subscription(session: AsyncSession, user_id: int, months: int) -> Subscription:
    last = await get_last_subscription(session, user_id)
    now = datetime.now(UTC)
    starts = last.expires_at if last and last.expires_at > now else now
    expires = starts + timedelta(days=30 * months)  # просто 30 днів/місяць для білінгу
    sub = Subscription(user_id=user_id, starts_at=starts, expires_at=expires, is_trial=0)
    session.add(sub)
    await session.flush()
    return sub

async def is_active(session: AsyncSession, user_id: int):
    last = await get_last_subscription(session, user_id)
    if not last:
        return False, None
    now = datetime.now(UTC)
    return (last.expires_at > now), last.expires_at
