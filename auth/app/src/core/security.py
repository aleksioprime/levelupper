import http
from typing import Optional, Set, Union

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.token import JWTHelper
from src.core.config import settings


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )

        # Проверяем service token
        service_token_result = self._check_service_token(credentials.credentials)
        if service_token_result:
            return service_token_result

        # Проверяем JWT token
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )

        return decoded_token

    def _check_service_token(self, token: str) -> Optional[dict]:
        """Проверяет service token"""
        if settings.service_token and token == settings.service_token:
            # Возвращаем объект как от JWT для service аутентификации
            return {
                "sub": "00000000-0000-0000-0000-000000000000",
                "is_superuser": True,  # Service token имеет максимальные права
                "service_auth": True
            }
        return None

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        payload = JWTHelper().decode(jwt_token)
        return payload