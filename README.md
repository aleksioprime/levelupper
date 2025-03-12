# Платформа образовательных курсов


## Запуск для разработчика

Скачайте репозиторий:
```
git clone https://github.com/aleksioprime/smart-learning.git
cd smart-learning
```

Запустите сервис локально:
```
docker-compose -p learning up -d --build
```

Если выходит ошибка `exec /usr/src/app/entrypoint.sh: permission denied`, то нужно вручную установить флаг выполнения для entrypoint.sh в локальной системе:
```
chmod +x auth/entrypoint.sh
```

Создание миграциий:
```shell
docker exec -it learning-auth alembic revision --autogenerate -m "init"
```

Применение миграции (при перезапуске сервиса делается автоматически):
```shell
docker exec -it learning-auth alembic upgrade head
```

Создание суперпользователя:
```shell
docker-compose -p learning exec auth python manage/create_superuser.py \
  --login superuser \
  --password 1q2w3e \
  --email admin@smartlearning.ru
```