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


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    category_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("categories.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    level: Mapped[CourseLevel]
    status: Mapped[CourseStatus] = mapped_column(default=CourseStatus.draft)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category")
    author = relationship("User")