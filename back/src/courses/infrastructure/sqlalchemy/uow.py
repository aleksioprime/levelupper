from src.common.db.postgres import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.uow import AbstractUnitOfWork
from .repositories import (
    CourseRepository,
    LessonRepository,
    AssignmentRepository,
    EnrollmentRepository,
    LessonProgressRepository,
    AssignmentSubmissionRepository
)


class UnitOfWork(AbstractUnitOfWork):
    """Реализация Unit of Work для управления репозиториями и транзакциями."""

    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        # Инициализация всех репозиториев
        self.courses = CourseRepository(self.session)
        self.lessons = LessonRepository(self.session)
        self.assignments = AssignmentRepository(self.session)
        self.enrollments = EnrollmentRepository(self.session)
        self.lesson_progress = LessonProgressRepository(self.session)
        self.assignment_submissions = AssignmentSubmissionRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
