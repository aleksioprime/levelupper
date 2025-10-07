# Сервис авторизации

## Запуск сервиса

Подготовьте переменные окружения из файла `.env.example`.

Для создания ключей можно воспользоваться одним из способов:
```shell
python3 -c "import secrets; print(secrets.token_hex(32))"

python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_') for _ in range(64)))"
```

Запустите сервис локально:
```shell
docker-compose -p levelupper-auth up -d --build
```

Если выходит ошибка `exec /usr/src/app/entrypoint.sh: permission denied`, то нужно вручную установить флаг выполнения для entrypoint.sh в локальной системе:
```shell
chmod +x app/entrypoint.sh
```

Создание миграциий:
```shell
docker exec -it levelupper-auth-app alembic revision --autogenerate -m "init migration"
```

Применение миграции (при перезапуске сервиса делается автоматически):
```shell
docker exec -it levelupper-auth-app alembic upgrade head
```

Проверить базы:
```shell
docker exec -it levelupper-auth-postgres psql -U <пользователь> <база данных> -c "\dt"
```

Создание суперпользователя:
```shell
docker-compose -p levelupper-auth exec app python scripts/create_superuser.py --username superuser --password z7JBes --email admin@levelupper.ru
```