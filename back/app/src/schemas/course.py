from uuid import UUID
from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.schemas.moderator import ModeratorSchema
from src.schemas.pagination import BasePaginationParams


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


# Схемы для Elasticsearch
class GroupNestedSchema(BaseModel):
    """Схема для вложенной группы"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class ModeratorNestedSchema(BaseModel):
    """Схема для вложенного модератора"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID


class TopicNestedSchema(BaseModel):
    """Схема для вложенной темы"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    order: int


class CourseElasticsearchSchema(BaseModel):
    """Схема курса для Elasticsearch"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    groups: List[GroupNestedSchema] = Field(default_factory=list)
    moderators: List[ModeratorNestedSchema] = Field(default_factory=list)
    topics: List[TopicNestedSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CourseQueryParams(BasePaginationParams):
    ...

    class Config:
        arbitrary_types_allowed = True