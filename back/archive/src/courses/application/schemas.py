from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from src.common.enums.course import CourseLevel, CourseStatus
from src.common.enums.lesson import LessonType, LessonStatus, AssignmentType, SubmissionStatus
from src.common.enums.enrollment import EnrollmentStatus, ProgressStatus


# === Course Schemas ===
class CourseCreateSchema(BaseModel):
    """Схема для создания курса."""
    title: str = Field(..., min_length=1, max_length=255, description="Название курса")
    description: str = Field(..., min_length=1, description="Описание курса")
    author_id: UUID = Field(..., description="ID автора курса")
    level: Optional[CourseLevel] = Field(CourseLevel.beginner, description="Уровень сложности")
    price: Optional[Decimal] = Field(None, ge=0, description="Цена курса")
    duration_hours: Optional[int] = Field(None, ge=1, description="Длительность в часах")
    tags: Optional[List[str]] = Field([], description="Теги курса")
    image_url: Optional[str] = Field(None, description="URL изображения курса")
    max_students: Optional[int] = Field(None, ge=1, description="Максимальное количество студентов")


class CourseUpdateSchema(BaseModel):
    """Схема для обновления курса."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    level: Optional[CourseLevel] = None
    status: Optional[CourseStatus] = None
    price: Optional[Decimal] = Field(None, ge=0)
    duration_hours: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    max_students: Optional[int] = Field(None, ge=1)


class CourseSchema(BaseModel):
    """Схема для возврата данных курса."""
    id: UUID
    title: str
    description: str
    author_id: UUID
    level: CourseLevel
    status: CourseStatus
    price: Optional[Decimal]
    duration_hours: Optional[int]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    image_url: Optional[str]
    is_free: bool
    max_students: Optional[int]

    class Config:
        from_attributes = True


# === Lesson Schemas ===
class LessonCreateSchema(BaseModel):
    """Схема для создания урока."""
    course_id: UUID = Field(..., description="ID курса")
    title: str = Field(..., min_length=1, max_length=255, description="Название урока")
    content: str = Field(..., min_length=1, description="Содержание урока")
    lesson_type: LessonType = Field(..., description="Тип урока")
    order_index: int = Field(..., ge=0, description="Порядковый номер урока")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Длительность в минутах")
    video_url: Optional[str] = Field(None, description="URL видео")
    materials: Optional[List[Dict[str, Any]]] = Field([], description="Дополнительные материалы")
    is_free_preview: Optional[bool] = Field(False, description="Бесплатный предпросмотр")


class LessonUpdateSchema(BaseModel):
    """Схема для обновления урока."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    lesson_type: Optional[LessonType] = None
    status: Optional[LessonStatus] = None
    order_index: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=1)
    video_url: Optional[str] = None
    materials: Optional[List[Dict[str, Any]]] = None
    is_free_preview: Optional[bool] = None


class LessonSchema(BaseModel):
    """Схема для возврата данных урока."""
    id: UUID
    course_id: UUID
    title: str
    content: str
    lesson_type: LessonType
    status: LessonStatus
    order_index: int
    duration_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    video_url: Optional[str]
    materials: List[Dict[str, Any]]
    is_free_preview: bool

    class Config:
        from_attributes = True


# === Assignment Schemas ===
class AssignmentCreateSchema(BaseModel):
    """Схема для создания задания."""
    lesson_id: UUID = Field(..., description="ID урока")
    title: str = Field(..., min_length=1, max_length=255, description="Название задания")
    description: str = Field(..., min_length=1, description="Описание задания")
    assignment_type: AssignmentType = Field(..., description="Тип задания")
    questions: List[Dict[str, Any]] = Field(..., description="Вопросы и варианты ответов")
    max_score: int = Field(..., ge=1, description="Максимальный балл")
    passing_score: int = Field(..., ge=0, description="Проходной балл")
    time_limit_minutes: Optional[int] = Field(None, ge=1, description="Ограничение по времени")
    is_required: bool = Field(True, description="Обязательное задание")

    @validator('passing_score')
    def validate_passing_score(cls, v, values):
        if 'max_score' in values and v > values['max_score']:
            raise ValueError('passing_score cannot be greater than max_score')
        return v


