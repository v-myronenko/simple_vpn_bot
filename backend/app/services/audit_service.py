from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog, User


class AuditService:
    """
    Мінімальний сервіс для запису важливих подій у audit_logs.
    """

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        event_type: str,
        source: str,
        level: str = "info",
        user: User | None = None,
        telegram_id: int | None = None,
        object_type: str | None = None,
        object_id: int | None = None,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
        commit: bool = False,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user.id if user else None,
            telegram_id=telegram_id,
            source=source,
            event_type=event_type,
            level=level,
            object_type=object_type,
            object_id=object_id,
            description=description,
            meta=json.dumps(meta, ensure_ascii=False) if meta else None,
        )

        self.db.add(entry)

        if commit:
            self.db.commit()
            self.db.refresh(entry)

        return entry
