from uuid import UUID
from pydantic import BaseModel, Field

from src.schemas.moderator import ModeratorSchema


class CourseSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор курса")
    title: str = Field(..., description="Название курса")
    description: str | None = Field(None, description="Описание курса")

    class Config:
        from_attributes = True


class CourseCreateSchema(BaseModel):
    title: str = Field(..., description="Название нового курса")
    description: str | None = Field(None, description="Описание курса")


class CourseUpdateSchema(BaseModel):
    title: str | None = Field(None, description="Новое название курса")
    description: str | None = Field(None, description="Новое описание курса")


class CourseDetailSchema(CourseSchema):
    moderators: list[ModeratorSchema] = Field(default_factory=list, description="Модераторы курса")