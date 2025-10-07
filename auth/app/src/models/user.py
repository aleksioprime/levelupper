"""Модели пользователя"""

from datetime import datetime

from sqlalchemy import  DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash

from .base import Base, UUIDMixin, TimestampMixin


class User(UUIDMixin, TimestampMixin, Base):
    """
    Модель пользователя.
    Содержит основную информацию о пользователе, а также связанные роли
    """
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    photo: Mapped[str | None] = mapped_column(String(255))

    tg_username: Mapped[str | None] = mapped_column(String(255))
    tg_user_id: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def check_password(self, password: str) -> bool:
        """Проверка пароля пользователя"""
        return check_password_hash(self.hashed_password, password)

    def __repr__(self) -> str:
        return f"Пользователь: {self.username}"