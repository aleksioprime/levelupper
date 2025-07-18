from __future__ import annotations
from typing import Optional, Annotated
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey, String, Text, Integer, DateTime, Boolean, Enum, Float,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
import enum


class UserCourseEnrollment(Base):
    __tablename__ = "user_course_enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"))
    status: Mapped[EnrollmentStatus] = mapped_column(default=EnrollmentStatus.enrolled)
    progress: Mapped[float] = mapped_column(default=0.0)
    enrolled_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# 📘 Открытие темы пользователю
class UserThemeAccess(Base):
    __tablename__ = "user_theme_access"
    __table_args__ = (UniqueConstraint("user_id", "theme_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    theme_id: Mapped[UUID] = mapped_column(ForeignKey("course_themes.id"))
    unlocked_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    unlocked_by: Mapped[str] = mapped_column(String(50))