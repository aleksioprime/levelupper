"""Схемы для работы с пользователями в микросервисной архитектуре"""

from typing import Optional
import uuid
from pydantic import BaseModel



class UserInfo(BaseModel):
    """Модель информации о пользователе из auth-сервиса"""
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool
    is_active: bool = True