from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ModeratorSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор записи")
    course_id: UUID = Field(..., description="ID курса")
    user_id: UUID = Field(..., description="ID пользователя-модератора")
    created_at: datetime = Field(..., description="Дата добавления модератора")

    class Config:
        from_attributes = True


class ModeratorCreateSchema(BaseModel):
    user_id: UUID = Field(..., description="ID пользователя для назначения модератором")


class ModeratorListSchema(BaseModel):
    moderators: list[ModeratorSchema] = Field(..., description="Список модераторов курса")