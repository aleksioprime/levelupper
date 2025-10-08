from uuid import UUID

from pydantic import BaseModel, Field


class UserJWT(BaseModel):
    """
    Схема для представления данных пользователя в JWT
    """
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    is_superuser: bool = False
    is_admin: bool = False
    token: str