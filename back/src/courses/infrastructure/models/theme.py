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


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"))
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("themes.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column()
    is_required: Mapped[bool] = mapped_column(default=True)

    course = relationship("Course", backref="themes")
    parent = relationship("CourseTheme", remote_side=[id], backref="subthemes")