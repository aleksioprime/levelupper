# 🌬️ Apache Airflow в Smart Learning Platform

Airflow используется для автоматизации ETL процессов и синхронизации данных между PostgreSQL и Elasticsearch в нашей образовательной платформе.

## 📋 Обзор

### Архитектура
- **Airflow Webserver** - веб-интерфейс для управления DAG'ами (порт 8304)
- **Airflow Scheduler** - планировщик выполнения задач
- **PostgreSQL** - база данных Airflow (та же, что у основного приложения)
- **Redis** - брокер сообщений и кэш

### Основные DAG'и

#### `sync_learning_data_to_elasticsearch`
Основной DAG для синхронизации образовательных данных с Elasticsearch.

**Расписание**: каждые 15 минут
**Задачи**:
1. `health_check_elasticsearch` - проверка доступности ES
2. `sync_courses_to_elasticsearch` - синхронизация курсов
3. `sync_topics_to_elasticsearch` - синхронизация тем курсов
4. `sync_lessons_to_elasticsearch` - синхронизация уроков

**Особенности синхронизации**:
- Инкрементальная синхронизация (только изменённые данные)
- Время последней синхронизации хранится в Redis
- Агрегация данных (количество записей, рейтинги)
- Обработка ошибок с логированием

## 🚀 Запуск и управление

### Доступ к веб-интерфейсу
```
URL: http://localhost:8304
Логин: admin (из переменной AIRFLOW_ADMIN_USERNAME)
Пароль: (из переменной AIRFLOW_ADMIN_PASSWORD)
```

### Переменные окружения
Настройте в `.env` файле:
```env
# Airflow Admin
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=your_password
AIRFLOW_ADMIN_FIRSTNAME=Admin
AIRFLOW_ADMIN_LASTNAME=User
AIRFLOW_ADMIN_EMAIL=admin@example.com

# База данных (используется общая с приложением)
POSTGRES_USER=learning_user
POSTGRES_PASSWORD=learning_password
POSTGRES_DB=learning_db

# Redis
REDIS_URL=redis://redis:6379/0
```

### Команды Docker Compose
```bash
# Запуск всех сервисов (включая Airflow)
docker-compose up -d

# Просмотр логов Airflow
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Остановка только Airflow
docker-compose stop airflow-webserver airflow-scheduler

# Перезапуск после изменения DAG'ов
docker-compose restart airflow-scheduler
```

## 🗂️ Структура файлов

```
back/airflow/
├── README.md              # Этот файл
├── init.sh               # Скрипт инициализации
└── dags/                 # DAG'и
    └── sync_courses_to_elastic.py
```

## 📊 Мониторинг и отладка

### Логи
- **Webserver**: `./back/airflow/logs/scheduler/`
- **Scheduler**: `./back/airflow/logs/dag_processor_manager/`
- **Task logs**: доступны через веб-интерфейс

### Основные метрики
- Статус выполнения DAG'ов
- Время выполнения задач
- Количество синхронизированных записей
- Ошибки подключения к внешним сервисам

### Типичные проблемы

**DAG не появляется в интерфейсе**
```bash
# Проверьте синтаксис Python
python /path/to/dag/file.py

# Перезапустите scheduler
docker-compose restart airflow-scheduler
```

**Ошибки подключения к БД/ES**
```bash
# Проверьте доступность сервисов
docker-compose ps
docker-compose logs elasticsearch
docker-compose logs postgres
```

**Задачи падают с импортами**
- Убедитесь, что все зависимости установлены в образе Airflow
- Проверьте пути импортов в DAG файлах

## 🔧 Разработка

### Добавление нового DAG'а
1. Создайте файл в `back/airflow/dags/`
2. Используйте стандартную структуру:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'smart-learning',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG('my_dag', default_args=default_args, schedule_interval='@daily')
```

### Тестирование задач
```bash
# Тест конкретной задачи
docker exec -it learning-airflow-scheduler airflow tasks test sync_learning_data_to_elasticsearch health_check_elasticsearch 2024-01-01

# Запуск DAG'а вручную
docker exec -it learning-airflow-scheduler airflow dags trigger sync_learning_data_to_elasticsearch
```

### Отладка синхронизации
```bash
# Очистка кэша синхронизации в Redis
docker exec -it learning-redis redis-cli
> DEL sync:courses:last_updated_at
> DEL sync:topics:last_updated_at
> DEL sync:lessons:last_updated_at
```

## 📈 Производительность

### Оптимизация
- Используйте инкрементальную синхронизацию
- Настройте подходящий `schedule_interval`
- Ограничивайте `max_active_runs=1` для предотвращения конфликтов
- Используйте пулы соединений для БД

### Масштабирование
Для больших объёмов данных рассмотрите:
- Разбиение синхронизации на более мелкие задачи
- Использование Airflow Executors (Celery, Kubernetes)
- Кэширование промежуточных результатов

## 🔗 Связанные компоненты

- **Elasticsearch**: индексы `courses`, `topics`, `lessons`
- **PostgreSQL**: таблицы `courses`, `course_topics`, `lessons`, `enrollments`, `assignments`
- **Redis**: кэш времени последней синхронизации
- **Backend API**: использует данные из Elasticsearch для поиска