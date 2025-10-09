from uuid import UUID
from typing import List
import math

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException
from src.repositories.uow import UnitOfWork
from src.repositories.elasticsearch.course import CourseElasticSearchRepository
from src.schemas.course import CourseSchema, CourseUpdateSchema, CourseDetailSchema, CourseCreateSchema, CourseQueryParams
from src.schemas.moderator import ModeratorSchema, ModeratorListSchema
from src.schemas.pagination import PaginatedResponse



class CourseService:
    """
    Сервис для управления курсами
    """
    def __init__(self, uow: UnitOfWork, elasticsearch: CourseElasticSearchRepository):
        self.uow = uow
        self.elasticsearch = elasticsearch

    async def get_all(self) -> List[CourseSchema]:
        """
        Выдаёт список всех курсов
        """
        async with self.uow:
            courses = await self.uow.course.get_all()

        return courses

    async def get_detail_by_id(self, course_id: UUID) -> CourseDetailSchema:
        """
        Выдаёт детальную информацию о курсе по его ID
        """
        async with self.uow:
            course = await self.uow.course.get_detail_by_id(course_id)
            if not course:
                raise BaseException(f"Курс с ID {course_id} не найден")
        return course

    async def search_courses(self, params: CourseQueryParams) -> PaginatedResponse[CourseDetailSchema]:
        """Поиск курсов"""
        try:
            courses, total = await self.elasticsearch.search_courses(params)

            items = [CourseDetailSchema.model_validate(course) for course in courses]

            return PaginatedResponse[CourseDetailSchema](
                items=items,
                total=total,
                limit=params.limit,
                offset=params.offset,
                has_next=(params.offset + 1) * params.limit < total,
                has_previous=params.offset > 0
            )

        except Exception as e:
            raise BaseException(f"Ошибка поиска курсов") from e

    async def create(self, body: CourseCreateSchema) -> CourseSchema:
        """
        Создаёт новый курс
        """
        async with self.uow:
            try:
                created_course = await self.uow.course.create(body)
            except IntegrityError as exc:
                raise BaseException("Ошибка ограничения целостности данных в базе данных") from exc

        return created_course

    async def update(self, course_id: UUID, body: CourseUpdateSchema) -> CourseSchema:
        """
        Обновляет информацию о курсе по его ID
        """
        async with self.uow:
            try:
                updated_course = await self.uow.course.update(course_id, body)
            except NoResultFound as exc:
                raise BaseException(f"Курс с ID {course_id} не найден") from exc
        return updated_course

    async def delete(self, course_id: UUID) -> None:
        """
        Удаляет курс по его ID
        """
        async with self.uow:
            try:
                await self.uow.course.delete(course_id)
            except NoResultFound as exc:
                raise BaseException(f"Курс с ID {course_id} не найден") from exc

    async def add_moderator(self, course_id: UUID, user_id: UUID) -> ModeratorSchema:
        """
        Добавляет модератора к курсу
        """
        async with self.uow:
            try:
                course = await self.uow.course.get_by_id(course_id)
                if not course:
                    raise BaseException(f"Курс с ID {course_id} не найден")

                moderator = await self.uow.course_moderator.add_moderator(course_id, user_id)
                return ModeratorSchema.model_validate(moderator)
            except IntegrityError as exc:
                raise BaseException("Пользователь уже является модератором этого курса") from exc

    async def remove_moderator(self, course_id: UUID, user_id: UUID) -> None:
        """
        Удаляет модератора курса
        """
        async with self.uow:
            try:
                await self.uow.course_moderator.remove_moderator(course_id, user_id)
            except NoResultFound as exc:
                raise BaseException(f"Модератор не найден") from exc

    async def get_course_moderators(self, course_id: UUID) -> ModeratorListSchema:
        """
        Получает список модераторов курса
        """
        async with self.uow:
            course = await self.uow.course.get_by_id(course_id)
            if not course:
                raise BaseException(f"Курс с ID {course_id} не найден")

            moderators = await self.uow.course_moderator.get_course_moderators(course_id)
            moderator_schemas = [ModeratorSchema.model_validate(mod) for mod in moderators]
            return ModeratorListSchema(moderators=moderator_schemas)

    async def is_course_moderator(self, course_id: UUID, user_id: UUID) -> bool:
        """
        Проверяет, является ли пользователь модератором курса
        """
        async with self.uow:
            return await self.uow.course_moderator.is_course_moderator(course_id, user_id)