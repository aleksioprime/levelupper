# Архитектура взаимодействия с Auth-сервисом

## Обзор

В нашей микросервисной архитектуре сервис авторизации (auth) работает отдельно от основного приложения. Основные принципы взаимодействия:

1. **Не дублируем модель User** - модель пользователя существует только в auth-сервисе
2. **Используем только user_id** - в основных моделях храним только UUID пользователя
3. **Обогащаем данные по запросу** - получаем информацию о пользователях через HTTP API
4. **Кешируем при необходимости** - для производительности можем кешировать данные пользователей

## Изменения в моделях

### Удалена модель User
Модель `User` больше не существует в основном сервисе. Вместо неё:

```python
# Вместо связи с User используем только ID
class Enrollment(UUIDMixin, Base):
    # Ссылка на пользователя из auth-сервиса (только ID)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        comment="ID пользователя из auth-сервиса"
    )
    # НЕТ relationship с User!
```

### Обновлены все связанные модели
- `Enrollment.user_id` - только UUID, без foreign key
- `Submission.student_id` - только UUID
- `Grade.teacher_id` - только UUID
- `Comment.teacher_id` - только UUID

## Сервисы для взаимодействия

### AuthService
```python
from src.services.auth_service import auth_service

# Получить информацию о пользователе
user_info = await auth_service.get_user_info(user_id)

# Получить информацию о нескольких пользователях
users_info = await auth_service.get_users_info([user_id1, user_id2])

# Проверить существование пользователя
exists = await auth_service.verify_user_exists(user_id)
```

### UserInfoEnricher
```python
from src.dependencies.user_info import user_info_enricher

# Обогатить один объект
data = await enricher.enrich_with_user_info(enrollment_dict)

# Обогатить список объектов (батч-запрос)
data = await enricher.enrich_list_with_users_info(enrollments_list)
```

## Пример использования в сервисах

```python
class EnrollmentService:
    async def get_enrollment_by_id(
        self,
        enrollment_id: uuid.UUID,
        include_user_info: bool = False
    ) -> Optional[EnrollmentWithUserInfo]:
        # Получаем данные из БД
        enrollment = await self.db.get(Enrollment, enrollment_id)

        # Конвертируем в dict
        data = enrollment_to_dict(enrollment)

        # Обогащаем пользовательскими данными если нужно
        if include_user_info:
            data = await user_info_enricher.enrich_with_user_info(data)

        return EnrollmentWithUserInfo(**data)
```

## Схемы с пользовательской информацией

```python
class EnrollmentWithUserInfo(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    role: str
    status: str

    # Опциональная информация о пользователе
    user_info: Optional[UserInfoSchema] = None
```

## Эндпоинты API

```python
@router.get("/enrollments/{enrollment_id}")
async def get_enrollment(
    enrollment_id: uuid.UUID,
    include_user_info: bool = Query(False),
    service: EnrollmentService = Depends()
):
    return await service.get_enrollment_by_id(
        enrollment_id,
        include_user_info=include_user_info
    )
```

## Рекомендации

### 1. Валидация пользователей
Перед созданием записей проверяйте существование пользователей:

```python
async def create_enrollment(user_id: uuid.UUID, ...):
    # Проверяем существование пользователя
    if not await auth_service.verify_user_exists(user_id):
        raise HTTPException(404, "Пользователь не найден")

    # Создаем запись
    enrollment = Enrollment(user_id=user_id, ...)
```

### 2. Обогащение данных
Используйте параметр `include_user_info` для контроля обогащения:

```python
# Без пользовательских данных (быстро)
enrollments = await service.get_enrollments(include_user_info=False)

# С пользовательскими данными (медленнее, но полнее)
enrollments = await service.get_enrollments(include_user_info=True)
```

### 3. Батчинг запросов
Для списков всегда используйте батч-запросы:

```python
# ✅ Правильно - один запрос для всех пользователей
await enricher.enrich_list_with_users_info(items)

# ❌ Неправильно - запрос для каждого пользователя
for item in items:
    await enricher.enrich_with_user_info(item)
```

### 4. Обработка ошибок
Auth-сервис может быть недоступен:

```python
# Сервис должен работать даже если auth недоступен
user_info = await auth_service.get_user_info(user_id)
if user_info is None:
    # Продолжаем работу без пользовательских данных
    pass
```

### 5. Конфигурация
Добавьте в настройки URL auth-сервиса:

```python
# settings.py
class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://auth:8000"
    AUTH_SERVICE_TIMEOUT: float = 30.0
```

## Новые эндпоинты Auth-сервиса

Для поддержки микросервисной архитектуры в auth-сервис добавлены новые эндпоинты:

### 1. Получение одного пользователя
```http
GET /api/v1/users/{user_id}/
```
Возвращает информацию о пользователе по ID.

### 2. Батч-получение пользователей
```http
POST /api/v1/users/batch/
Content-Type: application/json

{
  "user_ids": ["uuid1", "uuid2", "uuid3"]
}
```
Возвращает:
```json
{
  "users": {
    "uuid1": {
      "id": "uuid1",
      "username": "user1",
      "email": "user1@example.com",
      ...
    },
    "uuid2": { ... }
  },
  "not_found": ["uuid3"]
}
```

### 3. Проверка существования пользователей
```http
POST /api/v1/users/exists/
Content-Type: application/json

{
  "user_ids": ["uuid1", "uuid2", "uuid3"]
}
```
Возвращает:
```json
{
  "exists": {
    "uuid1": true,
    "uuid2": true,
    "uuid3": false
  }
}
```

### Ограничения
- Максимум 100 пользователей в одном батч-запросе
- Все эндпоинты требуют авторизации
- Доступны для всех авторизованных пользователей

## Пример использования новых эндпоинтов

```python
# AuthService обновлен для использования новых эндпоинтов
class AuthService:
    async def get_users_info(self, user_ids: List[uuid.UUID]) -> Dict[uuid.UUID, UserInfo]:
        """Использует POST /api/v1/users/batch/"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_service_url}/api/v1/users/batch/",
                json={"user_ids": [str(uid) for uid in user_ids]}
            )
            data = response.json()
            return {
                uuid.UUID(uid): UserInfo(**user_data)
                for uid, user_data in data["users"].items()
            }

    async def verify_users_exist(self, user_ids: List[uuid.UUID]) -> Dict[uuid.UUID, bool]:
        """Использует POST /api/v1/users/exists/"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_service_url}/api/v1/users/exists/",
                json={"user_ids": [str(uid) for uid in user_ids]}
            )
            data = response.json()
            return {uuid.UUID(uid): exists for uid, exists in data["exists"].items()}
```

## Миграция существующего кода

1. Удалите все `relationship` с User из моделей
2. Замените `ForeignKey("users.id")` на обычные UUID поля
3. Обновите сервисы для работы через AuthService
4. Добавьте обогащение данных где необходимо
5. Обновите схемы и эндпоинты
6. **Деплойте обновленный auth-сервис с новыми эндпоинтами**