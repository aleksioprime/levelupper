"""Модели курса, группы и записи в группу"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Text, String, ForeignKey, Enum, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin
from src.constants.enrollment import EnrollmentRole, EnrollmentStatus


class Group(UUIDMixin, TimestampMixin, Base):
    """
    Модель группы.
    Привязана к курсу и содержит список записанных пользователей
    """
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    moodle_group_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    course: Mapped["Course"] = relationship(back_populates="groups", lazy="selectin")

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"Группа {self.name} курса {self.course.title}"


class Enrollment(UUIDMixin, Base):
    """
    Модель записи пользователя в группу.
    Определяет его роль, статус и период участия
    """
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group'),
    )

    role: Mapped[EnrollmentRole] = mapped_column(Enum(EnrollmentRole), nullable=False)
    status: Mapped[EnrollmentStatus] = mapped_column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE, nullable=False)
    date_start: Mapped[date | None] = mapped_column(Date)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)

    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    group: Mapped["Group"] = relationship(back_populates="enrollments", lazy="selectin")

    progress: Mapped["Progress"] = relationship(
        back_populates="enrollment",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"Запись user={self.user_id} group={self.group_id} role={self.role} status={self.status}"


__all__ = ["Group", "Enrollment"]