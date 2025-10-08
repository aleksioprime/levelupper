""" Репозиторий для работы с модераторами курсов """

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound

from src.models.course import CourseModerator


class ModeratorRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_moderator(self, course_id: UUID, user_id: UUID) -> CourseModerator:
        """ Добавляет модератора к курсу """
        moderator = CourseModerator(course_id=course_id, user_id=user_id)
        self.session.add(moderator)
        await self.session.flush()
        return moderator

    async def remove_moderator(self, course_id: UUID, user_id: UUID) -> None:
        """ Удаляет модератора курса """
        stmt = delete(CourseModerator).where(
            CourseModerator.course_id == course_id,
            CourseModerator.user_id == user_id
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise NoResultFound(f"Модератор {user_id} курса {course_id} не найден")

    async def get_course_moderators(self, course_id: UUID) -> list[CourseModerator]:
        """ Получает список модераторов курса """
        query = select(CourseModerator).where(CourseModerator.course_id == course_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_courses(self, user_id: UUID) -> list[CourseModerator]:
        """ Получает список курсов, которые модерирует пользователь """
        query = select(CourseModerator).where(CourseModerator.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def is_course_moderator(self, course_id: UUID, user_id: UUID) -> bool:
        """ Проверяет, является ли пользователь модератором курса """
        query = select(CourseModerator).where(
            CourseModerator.course_id == course_id,
            CourseModerator.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None