from abc import ABC, abstractmethod

from .repositories import (
    AbstractCourseRepository,
    AbstractLessonRepository,
    AbstractAssignmentRepository,
    AbstractEnrollmentRepository,
    AbstractLessonProgressRepository,
    AbstractAssignmentSubmissionRepository
)


class AbstractUnitOfWork(ABC):
    """Абстрактный Unit of Work для управления репозиториями и транзакциями."""

    courses: AbstractCourseRepository
    lessons: AbstractLessonRepository
    assignments: AbstractAssignmentRepository
    enrollments: AbstractEnrollmentRepository
    lesson_progress: AbstractLessonProgressRepository
    assignment_submissions: AbstractAssignmentSubmissionRepository

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...
