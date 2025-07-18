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


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("categories.id"))
    is_visible: Mapped[bool] = mapped_column(default=True)

    parent: Mapped[Optional[Category]] = relationship("Category", remote_side=[id], backref="children")