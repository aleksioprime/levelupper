"""Базовые модели и миксины для SQLAlchemy"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.postgres import Base
from src.utils.time import utc_now


class UUIDMixin:
    """Миксин для добавления UUID в качестве первичного ключа"""

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


class TimestampMixin:
    """Миксин для добавления временных меток создания и обновления"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base", "UUIDMixin", "TimestampMixin"]