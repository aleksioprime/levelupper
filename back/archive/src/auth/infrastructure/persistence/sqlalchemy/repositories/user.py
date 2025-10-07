from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
import logging

from sqlalchemy import update, select, func
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash

from src.auth.domain.repositories.user import BaseUserRepository
from src.auth.infrastructure.persistence.sqlalchemy.models.user import User as ORMUser
from src.auth.infrastructure.persistence.sqlalchemy.repositories.base import BaseSQLRepository
from src.auth.infrastructure.persistence.sqlalchemy.mappers import orm_to_domain, domain_to_orm
from src.auth.application.schemas.user import UserUpdateSchema, UpdatePasswordUserSchema, UserQueryParams

logger = logging.getLogger(__name__)


class UserRepository(BaseUserRepository, BaseSQLRepository):

    async def get_user_by_id(self, user_id: UUID):
        """
        Получает пользователя по его ID
        """
        query = select(ORMUser).filter(ORMUser.id == user_id)
        result = await self.session.execute(query)
        orm_user = result.scalars().unique().one_or_none()
        return orm_to_domain(orm_user) if orm_user else None

    async def get_user_all(self, params: UserQueryParams):
        """ Получает список всех пользователей """
        query = (
            select(ORMUser)
            .limit(params.limit)
            .offset(params.offset)
        )
        result = await self.session.execute(query)
        orm_users = result.scalars().unique().all()
        users = [orm_to_domain(u) for u in orm_users]
        total = await self._count_all_users()
        return users, total

    async def _count_all_users(self) -> int:
        query = select(func.count()).select_from(ORMUser)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, user: ORMUser) -> None:
        """ Добавляет нового пользователя в текущую сессию """
        orm_user = domain_to_orm(user)
        self.session.add(orm_user)

    async def update(self, user_id: UUID, body: UserUpdateSchema) -> ORMUser:
        """ Обновляет пользователя по его ID """
        update_data = {key: value for key, value in body.dict(exclude_unset=True).items()}
        if not update_data:
            raise NoResultFound("Нет данных для обновления")

        stmt = (
            update(ORMUser)
            .filter_by(id=user_id)
            .values(**update_data)
        )
        await self.session.execute(stmt)
        return await self.get_user_by_id(user_id)

    async def delete(self, user_id: UUID) -> None:
        """ Удаляет пользователя по его ID """
        stmt = select(ORMUser).filter(ORMUser.id == user_id)
        result = await self.session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            raise NoResultFound(f"Пользователь с ID {user_id} не найден")

        await self.session.delete(orm_user)

    async def update_password(self, user_id: UUID, body: UpdatePasswordUserSchema) -> None:
        """ Обновляет пароль пользователя по его ID """
        if not body.password:
            raise NoResultFound("Нет данных для обновления")

        hashed_password = generate_password_hash(body.password)

        stmt = (
            update(ORMUser)
            .where(ORMUser.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self.session.execute(stmt)

    async def update_photo(self, user_id: UUID, photo: str) -> None:
        """ Обновляет фотографию пользователя по его ID """
        stmt = (
            update(ORMUser)
            .where(ORMUser.id == user_id)
            .values(photo=photo)
        )
        await self.session.execute(stmt)
