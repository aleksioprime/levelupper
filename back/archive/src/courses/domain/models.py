from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from src.common.enums.course import CourseLevel, CourseStatus
from src.common.enums.lesson import LessonType, LessonStatus, AssignmentType, SubmissionStatus
from src.common.enums.enrollment import EnrollmentStatus, ProgressStatus


@dataclass
class Course:
    """Доменная сущность курса."""

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

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        author_id: UUID,
        level: CourseLevel = CourseLevel.beginner,
        price: Optional[Decimal] = None,
        duration_hours: Optional[int] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        max_students: Optional[int] = None
    ) -> "Course":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            title=title,
            description=description,
            author_id=author_id,
            level=level,
            status=CourseStatus.draft,
            price=price,
            duration_hours=duration_hours,
            created_at=now,
            updated_at=now,
            tags=tags or [],
            image_url=image_url,
            is_free=price is None or price == 0,
            max_students=max_students
        )


@dataclass
class Lesson:
    """Доменная сущность урока."""

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
    materials: List[Dict[str, Any]]  # Дополнительные материалы
    is_free_preview: bool

    @classmethod
    def create(
        cls,
        course_id: UUID,
        title: str,
        content: str,
        lesson_type: LessonType,
        order_index: int,
        duration_minutes: Optional[int] = None,
        video_url: Optional[str] = None,
        materials: Optional[List[Dict[str, Any]]] = None,
        is_free_preview: bool = False
    ) -> "Lesson":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            course_id=course_id,
            title=title,
            content=content,
            lesson_type=lesson_type,
            status=LessonStatus.draft,
            order_index=order_index,
            duration_minutes=duration_minutes,
            created_at=now,
            updated_at=now,
            video_url=video_url,
            materials=materials or [],
            is_free_preview=is_free_preview
        )


@dataclass
class Assignment:
    """Доменная сущность задания."""

    id: UUID
    lesson_id: UUID
    title: str
    description: str
    assignment_type: AssignmentType
    questions: List[Dict[str, Any]]  # Вопросы и варианты ответов
    max_score: int
    passing_score: int
    time_limit_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_required: bool

    @classmethod
    def create(
        cls,
        lesson_id: UUID,
        title: str,
        description: str,
        assignment_type: AssignmentType,
        questions: List[Dict[str, Any]],
        max_score: int,
        passing_score: int,
        time_limit_minutes: Optional[int] = None,
        is_required: bool = True
    ) -> "Assignment":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            lesson_id=lesson_id,
            title=title,
            description=description,
            assignment_type=assignment_type,
            questions=questions,
            max_score=max_score,
            passing_score=passing_score,
            time_limit_minutes=time_limit_minutes,
            created_at=now,
            updated_at=now,
            is_required=is_required
        )


@dataclass
class Enrollment:
    """Доменная сущность записи на курс."""

    id: UUID
    user_id: UUID
    course_id: UUID
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime]
    progress_percentage: float
    last_accessed_at: Optional[datetime]
    certificate_issued: bool

    @classmethod
    def create(cls, user_id: UUID, course_id: UUID) -> "Enrollment":
        return cls(
            id=uuid4(),
            user_id=user_id,
            course_id=course_id,
            status=EnrollmentStatus.enrolled,
            enrolled_at=datetime.utcnow(),
            completed_at=None,
            progress_percentage=0.0,
            last_accessed_at=None,
            certificate_issued=False
        )


@dataclass
class LessonProgress:
    """Доменная сущность прогресса по уроку."""

    id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    status: ProgressStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_spent_minutes: int

    @classmethod
    def create(cls, enrollment_id: UUID, lesson_id: UUID) -> "LessonProgress":
        return cls(
            id=uuid4(),
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
            status=ProgressStatus.not_started,
            started_at=None,
            completed_at=None,
            time_spent_minutes=0
        )


@dataclass
class AssignmentSubmission:
    """Доменная сущность ответа на задание."""

    id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    answers: Dict[str, Any]  # Ответы пользователя
    score: Optional[int]
    status: SubmissionStatus
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    feedback: Optional[str]
    attempt_number: int

    @classmethod
    def create(
        cls,
        assignment_id: UUID,
        enrollment_id: UUID,
        answers: Dict[str, Any],
        attempt_number: int = 1
    ) -> "AssignmentSubmission":
        return cls(
            id=uuid4(),
            assignment_id=assignment_id,
            enrollment_id=enrollment_id,
            answers=answers,
            score=None,
            status=SubmissionStatus.submitted,
            submitted_at=datetime.utcnow(),
            graded_at=None,
            feedback=None,
            attempt_number=attempt_number
        )
