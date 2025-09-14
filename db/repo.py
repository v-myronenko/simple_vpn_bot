from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Subscription


async def get_or_create_user(
    session: AsyncSession, *, telegram_id: int, username: Optional[str]
) -> User:
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalars().first()
    if user:
        # оновимо username, якщо змінився
        if username is not None and username != user.username:
            user.username = username
            await session.commit()
        return user

    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_active_subscription(session: AsyncSession, user_id: int) -> Optional[Subscription]:
    now = datetime.utcnow()
    res = await session.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.expires_at > now)
        .order_by(Subscription.expires_at.desc())
    )
    return res.scalars().first()


async def grant_trial_if_needed(session: AsyncSession, user_id: int, *, days: int = 7) -> Optional[Subscription]:
    """Видати триал, якщо у користувача зовсім немає підписок."""
    res = await session.execute(select(Subscription).where(Subscription.user_id == user_id))
    has_any = res.scalars().first()
    if has_any:
        return None

    now = datetime.utcnow()
    sub = Subscription(
        user_id=user_id,
        starts_at=now,
        expires_at=now + timedelta(days=days),
        is_trial=1,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub
