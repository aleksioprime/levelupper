# 🎓 Smart Learning Platform

Современная микросервисная платформа для управления учебными курсами с полнофункциональной системой онлайн-обучения. Включает создание курсов, управление уроками, задания различных типов, систему аутентификации, отслеживание прогресса и мощный поиск на базе Elasticsearch.

## ✨ Основные возможности

### 📚 Управление курсами
- Создание и редактирование курсов с различными уровнями сложности
- Богатый контент: текст, видео, интерактивные материалы
- Система тегов и категорий
- Гибкое ценообразование (бесплатные и платные курсы)

### 📖 Система уроков
- Множественные типы уроков: текст, видео, тесты, задания
- Последовательное изучение с отслеживанием прогресса
- Дополнительные материалы и ресурсы
- Предпросмотр бесплатных уроков

### ✅ Задания и оценивание
- Разнообразные типы заданий:
  - Множественный выбор
  - Единичный выбор
  - Ввод текста и кода
  - Загрузка файлов
  - Эссе
- Автоматическая и ручная проверка
- Система оценок и обратной связи
- Множественные попытки

### 📊 Отслеживание прогресса
- Детальная аналитика прохождения курсов
- Статистика времени изучения
- Индивидуальный прогресс по урокам
- Сертификаты о завершении

### 🔍 Мощный поиск
- Полнотекстовый поиск по Elasticsearch
- Фильтрация по уровню, цене, тегам
- Рекомендательная система
- Популярные и трендовые курсы

## 🏗️ Архитектура системы

### Микросервисная архитектура
Платформа построена на основе микросервисов с четким разделением ответственности:

- **Auth Service** (`auth/`) - сервис аутентификации и авторизации
- **Learning Service** (`back/`) - основной сервис управления курсами и обучением
- **Frontend** (`front/`) - пользовательский интерфейс
- **ETL Service** - Apache Airflow для синхронизации данных

## 🛠 Технологический стек

### Backend Services
- **FastAPI** - высокопроизводительный веб-фреймворк
- **SQLAlchemy 2.0** - современная ORM с асинхронной поддержкой
- **PostgreSQL** - надежная реляционная БД (мультитенантная)
- **Redis** - кэширование и управление сессиями
- **Elasticsearch 8.13** - полнотекстовый поиск и аналитика
- **Alembic** - управление миграциями БД
- **Pydantic V2** - валидация данных и сериализация

### Frontend
- **Vue.js 3** - прогрессивный JavaScript фреймворк
- **Vite** - быстрый сборщик и dev-сервер
- **Pinia** - современное управление состоянием
- **Nginx** - веб-сервер и reverse proxy

### ETL & Data Pipeline
- **Apache Airflow 2.9** - оркестрация ETL процессов
- **Инкрементальная синхронизация** - оптимизированная передача данных
- **Redis-кэширование** - отслеживание времени последней синхронизации

### DevOps & Инфраструктура
- **Docker & Docker Compose** - контейнеризация всех сервисов
- **Multi-stage builds** - оптимизация образов
- **Health checks** - мониторинг состояния сервисов
- **Volume management** - персистентное хранение данных

### Архитектурные паттерны
- **Microservices** - слабосвязанные независимые сервисы
- **Clean Architecture** - четкое разделение слоев
- **Domain-Driven Design** - фокус на бизнес-логике
- **Repository Pattern** - абстракция доступа к данным
- **Unit of Work** - управление транзакциями
- **CQRS** - разделение команд и запросов

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/aleksioprime/levelupper.git
cd levelupper
```

### 2. Настройка переменных окружения
```bash
# Основные переменные окружения
cp .env.example .env

# Настройки для auth сервиса
cp auth/.env.example auth/.env
```

Отредактируйте необходимые параметры

### 3. Запуск всех сервисов

Создайте сеть
```sh
docker network create levelupper-network
```

```bash
# Запустите все сервисы платформы
docker-compose -p levelupper up -d --build

