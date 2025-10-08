import time

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, decode

from src.core.config import settings
from src.schemas.security import UserJWT
from src.exceptions.base import BaseException


class JWTHelper:
    """
    Класс для работы с JWT токенами
    """

    def verify(self, token: str) -> dict:
        """
        Проверяет подлинность JWT токена
        """
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise BaseException('Token has expired')
        except jwt.InvalidTokenError:
            raise BaseException('Invalid token')

        return payload

    @staticmethod
    def decode(token: str) -> dict | None:
        """
        Проверяет подлинность и срок действия переданного JWT токена
        """

        try:
            decoded_token = decode(
                token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )

            if decoded_token["exp"] < time.time():
                return None

            user_data = {
                "user_id": decoded_token.get("sub"),
                "is_superuser": decoded_token.get("is_superuser", False),
                "is_admin": decoded_token.get("is_admin", False),
                "token": token,
            }

            return UserJWT(**user_data)
        except (ExpiredSignatureError, InvalidTokenError):
            return None