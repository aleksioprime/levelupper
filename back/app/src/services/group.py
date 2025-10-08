from uuid import UUID
from typing import List

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException
from src.repositories.uow import UnitOfWork
from src.schemas.group import GroupSchema, GroupUpdateSchema, GroupDetailSchema, GroupCreateSchema
from src.schemas.enrollment import EnrollmentSchema, EnrollmentCreateSchema, EnrollmentUpdateSchema, EnrollmentListSchema
from src.constants.enrollment import EnrollmentRole


class GroupService:
    """
    Сервис для управления группами
    """
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self) -> List[GroupSchema]:
        """
        Выдаёт список всех групп
        """
        async with self.uow:
            groups = await self.uow.group.get_all()

        return groups

    async def get_detail_by_id(self, group_id: UUID) -> GroupDetailSchema:
        """
        Выдаёт детальную информацию о группе по её ID
        """
        async with self.uow:
            group = await self.uow.group.get_detail_by_id(group_id)
            if not group:
                raise BaseException(f"Группа с ID {group_id} не найдена")
        return group

    async def create(self, body: GroupCreateSchema) -> GroupSchema:
        """
        Создаёт новую группу
        """
        async with self.uow:
            try:
                created_group = await self.uow.group.create(body)
            except IntegrityError as exc:
                raise BaseException("Ошибка ограничения целостности данных в базе данных") from exc

        return created_group

    async def update(self, group_id: UUID, body: GroupUpdateSchema) -> GroupSchema:
        """
        Обновляет информацию о группе по её ID
        """
        async with self.uow:
            try:
                updated_group = await self.uow.group.update(group_id, body)
            except NoResultFound as exc:
                raise BaseException(f"Группа с ID {group_id} не найдена") from exc
        return updated_group

    async def delete(self, group_id: UUID) -> None:
        """
        Удаляет группу по её ID
        """
        async with self.uow:
            try:
                await self.uow.group.delete(group_id)
            except NoResultFound as exc:
                raise BaseException(f"Группа с ID {group_id} не найдена") from exc

    async def add_enrollment(self, group_id: UUID, body: EnrollmentCreateSchema) -> EnrollmentSchema:
        """
        Добавляет участника в группу
        """
        async with self.uow:
            try:
                # Проверяем, существует ли группа
                group = await self.uow.group.get_by_id(group_id)
                if not group:
                    raise BaseException(f"Группа с ID {group_id} не найдена")

                # Добавляем участника
                enrollment = await self.uow.enrollment.add_enrollment(
                    group_id=group_id,
                    user_id=body.user_id,
                    role=body.role,
                    status=body.status
                )
                return EnrollmentSchema.model_validate(enrollment)
            except IntegrityError as exc:
                raise BaseException("Пользователь уже является участником этой группы") from exc

    async def remove_enrollment(self, group_id: UUID, user_id: UUID) -> None:
        """
        Удаляет участника из группы
        """
        async with self.uow:
            try:
                await self.uow.enrollment.remove_enrollment(group_id, user_id)
            except NoResultFound as exc:
                raise BaseException(f"Участник не найден в группе") from exc

    async def update_enrollment(self, group_id: UUID, user_id: UUID, body: EnrollmentUpdateSchema) -> EnrollmentSchema:
        """
        Обновляет данные участника группы
        """
        async with self.uow:
            try:
                enrollment = None
                if body.role is not None:
                    enrollment = await self.uow.enrollment.update_enrollment_role(group_id, user_id, body.role)
                if body.status is not None:
                    enrollment = await self.uow.enrollment.update_enrollment_status(group_id, user_id, body.status)

                if enrollment is None:
                    # Если ничего не обновлялось, просто получаем текущую запись
                    enrollment = await self.uow.enrollment.get_enrollment(group_id, user_id)
                    if not enrollment:
                        raise NoResultFound()

                return EnrollmentSchema.model_validate(enrollment)
            except NoResultFound as exc:
                raise BaseException(f"Участник не найден в группе") from exc

    async def get_group_enrollments(self, group_id: UUID) -> EnrollmentListSchema:
        """
        Получает список участников группы
        """
        async with self.uow:
            group = await self.uow.group.get_by_id(group_id)
            if not group:
                raise BaseException(f"Группа с ID {group_id} не найдена")

            enrollments = await self.uow.enrollment.get_group_enrollments(group_id)
            enrollment_schemas = [EnrollmentSchema.model_validate(enr) for enr in enrollments]
            return EnrollmentListSchema(enrollments=enrollment_schemas)

    async def add_student(self, group_id: UUID, user_id: UUID) -> EnrollmentSchema:
        """
        Добавляет студента в группу
        """
        body = EnrollmentCreateSchema(user_id=user_id, role=EnrollmentRole.STUDENT)
        return await self.add_enrollment(group_id, body)

    async def add_teacher(self, group_id: UUID, user_id: UUID) -> EnrollmentSchema:
        """
        Добавляет преподавателя в группу
        """
        body = EnrollmentCreateSchema(user_id=user_id, role=EnrollmentRole.TEACHER)
        return await self.add_enrollment(group_id, body)