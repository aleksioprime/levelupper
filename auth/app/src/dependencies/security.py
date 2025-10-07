from typing import List, Optional
from fastapi import Depends, HTTPException, Request, status

from src.schemas.security import UserJWT
from src.core.security import JWTBearer


def permission_required(
    roles: Optional[List[str]] = None,
    allow_self: bool = False,
    user_id_param: str = "user_id",
):
    def checker(
        user: UserJWT = Depends(JWTBearer()),
        request: Request = None,
    ):
        if getattr(user, "is_superuser", False):
            return user

        if not roles and not allow_self:
            return user

        if roles:
            user_roles = getattr(user, "roles", [])
            if isinstance(user_roles, str):
                user_roles = [user_roles]
            if set(user_roles) & set(roles):
                return user

        if allow_self:
            user_id = request.path_params.get(user_id_param)
            if str(getattr(user, "user_id")) == str(user_id):
                return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return checker