class AssignmentUpdateSchema(BaseModel):
    """Схема для обновления задания."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    assignment_type: Optional[AssignmentType] = None
    questions: Optional[List[Dict[str, Any]]] = None
    max_score: Optional[int] = Field(None, ge=1)
    passing_score: Optional[int] = Field(None, ge=0)
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None


class AssignmentSchema(BaseModel):
    """Схема для возврата данных задания."""
    id: UUID
    lesson_id: UUID
    title: str
    description: str
    assignment_type: AssignmentType
    questions: List[Dict[str, Any]]
    max_score: int
    passing_score: int
    time_limit_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_required: bool

    class Config:
        from_attributes = True


# === Enrollment Schemas ===
class EnrollmentCreateSchema(BaseModel):
    """Схема для записи на курс."""
    user_id: UUID = Field(..., description="ID пользователя")
    course_id: UUID = Field(..., description="ID курса")


class EnrollmentSchema(BaseModel):
    """Схема для возврата данных о записи на курс."""
    id: UUID
    user_id: UUID
    course_id: UUID
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime]
    progress_percentage: float
    last_accessed_at: Optional[datetime]
    certificate_issued: bool

    class Config:
        from_attributes = True


# === Lesson Progress Schemas ===
class LessonProgressUpdateSchema(BaseModel):
    """Схема для обновления прогресса по уроку."""
    time_spent_minutes: int = Field(..., ge=0, description="Время, потраченное на урок")


class LessonProgressSchema(BaseModel):
    """Схема для возврата данных о прогрессе по уроку."""
    id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    status: ProgressStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_spent_minutes: int

    class Config:
        from_attributes = True


# === Assignment Submission Schemas ===
class AssignmentSubmissionCreateSchema(BaseModel):
    """Схема для отправки ответа на задание."""
    assignment_id: UUID = Field(..., description="ID задания")
    enrollment_id: UUID = Field(..., description="ID записи на курс")
    answers: Dict[str, Any] = Field(..., description="Ответы пользователя")


class AssignmentSubmissionGradeSchema(BaseModel):
    """Схема для оценки задания."""
    score: int = Field(..., ge=0, description="Оценка")
    feedback: Optional[str] = Field(None, description="Обратная связь")
    status: SubmissionStatus = Field(..., description="Статус")


class AssignmentSubmissionSchema(BaseModel):
    """Схема для возврата данных об ответе на задание."""
    id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    answers: Dict[str, Any]
    score: Optional[int]
    status: SubmissionStatus
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    feedback: Optional[str]
    attempt_number: int

    class Config:
        from_attributes = True


# === Search and Filter Schemas ===
class CourseSearchSchema(BaseModel):
    """Схема для поиска курсов."""
    query: Optional[str] = Field(None, description="Поисковый запрос")
    level: Optional[CourseLevel] = Field(None, description="Уровень сложности")
    status: Optional[CourseStatus] = Field(None, description="Статус курса")
    is_free: Optional[bool] = Field(None, description="Бесплатный курс")
    tags: Optional[List[str]] = Field(None, description="Теги")
    price_from: Optional[Decimal] = Field(None, ge=0, description="Цена от")
    price_to: Optional[Decimal] = Field(None, ge=0, description="Цена до")
    author_id: Optional[UUID] = Field(None, description="ID автора")


class PaginationSchema(BaseModel):
    """Схема для пагинации."""
    limit: int = Field(10, ge=1, le=100, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение")


class PaginatedResponseSchema(BaseModel):
    """Схема для пагинированного ответа."""
    items: List[Any]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