# Проверьте статус всех контейнеров
docker-compose -p levelupper ps
```

### 4. Инициализация базы данных

Создание миграциий:
```shell
docker-compose -p levelupper exec backend alembic revision --autogenerate -m "init migration"
```

Применение миграции (при перезапуске сервиса делается автоматически):
```bash
# Примените миграции для основного сервиса
docker-compose -p levelupper exec backend alembic upgrade head
```

### 5. Инициализация Elasticsearch
```bash
# Создайте индексы Elasticsearch
docker-compose -p levelupper exec backend python -c "
import asyncio
from src.elasticsearch.models import create_indices
asyncio.run(create_indices())
"
```

### 6. Настройка Airflow
```bash
# Активируйте основной DAG синхронизации
# Зайдите в веб-интерфейс: http://localhost:8304
# Логин: admin, пароль: admin (или значения из .env)
# Включите DAG: sync_learning_data_to_elasticsearch
```

## 🌐 Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://localhost:8303 | Веб-интерфейс платформы |
| **Auth API** | http://localhost:8301 | API аутентификации |
| **Auth Docs** | http://localhost:8301/docs | Swagger документация Auth |
| **Learning API** | http://localhost:8302 | API управления курсами |
| **Learning Docs** | http://localhost:8302/docs | Swagger документация Learning |
| **Airflow** | http://localhost:8304 | Управление ETL процессами |

### Внутренние сервисы
| Сервис | Хост | Описание |
|--------|------|----------|
| **PostgreSQL** | postgres:5432 | Основная база данных |
| **Redis** | redis:6379 | Кэш и брокер сообщений |
| **Elasticsearch** | elasticsearch:9200 | Поисковый движок |

## 🔐 Административные панели

### Auth Service Admin
Управление пользователями и авторизацией:
- **URL**: http://localhost:8301/admin
- **Логин**: `admin` (создается при инициализации)
- **Возможности**: управление пользователями, ролями, токенами

### Learning Service Admin
Управление образовательным контентом:
- **URL**: http://localhost:8302/admin
- **Логин**: используйте токен от Auth сервиса
- **Возможности**:
  - Управление курсами и темами
  - Создание и редактирование уроков
  - Управление заданиями и тестами
  - Просмотр прогресса студентов
  - Проверка выполненных работ

### Airflow Admin
Управление ETL процессами:
- **URL**: http://localhost:8304
- **Логин**: admin/admin (настраивается в .env)
- **Возможности**:
  - Мониторинг синхронизации данных
  - Управление расписанием DAG'ов
  - Просмотр логов выполнения

## 🔗 API Endpoints

### Auth Service (порт 8301)
```
POST   /api/v1/auth/register     - Регистрация пользователя
POST   /api/v1/auth/login        - Авторизация пользователя
POST   /api/v1/auth/refresh      - Обновление токена
GET    /api/v1/auth/me           - Получение текущего пользователя
POST   /api/v1/auth/logout       - Выход из системы
GET    /admin/                   - Административная панель
```

### Learning Service (порт 8302)
```
# Курсы
GET    /api/v1/courses/          - Список курсов
POST   /api/v1/courses/          - Создание курса
GET    /api/v1/courses/{id}/     - Детали курса
PATCH  /api/v1/courses/{id}/     - Обновление курса

# Темы курсов
GET    /api/v1/topics/           - Список тем
POST   /api/v1/topics/           - Создание темы
GET    /api/v1/topics/{id}/      - Детали темы

# Уроки
GET    /api/v1/lessons/          - Список уроков
POST   /api/v1/lessons/          - Создание урока
GET    /api/v1/lessons/{id}/     - Детали урока

# Поиск
GET    /api/v1/search/courses/   - Поиск курсов в Elasticsearch
GET    /admin/                   - Административная панель
```

## 🔧 Разработка

### Структура проекта
```
levelupper/
├── auth/                    # Сервис аутентификации
│   ├── app/                # FastAPI приложение
│   ├── docker-compose.yaml # Локальная конфигурация
│   └── README.md          # Документация сервиса
├── back/                   # Основной learning сервис
│   ├── airflow/           # ETL и синхронизация данных
│   ├── app/               # FastAPI приложение
│   └── postgres/          # Скрипты инициализации БД
├── front/                  # Frontend приложение
│   ├── app/               # Vue.js приложение
│   └── nginx/             # Конфигурация Nginx
├── docker-compose.yaml     # Основная конфигурация
└── README.md              # Этот файл
```

### Разработка отдельных сервисов

#### Auth Service
```bash
cd auth
docker-compose up -d  # Запуск только auth сервиса
```

#### Learning Service
```bash
# Для разработки основного сервиса нужны зависимости (postgres, redis, elasticsearch)
docker-compose up -d postgres redis elasticsearch
cd back/app
python src/main.py  # Локальный запуск
```

#### Frontend
```bash
cd front/app
npm install
npm run dev  # Режим разработки с hot reload
```

### Полезные команды разработки
```bash
# Перезапуск конкретного сервиса
docker-compose restart backend

# Просмотр логов в реальном времени
docker-compose logs -f backend

# Выполнение команд в контейнере
docker-compose exec backend bash

# Создание миграций
docker-compose exec backend alembic revision --autogenerate -m "description"

# Тестирование подключений
docker-compose exec airflow-scheduler python /opt/airflow/dags/test_connections.py
```

## 🧪 Тестирование

### Backend тесты
```bash
# Auth Service
cd auth/app
pytest --cov=src tests/

# Learning Service
cd back/app
pytest --cov=src tests/
```

### Frontend тесты
```bash
cd front/app
npm run test
npm run test:coverage
```

### Интеграционные тесты
```bash
# Тестирование подключений через Airflow
docker-compose exec airflow-webserver airflow dags test test_connections

# Тестирование API через curl
curl http://localhost:8301/api/v1/auth/health
curl http://localhost:8302/api/v1/courses/
```

## 📊 Мониторинг

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
```

### Состояние сервисов
```bash
docker-compose ps
docker stats
```

## 🔄 ETL и синхронизация

Apache Airflow автоматически синхронизирует данные между PostgreSQL и Elasticsearch каждые 15 минут.

### Доступные DAG'и:
- `sync_learning_data_to_elasticsearch` - основной DAG для синхронизации курсов, тем и уроков
- `test_connections` - тестирование подключений к БД, ES и Redis

### Управление:
- **Веб-интерфейс**: http://localhost:8304
- **Логин/пароль**: admin/admin (настраивается в `.env`)

### Инкрементальная синхронизация:
- Синхронизируются только изменённые данные
- Время последней синхронизации хранится в Redis
- Автоматическое создание индексов Elasticsearch

Подробная документация: [back/airflow/README.md](back/airflow/README.md)

## 🐛 Решение проблем

### Проблемы с правами доступа
```bash
# Исправление прав для скриптов
chmod +x back/app/entrypoint.sh
chmod +x back/airflow/init.sh
chmod +x auth/app/entrypoint.sh
```

### Elasticsearch
```bash
# Увеличьте vm.max_map_count (Linux/WSL)
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Проверка индексов
curl http://localhost:9200/_cat/indices
```

### PostgreSQL
```bash
# Проблемы с подключением к БД
docker-compose restart postgres
docker-compose logs postgres

# Проверка состояния БД
docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt"
```

### Airflow
```bash
# Проблемы с DAG'ами
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow tasks test sync_learning_data_to_elasticsearch health_check_elasticsearch

# Переустановка зависимостей
docker-compose exec airflow-webserver pip install -r /requirements.txt
```

### Сброс данных
```bash
# Полная очистка (ОСТОРОЖНО!)
docker-compose down -v
docker system prune -a
```

## 📈 Масштабирование и Production

### Рекомендации для продакшена
- **Базы данных**: используйте управляемые сервисы (AWS RDS, Google Cloud SQL)
- **Кэширование**: Redis Cluster для высокой доступности
- **Поиск**: Elasticsearch Cluster с несколькими нодами
- **Хранилище**: S3/GCS для статических файлов и медиа
- **CDN**: CloudFlare/CloudFront для ускорения доставки контента
- **Мониторинг**: Prometheus + Grafana + AlertManager
- **Логи**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **Безопасность**: HTTPS, сертификаты Let's Encrypt
- **CI/CD**: GitHub Actions/GitLab CI для автоматического деплоя

### Настройки производительности
```bash
# PostgreSQL
# Увеличьте shared_buffers, work_mem, max_connections

# Redis
# Настройте persistence, clustering

# Elasticsearch
# Увеличьте heap size, настройте шардинг

# Airflow
# Используйте CeleryExecutor для масштабирования
```

## 📚 Документация

### Детальная документация сервисов
- [Auth Service](auth/README.md) - сервис аутентификации и авторизации
- [Airflow ETL](back/airflow/README.md) - процессы синхронизации данных
- API документация доступна через Swagger UI для каждого сервиса

### Архитектурные решения
- **Микросервисы**: каждый сервис имеет свою зону ответственности
- **База данных**: мультитенантная PostgreSQL для всех сервисов
- **Аутентификация**: JWT токены с refresh механизмом
- **Поиск**: полнотекстовый поиск с поддержкой русского языка
- **ETL**: инкрементальная синхронизация данных каждые 15 минут

## 🤝 Участие в разработке

### Процесс разработки
1. Форкните репозиторий
2. Создайте feature ветку: `git checkout -b feature/amazing-feature`
3. Внесите изменения с тестами
4. Запустите тесты: `pytest` и `npm test`
5. Создайте Pull Request с подробным описанием

### Стандарты кода
- **Python**: Black, isort, flake8
- **JavaScript**: ESLint, Prettier
- **Коммиты**: Conventional Commits
- **Тесты**: покрытие >80%

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для подробностей.

---

**Smart Learning Platform** - современное решение для онлайн-образования 🎓

Создано с ❤️ командой разработчиков для будущего образования