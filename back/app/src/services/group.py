from uuid import UUID
from typing import List

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException
from src.models.group import Group
from src.repositories.uow import UnitOfWork
from src.schemas.group import GroupSchema, GroupUpdateSchema, GroupDetailSchema


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

    async def create(self, body: GroupUpdateSchema) -> GroupSchema:
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