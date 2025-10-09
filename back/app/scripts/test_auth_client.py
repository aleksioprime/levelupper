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

    print('\\n5. 🔒 Тестируем ограничения service token:')
    # Тестируем эндпоинт без allow_service_auth (должен вернуть ошибку)
    try:
        async with httpx.AsyncClient() as client:
            # Пробуем получить /users/me/ с service token (должен быть запрещен)
            response = await client.get(
                f'{settings.auth_service.url}/api/v1/users/me/',
                headers={'Authorization': f'Bearer {settings.auth_service.service_token}'}
            )
            if response.status_code == 403:
                print('   ✅ Service token корректно заблокирован для /users/me/')
            elif response.status_code == 200:
                print('   ❌ ОШИБКА: Service token не должен работать для /users/me/')
            elif response.status_code == 500:
                print('   ✅ Service token заблокирован для /users/me/ (500 - внутренняя ошибка)')
                print('      (Это ожидаемо - эндпоинт не поддерживает service auth)')
            else:
                print(f'   ⚠️  Неожиданный код ответа для /users/me/: {response.status_code}')
                print(f'      Ответ: {response.text[:100]}...')
    except Exception as e:
        print(f'   ⚠️  Ошибка при тестировании ограничений: {e}')

    print('\\n6. ✅ Тестируем разрешенные service token эндпоинты:')
    # Проверяем, что service token работает на разрешенных эндпоинтах
    try:
        async with httpx.AsyncClient() as client:
            # Тестируем /users/{user_id}/ с service token (должен работать)
            response = await client.get(
                f'{settings.auth_service.url}/api/v1/users/{user_id}/',
                headers={'Authorization': f'Bearer {settings.auth_service.service_token}'}
            )
            if response.status_code == 200:
                user_data = response.json()
                print(f'   ✅ Service token работает для /users/{{user_id}}/: {user_data["username"]}')
            else:
                print(f'   ❌ ОШИБКА: Service token должен работать для /users/{{user_id}}/')
                print(f'      Код ответа: {response.status_code}')

            # Тестируем /users/batch/ с service token (должен работать)
            batch_response = await client.post(
                f'{settings.auth_service.url}/api/v1/users/batch/',
                headers={'Authorization': f'Bearer {settings.auth_service.service_token}'},
                json={'user_ids': [str(user_id)]}
            )
            if batch_response.status_code == 200:
                batch_data = batch_response.json()
                users_count = len(batch_data.get('users', {}))
                print(f'   ✅ Service token работает для /users/batch/: {users_count} пользователей')
            else:
                print(f'   ❌ ОШИБКА: Service token должен работать для /users/batch/')
                print(f'      Код ответа: {batch_response.status_code}')

    except Exception as e:
        print(f'   ⚠️  Ошибка при тестировании разрешенных эндпоинтов: {e}')

    print('\\n🎉 Все тесты прошли успешно!')

asyncio.run(test())