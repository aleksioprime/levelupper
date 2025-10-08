from uuid import UUID

from pydantic import BaseModel, Field


class UserJWT(BaseModel):
    """
    Схема для представления данных пользователя в JWT
    """
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    is_superuser: bool = False
    token: str
    service_auth: bool = Field(default=False, description="Является ли это межсервисной аутентификацией")