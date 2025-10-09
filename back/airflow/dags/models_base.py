"""
Базовые модели для Airflow DAG'ов
Совместимость с SQLAlchemy 1.4.x
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# Создаем Base для моделей Airflow
Base = declarative_base()


class UUIDMixin:
    """Миксин для добавления UUID в качестве первичного ключа"""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )


class TimestampMixin:
    """Миксин для добавления временных меток создания и обновления"""

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base", "UUIDMixin", "TimestampMixin"]