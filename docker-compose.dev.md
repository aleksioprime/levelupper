# Docker Compose для разработки

## Запуск проекта Learning

### Полный запуск всех сервисов
```bash
docker-compose -p learning up -d
```

### Запуск с пересборкой
```bash
docker-compose -p learning up -d --build
```

### Создание суперпользователя
```bash
docker-compose -p learning exec backend python scripts/create_superuser.py \
  --username superuser \
  --password 1q2w3e \
  --email admin@learning.ru
```

### Запуск отдельных сервисов
```bash
# Только база данных и кеш
docker-compose -p learning up -d postgres redis

# Добавить поиск
docker-compose -p learning up -d elasticsearch

# Добавить ETL
docker-compose -p learning up -d airflow-webserver airflow-scheduler

# Добавить приложение
docker-compose -p learning up -d backend frontend
```

## Доступные порты

- **Backend API**: http://localhost:8301
  - Swagger UI: http://localhost:8301/docs
  - SQLAdmin: http://localhost:8301/admin (admin/admin123)
- **Frontend**: http://localhost:8302 (dev) или http://localhost:8303 (prod)
- **PostgreSQL**: localhost:8305 (учебные_курсы/разработка/пароль123)
- **Redis**: localhost:8306
- **Elasticsearch**: http://localhost:8307
- **Airflow**: http://localhost:8308 (airflow/airflow)

## Переменные окружения

Создайте файл `.env` на основе `.env.example`

## Команды для разработки

### Перезапуск отдельного сервиса
```bash
docker-compose -p learning restart backend
docker-compose -p learning restart frontend
```

### Просмотр логов
```bash
docker-compose -p learning logs -f backend
docker-compose -p learning logs -f frontend
docker-compose -p learning logs -f airflow-webserver
```

### Подключение к контейнеру
```bash
docker-compose -p learning exec backend bash
docker-compose -p learning exec postgres psql -U разработка -d учебные_курсы
```

### Очистка и пересборка
```bash
docker-compose -p learning down -v  # Удалить тома
docker-compose -p learning build --no-cache  # Пересобрать без кеша
```

## Работа с миграциями

```bash
# Создание новой миграции
docker-compose -p learning exec backend alembic revision --autogenerate -m "описание изменения"

# Применение миграций
docker-compose -p learning exec backend alembic upgrade head

# Откат миграции
docker-compose -p learning exec backend alembic downgrade -1
```

## Наполнение тестовыми данными

```bash
# Создание суперпользователя
docker-compose -p learning exec backend python scripts/create_superuser.py

# Запуск синхронизации с Elasticsearch через Airflow
# Перейти в http://localhost:8380, включить DAG sync_courses_to_elastic
```

## Отладка

### Проблемы с подключением
1. Убедитесь, что все сервисы здоровы: `docker-compose -p learning ps`
2. Проверьте логи: `docker-compose -p learning logs [service-name]`
3. Проверьте сеть: `docker network ls`

### Проблемы с производительностью
1. Увеличьте память для Elasticsearch в docker-compose.yaml
2. Используйте volumes для кеширования зависимостей

### Очистка при проблемах
```bash
docker-compose -p learning down -v --remove-orphans
docker system prune -f
docker-compose -p learning up -d --force-recreate
```