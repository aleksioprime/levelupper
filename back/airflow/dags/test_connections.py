"""
Простой DAG для тестирования подключений
"""
from datetime import datetime, timedelta
import sys
import logging

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/usr/src/app')

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'smart-learning',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'test_connections',
    default_args=default_args,
    description='Тестирование подключений к БД и Elasticsearch',
    schedule_interval=None,  # Запуск только вручную
    catchup=False,
    tags=['test', 'connections']
)


def test_database_connection():
    """Тестирование подключения к PostgreSQL"""
    import asyncio
    from sqlalchemy import text

    from src.db.postgres import async_session_maker

    async def test_db():
        logger.info("Тестирование подключения к PostgreSQL...")
        try:
            async with async_session_maker() as session:
                # Простой запрос для проверки подключения
                result = await session.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"PostgreSQL версия: {version}")

                # Проверим существование основных таблиц
                tables_query = text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('courses', 'course_topics', 'lessons')
                """)
                tables_result = await session.execute(tables_query)
                tables = [row[0] for row in tables_result.fetchall()]
                logger.info(f"Найденные таблицы: {tables}")

        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    asyncio.run(test_db())


def test_elasticsearch_connection():
    """Тестирование подключения к Elasticsearch"""
    import asyncio
    from elasticsearch import AsyncElasticsearch

    async def test_es():
        logger.info("Тестирование подключения к Elasticsearch...")
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            # Проверка здоровья кластера
            health = await es_client.cluster.health()
            logger.info(f"Elasticsearch статус: {health['status']}")

            # Проверка существующих индексов
            indices = await es_client.cat.indices(format='json')
            index_names = [idx['index'] for idx in indices if not idx['index'].startswith('.')]
            logger.info(f"Существующие индексы: {index_names}")

        except Exception as e:
            logger.error(f"Ошибка подключения к Elasticsearch: {e}")
            raise
        finally:
            await es_client.close()

    asyncio.run(test_es())


def test_redis_connection():
    """Тестирование подключения к Redis"""
    import asyncio
    import redis.asyncio as redis

    async def test_redis():
        logger.info("Тестирование подключения к Redis...")
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

        try:
            # Простая проверка подключения
            pong = await redis_client.ping()
            logger.info(f"Redis ping: {pong}")

            # Проверка записи/чтения
            test_key = "airflow:test:connection"
            await redis_client.set(test_key, "test_value", ex=60)
            test_value = await redis_client.get(test_key)
            logger.info(f"Redis test value: {test_value}")

        except Exception as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
            raise
        finally:
            await redis_client.close()

    asyncio.run(test_redis())


# Определение задач
test_db_task = PythonOperator(
    task_id='test_database_connection',
    python_callable=test_database_connection,
    dag=dag
)

test_es_task = PythonOperator(
    task_id='test_elasticsearch_connection',
    python_callable=test_elasticsearch_connection,
    dag=dag
)

test_redis_task = PythonOperator(
    task_id='test_redis_connection',
    python_callable=test_redis_connection,
    dag=dag
)

# Параллельное выполнение всех тестов
[test_db_task, test_es_task, test_redis_task]