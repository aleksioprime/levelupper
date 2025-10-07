"""
Аутентификация для административной панели с использованием auth-сервиса
"""
import uuid
import httpx
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.core.config import settings


class AuthServiceClient:
    """Клиент для взаимодействия с auth-сервисом"""

    def __init__(self):
        self.auth_url = settings.auth_service.url
        self.timeout = settings.auth_service.timeout

    async def authenticate_user(self, username_or_email: str, password: str) -> dict | None:
        """
        Аутентифицирует пользователя через auth-сервис
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Предполагаем, что есть эндпоинт для аутентификации с логином/паролем
                response = await client.post(
                    f"{self.auth_url}/api/v1/auth/login",
                    json={
                        "username": username_or_email,
                        "password": password
                    }
                )

                if response.status_code == 200:
                    user_data = response.json()
                    # Проверяем права суперпользователя
                    if user_data.get("is_superuser", False):
                        return user_data

                return None

        except (httpx.RequestError, httpx.TimeoutException):
            return None

    async def get_user_info(self, user_id: str) -> dict | None:
        """
        Получает информацию о пользователе по ID
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_url}/api/v1/users/{user_id}/",
                    # Здесь может потребоваться добавить заголовки авторизации
                    # headers={"Authorization": f"Bearer {service_token}"}
                )

                if response.status_code == 200:
                    user_data = response.json()
                    # Проверяем права суперпользователя и активность
                    if (user_data.get("is_superuser", False) and
                        user_data.get("is_active", True)):
                        return user_data

                return None

        except (httpx.RequestError, httpx.TimeoutException):
            return None

    async def verify_token(self, token: str) -> dict | None:
        """
        Проверяет JWT токен через auth-сервис
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    user_data = response.json()
                    if user_data.get("is_superuser", False):
                        return user_data

                return None

        except (httpx.RequestError, httpx.TimeoutException):
            return None


class AdminAuth(AuthenticationBackend):
    """
    Аутентификация админки через auth-сервис
    """

    def __init__(self, secret_key: str):
        super().__init__(secret_key)
        self.auth_client = AuthServiceClient()

    async def login(self, request: Request) -> bool:
        """
        Аутентифицирует пользователя через auth-сервис
        """
        form = await request.form()
        username_or_email = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()

        if not username_or_email or not password:
            return False

        # Аутентификация через auth-сервис
        user_data = await self.auth_client.authenticate_user(username_or_email, password)

        if not user_data:
            return False

        # Сохраняем информацию о пользователе в сессии
        request.session.update({
            "user_id": str(user_data["id"]),
            "username": user_data.get("username", ""),
            "email": user_data.get("email", ""),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "is_superuser": user_data.get("is_superuser", False),
            "access_token": user_data.get("access_token")  # Если auth-сервис возвращает токен
        })

        return True

    async def logout(self, request: Request) -> bool:
        """
        Очищает сессию пользователя
        """
        # Можно добавить логику для инвалидации токена в auth-сервисе
        access_token = request.session.get("access_token")
        if access_token:
            try:
                async with httpx.AsyncClient(timeout=self.auth_client.timeout) as client:
                    await client.post(
                        f"{self.auth_client.auth_url}/api/v1/auth/logout",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
            except:
                pass  # Игнорируем ошибки при logout

        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        """
        Проверяет аутентификацию для каждого запроса
        """
        user_id = request.session.get("user_id")
        access_token = request.session.get("access_token")

        if not user_id:
            return None

        # Если есть токен, проверяем его валидность
        if access_token:
            user_data = await self.auth_client.verify_token(access_token)
            if user_data:
                # Обновляем данные сессии
                request.session.update({
                    "username": user_data.get("username", ""),
                    "email": user_data.get("email", ""),
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                })
                return user_data

        # Если токена нет или он невалиден, проверяем по user_id
        try:
            user_data = await self.auth_client.get_user_info(user_id)
            if user_data:
                return user_data
            else:
                # Пользователь больше не существует или не имеет прав
                request.session.clear()
                return None

        except Exception:
            return None