import asyncio
import uuid
import sys
sys.path.append('/usr/src/app')
from src.services.user import auth_service
from src.core.config import settings

async def test():
    user_id = uuid.UUID('89ee9213-0207-4e76-b134-22f6c79d4ecf')

    print('=== Финальный тест всех возможностей ===')

    # Получаем токен пользователя
    import httpx
    async with httpx.AsyncClient() as client:
        auth_response = await client.post(
            f'{settings.auth_service.url}/api/v1/auth/login/',
            json={'username': 'admin', 'password': 'admin123'}
        )
        user_token = auth_response.json()['access_token']

    print('1. ✅ Service token (по умолчанию):')
    result1 = await auth_service.get_user_info(user_id)
    print(f'   Пользователь: {result1.username}')

    print('\\n2. ✅ User token:')
    result2 = await auth_service.get_user_info(user_id, user_token=user_token)
    print(f'   Пользователь: {result2.username}')

    print('\\n3. ✅ Convenience methods:')
    result3 = await auth_service.get_user_info_by_service(user_id)
    result4 = await auth_service.get_user_info_by_user(user_id, user_token)
    print(f'   Service method: {result3.username}')
    print(f'   User method: {result4.username}')

    print('\\n4. ✅ Батч-запросы:')
    batch1 = await auth_service.get_users_info_by_service([user_id])
    batch2 = await auth_service.get_users_info_by_user([user_id], user_token)
    print(f'   Батч service: {len(batch1)} пользователей')
    print(f'   Батч user: {len(batch2)} пользователей')

    print('\\n🎉 Все тесты прошли успешно!')

asyncio.run(test())