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


# Схемы для Elasticsearch и детального отображения
class GroupNestedSchema(BaseModel):
    """Схема для вложенной группы"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class ModeratorNestedSchema(BaseModel):
    """Схема для вложенного модератора"""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID


class LessonNestedSchema(BaseModel):
    """Схема для вложенного урока"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    order: int
    date: Optional[date] = None


class TopicNestedSchema(BaseModel):
    """Схема для вложенной темы"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    order: int
    lessons: List[LessonNestedSchema] = Field(default_factory=list)


class CourseDetailSchema(CourseSchema):
    moderators: list[ModeratorSchema] = Field(default_factory=list, description="Модераторы курса")
    topics: List[TopicNestedSchema] = Field(default_factory=list, description="Темы курса с уроками")


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
    """Параметры поиска курсов"""
    query: Optional[str] = Field(None, description="Поисковый запрос по названию и описанию")
    group_ids: Optional[List[UUID]] = Field(None, description="Список ID групп для фильтрации")
    moderator_ids: Optional[List[UUID]] = Field(None, description="Список ID модераторов для фильтрации")

    @property
    def page(self) -> int:
        """Номер страницы (начиная с 1)"""
        return (self.offset // self.limit) + 1

    @property
    def size(self) -> int:
        """Размер страницы"""
        return self.limit

    class Config:
        arbitrary_types_allowed = True