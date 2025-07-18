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


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    theme_id: Mapped[UUID] = mapped_column(ForeignKey("course_themes.id"))
    title: Mapped[str] = mapped_column(String(255))
    type: Mapped[LessonType]
    content_url: Mapped[Optional[str]] = mapped_column(String(255))
    order: Mapped[int] = mapped_column()
    duration: Mapped[Optional[int]] = mapped_column()  # в секундах

    theme = relationship("CourseTheme", backref="lessons")