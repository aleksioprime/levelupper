""" Паттерн Unit of Work для управления транзакциями и репозиториями """

from src.db.postgres import async_session_maker
from src.repositories.course import CourseRepository
from src.repositories.group import GroupRepository
from src.repositories.moderator import ModeratorRepository
from src.repositories.enrollment import EnrollmentRepository


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()
        self.course = CourseRepository(self.session)
        self.group = GroupRepository(self.session)
        self.moderator = ModeratorRepository(self.session)
        self.enrollment = EnrollmentRepository(self.session)

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()