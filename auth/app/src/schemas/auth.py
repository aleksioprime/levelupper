from uuid import UUID

from pydantic import BaseModel, Field


class AuthSchema(BaseModel):
    """
    Схема для аутентификации пользователя.
    Определяет поля, необходимые для входа в систему
    """

    username: str = Field(..., description="Логин пользователя")
    password: str = Field(..., description="Пароль пользователя")
