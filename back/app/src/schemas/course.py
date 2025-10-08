from uuid import UUID
from pydantic import BaseModel, Field


class CourseSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор курса")
    name: str = Field(..., description="Название курса")

    class Config:
        from_attributes = True


class CourseCreateSchema(BaseModel):
    name: str = Field(..., description="Название нового курса")


class CourseUpdateSchema(BaseModel):
    name: str | None = Field(None, description="Новое название курса")


class CourseDetailSchema(CourseSchema):
    ...  # Здесь можно добавить дополнительные поля для детальной информации о курсе