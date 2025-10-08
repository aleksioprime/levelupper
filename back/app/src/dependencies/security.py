from typing import List, Optional
from fastapi import Depends, HTTPException, Request, status

from src.schemas.security import UserJWT
from src.core.security import JWTBearer


def permission_required(
    admin: bool = False,
    allow_self: bool = False,
    user_id_param: str = "user_id",
):
    """
    Декоратор для проверки прав доступа пользователя к эндпоинту
    """
    def checker(
        user: UserJWT = Depends(JWTBearer()),
        request: Request = None,
    ):
        if getattr(user, "is_superuser", False):
            # Проверка доступа для суперпользователей
            return user

        if admin and getattr(user, "is_admin", False):
            # Проверка доступа для администраторов
            return user

        if allow_self:
            # Проверка доступа к собственным данным
            user_id = request.path_params.get(user_id_param)
            if str(getattr(user, "user_id")) == str(user_id):
                return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return checker