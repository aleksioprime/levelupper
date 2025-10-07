from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from src.schemas.pagination import BasePaginationParams

class UserQueryParams(BasePaginationParams):

    class Config:
        arbitrary_types_allowed = True


class UserSchema(BaseModel):
    """
    Схема для представления данных пользователя
    """
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Логин пользователя")
    email: Optional[str] = Field(None, description="Email пользователя")
    is_superuser: Optional[bool] = Field(..., description="Суперпользователь")
    photo: str | None = Field(None, description="Изображение пользователя")

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """
    Схема для создание пользователя.
    Определяет поля, необходимые для создания нового пользователя
    """

    username: str = Field(..., description="Логин пользователя")
    password: str = Field(..., description="Пароль пользователя")
    email: str = Field(..., description="Email пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")


class UserUpdateSchema(BaseModel):
    """
    Схема для обновления данных пользователя
    """
    username: Optional[str] = Field(None, description="Логин пользователя для обновления")
    first_name: Optional[str] = Field(None, description="Имя пользователя для обновления")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя для обновления")
    email: Optional[str] = Field(None, description="Email пользователя")


class UpdatePasswordUserSchema(BaseModel):
    """
    Схема обновления пароля пользователя
    """
    password: str = Field(..., description="Пароль пользователя")


class BatchUserRequestSchema(BaseModel):
    """
    Схема для батч-запроса пользователей
    """
    user_ids: List[UUID] = Field(..., description="Список ID пользователей для получения", max_items=100)


class BatchUserResponseSchema(BaseModel):
    """
    Схема ответа для батч-запроса пользователей
    """
    users: dict[UUID, UserSchema] = Field(..., description="Словарь пользователей, где ключ - ID пользователя")
    not_found: List[UUID] = Field(default_factory=list, description="Список ID не найденных пользователей")


class UserExistsRequestSchema(BaseModel):
    """
    Схема для проверки существования пользователей
    """
    user_ids: List[UUID] = Field(..., description="Список ID пользователей для проверки", max_items=100)


class UserExistsResponseSchema(BaseModel):
    """
    Схема ответа для проверки существования пользователей
    """
    exists: dict[UUID, bool] = Field(..., description="Словарь существования пользователей")
