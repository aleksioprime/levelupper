from uuid import UUID
from pydantic import BaseModel, Field

from src.schemas.enrollment import EnrollmentSchema


class GroupSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор группы")
    name: str = Field(..., description="Название группы")
    course_id: UUID = Field(..., description="ID курса")
    moodle_group_id: str | None = Field(None, description="ID группы в Moodle")

    class Config:
        from_attributes = True


class GroupCreateSchema(BaseModel):
    name: str = Field(..., description="Название новой группы")
    course_id: UUID = Field(..., description="ID курса")
    moodle_group_id: str | None = Field(None, description="ID группы в Moodle")


class GroupUpdateSchema(BaseModel):
    name: str | None = Field(None, description="Новое название группы")
    course_id: UUID | None = Field(None, description="Новый ID курса")
    moodle_group_id: str | None = Field(None, description="Новый ID группы в Moodle")


class GroupDetailSchema(GroupSchema):
    enrollments: list[EnrollmentSchema] = Field(default_factory=list, description="Участники группы")