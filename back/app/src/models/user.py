"""Модели пользователей и прогресса обучения"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class User(UUIDMixin, TimestampMixin, Base):
    """
    Модель пользователя.
    Представляет основную информацию о пользователе системы.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Пользователь {self.username} ({self.email})"


class Progress(UUIDMixin, TimestampMixin, Base):
    """
    Модель прогресса обучения студента в группе.
    Отслеживает общий прогресс и статистику по курсу.
    """
    __tablename__ = "progress"

    completion_percentage: Mapped[float] = mapped_column(default=0.0, nullable=False)
    total_assignments: Mapped[int] = mapped_column(default=0, nullable=False)
    completed_assignments: Mapped[int] = mapped_column(default=0, nullable=False)
    average_score: Mapped[float | None] = mapped_column()

    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    enrollment: Mapped["Enrollment"] = relationship(back_populates="progress")

    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"Прогресс {self.completion_percentage}% (enrollment={self.enrollment_id})"


__all__ = ["User", "Progress"]