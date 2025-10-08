from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field

from src.constants.enrollment import EnrollmentRole, EnrollmentStatus


class EnrollmentSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор записи")
    group_id: UUID = Field(..., description="ID группы")
    user_id: UUID = Field(..., description="ID пользователя")
    role: EnrollmentRole = Field(..., description="Роль пользователя в группе")
    status: EnrollmentStatus = Field(..., description="Статус участия")
    date_start: date | None = Field(None, description="Дата начала участия")

    class Config:
        from_attributes = True


class EnrollmentCreateSchema(BaseModel):
    user_id: UUID = Field(..., description="ID пользователя")
    role: EnrollmentRole = Field(..., description="Роль пользователя в группе")
    status: EnrollmentStatus = Field(EnrollmentStatus.ACTIVE, description="Статус участия")
    date_start: date | None = Field(None, description="Дата начала участия")


class EnrollmentUpdateSchema(BaseModel):
    role: EnrollmentRole | None = Field(None, description="Новая роль пользователя")
    status: EnrollmentStatus | None = Field(None, description="Новый статус участия")
    date_start: date | None = Field(None, description="Новая дата начала участия")


class EnrollmentListSchema(BaseModel):
    enrollments: list[EnrollmentSchema] = Field(..., description="Список участников группы")