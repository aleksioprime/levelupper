from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer
from redis.asyncio import Redis

from src.common.db.redis import get_redis
from src.auth.presentation.dependencies.uow import get_unit_of_work
from src.auth.domain.uow import AbstractUnitOfWork
from src.auth.application.services.auth import AuthService
from src.common.utils.token import JWTHelper

http_bearer = HTTPBearer()


async def get_auth_service(
        uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
        redis: Annotated[Redis, Depends(get_redis)],
):
    jwt_helper = JWTHelper()
    return AuthService(uow, redis, jwt_helper)

