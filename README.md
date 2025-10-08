# 🎓 Smart Learning Platform

Современная платформа для управления учебными курсами с полнофункциональной системой онлайн-обучения, включающая создание курсов, управление уроками, задания различных типов, отслеживание прогресса и мощный поиск.

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

## 🛠 Технологический стек

### Backend
- **FastAPI** - высокопроизводительный веб-фреймворк
- **SQLAlchemy 2.0** - современная ORM с асинхронной поддержкой
- **PostgreSQL** - надежная реляционная БД
- **Redis** - кэширование и управление сессиями
- **Elasticsearch** - полнотекстовый поиск и аналитика
- **Alembic** - управление миграциями БД
- **Pydantic** - валидация данных и сериализация

### Frontend
- **Vue.js 3** - прогрессивный JavaScript фреймворк
- **Vite** - быстрый сборщик и dev-сервер
- **Pinia** - современное управление состоянием

### DevOps & Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Apache Airflow** - ETL процессы и синхронизация
- **Nginx** - веб-сервер и reverse proxy

### Архитектура
- **Clean Architecture** - четкое разделение слоев
- **Domain-Driven Design** - фокус на бизнес-логике
- **Repository Pattern** - абстракция доступа к данным
- **Unit of Work** - управление транзакциями

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/aleksioprime/smart-learning.git
cd smart-learning
```

### 2. Настройка переменных окружения
```bash
# Скопируйте файл конфигурации
cp .env.production .env

# Отредактируйте необходимые параметры
nano .env
```

### 3. Запуск сервисов
```bash
# Запустите все сервисы
docker-compose -p learning up -d --build

# Проверьте статус
docker-compose -p learning ps
```

### 4. Настройка базы данных
```bash
# Создайте миграции (если нужно)
docker exec -it learning-backend alembic revision --autogenerate -m "initial"

# Примените миграции
docker exec -it learning-backend alembic upgrade head

# Создайте суперпользователя
docker-compose -p learning exec backend python scripts/create_superuser.py --username admin --password admin123 --email admin@example.com
```

### 5. Инициализация Elasticsearch
```bash
# Создайте индексы
docker-compose -p learning exec backend python -c "
from src.common.elasticsearch.models import create_indices
create_indices()
"
```

## 🌐 Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://localhost:8303 | Веб-интерфейс платформы |
| **Backend API** | http://localhost:8302 | REST API |
| **API Docs** | http://localhost:8302/docs | Swagger документация |
| **Airflow** | http://localhost:8304 | Управление ETL процессами |
| **Elasticsearch** | http://elasticsearch:9200 | Поисковый движок (внутренний) |

## Административная панель

Платформа включает веб-интерфейс для администрирования данных через **SQLAdmin**:

- **URL**: http://localhost:8302/admin
- **Логин**: `admin`
- **Пароль**: `admin123`

### Возможности админ-панели:
- **Управление курсами**: создание, редактирование, удаление курсов
- **Управление уроками**: добавление материалов к курсам
- **Управление заданиями**: создание практических заданий
- **Отчеты по участникам**: просмотр прогресса обучения
- **Проверка работ**: просмотр и оценка выполненных заданий

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - Регистрация пользователя
- `POST /api/auth/login` - Авторизация пользователя
- `GET /api/auth/me` - Получение текущего пользователя

## 🔧 Разработка

### Быстрый старт с Docker
```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd smart-learning

# 2. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл при необходимости

# 3. Запустите все сервисы
docker-compose --profile full up -d

# 4. Дождитесь готовности сервисов (1-2 минуты)
docker-compose ps

# 5. Примените миграции
docker-compose exec backend alembic upgrade head

# 6. Создайте суперпользователя
docker-compose exec backend python scripts/create_superuser.py
```

### Доступы после запуска
- **API**: http://localhost:8301/docs (Swagger UI)
- **Admin**: http://localhost:8301/admin (admin/admin123)
- **Frontend**: http://localhost:8302 (development)
- **Airflow**: http://localhost:8308 (airflow/airflow)

📖 **Подробная документация**: [docker-compose.dev.md](docker-compose.dev.md)

### Локальная разработка без Docker

#### Backend
```bash
cd back
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
# Настройте подключения к БД, Redis, Elasticsearch
python -m src.main
```

#### Frontend
```bash
cd front/app
npm install
npm run dev
```

## 🧪 Тестирование

```bash
# Backend тесты
cd back
pytest --cov=src

# Frontend тесты
cd front/app
npm run test
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

### Permission denied для entrypoint.sh
```bash
chmod +x back/entrypoint.sh
```

### Elasticsearch требует больше памяти
```bash
# Увеличьте vm.max_map_count (Linux)
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Проблемы с подключением к БД
```bash
# Перезапустите сервисы
docker-compose restart postgres backend
```

## 📈 Масштабирование

Для продакшена рекомендуется:
- Использовать внешние базы данных (AWS RDS, Google Cloud SQL)
- Настроить кэширование Redis Cluster
- Использовать CDN для статических файлов
- Настроить мониторинг (Prometheus + Grafana)

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

---

Создано с ❤️ для современного онлайн-образования