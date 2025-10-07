"""Схемы для работы с пользователями в микросервисной архитектуре"""

from typing import Optional
import uuid
from pydantic import BaseModel


class UserInfoSchema(BaseModel):
    """Информация о пользователе из auth-сервиса"""
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool
    is_active: bool = True


class EnrollmentWithUserInfo(BaseModel):
    """Запись в группу с информацией о пользователе"""
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    role: str
    status: str
    date_start: Optional[str] = None

    # Информация о пользователе из auth-сервиса (опционально)
    user_info: Optional[UserInfoSchema] = None

    class Config:
        from_attributes = True


class SubmissionWithUserInfo(BaseModel):
    """Отправка задания с информацией о студенте"""
    id: uuid.UUID
    student_id: uuid.UUID
    assignment_id: uuid.UUID
    score: Optional[int] = None
    submitted_at: str

    # Информация о студенте из auth-сервиса (опционально)
    student_info: Optional[UserInfoSchema] = None

    class Config:
        from_attributes = True


class GradeWithUserInfo(BaseModel):
    """Оценка с информацией о преподавателе"""
    id: uuid.UUID
    value: int
    comment: Optional[str] = None
    submission_id: uuid.UUID
    teacher_id: Optional[uuid.UUID] = None
    graded_at: str

    # Информация о преподавателе из auth-сервиса (опционально)
    teacher_info: Optional[UserInfoSchema] = None

    class Config:
        from_attributes = True


class CommentWithUserInfo(BaseModel):
    """Комментарий с информацией о преподавателе"""
    id: uuid.UUID
    text: str
    teacher_id: Optional[uuid.UUID] = None
    submission_id: Optional[uuid.UUID] = None
    question_id: Optional[uuid.UUID] = None
    created_at: str

    # Информация о преподавателе из auth-сервиса (опционально)
    teacher_info: Optional[UserInfoSchema] = None

    class Config:
        from_attributes = True