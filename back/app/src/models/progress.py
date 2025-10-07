"""Модели прогресса обучения для микросервисной архитектуры

В данном сервисе мы не храним модель User, так как пользователи управляются 
отдельным сервисом авторизации. Мы работаем только с user_id (UUID) и 
обращаемся к auth-сервису за информацией о пользователях через API.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, UUIDMixin, TimestampMixin


class Progress(UUIDMixin, TimestampMixin, Base):
    """
    Модель прогресса обучения студента в группе.
    Отслеживает общий прогресс и статистику по курсу.
    """
    __tablename__ = "progress"

    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_assignments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_assignments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_score: Mapped[float | None] = mapped_column(Float)

    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    enrollment: Mapped["Enrollment"] = relationship(back_populates="progress")

    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"Прогресс {self.completion_percentage}% (enrollment={self.enrollment_id})"


__all__ = ["Progress"]