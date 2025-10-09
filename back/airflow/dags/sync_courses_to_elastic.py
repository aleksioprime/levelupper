"""
DAG для синхронизации данных курсов, тем и уроков с Elasticsearch.
Включает полную синхронизацию курсов, тем, уроков и агрегированных данных.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/usr/src/app')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройки по умолчанию для всех задач
default_args = {
    'owner': 'smart-learning',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

# Создание DAG
dag = DAG(
    'sync_learning_data_to_elasticsearch',
    default_args=default_args,
    description='Синхронизация данных курсов, тем и уроков с Elasticsearch',
    schedule_interval='*/15 * * * *',  # Каждые 15 минут
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'elasticsearch', 'courses', 'topics', 'lessons']
)


def sync_courses_to_elastic():
    """
    Синхронизация курсов с Elasticsearch.
    """
    import asyncio
    from sqlalchemy import text
    from elasticsearch import AsyncElasticsearch
    import redis.asyncio as redis

    from config.postgres import async_session_maker
    from src.elasticsearch.models import CourseDocument, create_indices

    async def run_sync():
        logger.info("Начинается синхронизация курсов с Elasticsearch")

        # Создаем индексы если их нет
        try:
            await create_indices()
        except Exception as e:
            logger.error(f"Ошибка при создании индексов: {e}")
            raise

        # Инициализация клиентов
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            # Получаем время последней синхронизации
            last_sync_key = "sync:courses:last_updated_at"
            last_sync_time = await redis_client.get(last_sync_key)

            # SQL запрос для получения курсов с агрегированными данными
            if last_sync_time:
                courses_query = text("""
                    SELECT c.*,
                           COUNT(DISTINCT e.id) as total_enrollments,
                           COALESCE(AVG(CAST(s.score AS FLOAT) / CAST(a.max_score AS FLOAT) * 5), 0) as average_rating
                    FROM courses c
                    LEFT JOIN groups g ON c.id = g.course_id
                    LEFT JOIN enrollments e ON g.id = e.group_id
                    LEFT JOIN course_topics ct ON c.id = ct.course_id
                    LEFT JOIN lessons l ON ct.id = l.topic_id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    LEFT JOIN submissions s ON a.id = s.assignment_id
                    WHERE c.updated_at > :last_sync_time
                    GROUP BY c.id
                """)
                params = {"last_sync_time": last_sync_time}
            else:
                courses_query = text("""
                    SELECT c.*,
                           COUNT(DISTINCT e.id) as total_enrollments,
                           COALESCE(AVG(CAST(s.score AS FLOAT) / CAST(a.max_score AS FLOAT) * 5), 0) as average_rating
                    FROM courses c
                    LEFT JOIN groups g ON c.id = g.course_id
                    LEFT JOIN enrollments e ON g.id = e.group_id
                    LEFT JOIN course_topics ct ON c.id = ct.course_id
                    LEFT JOIN lessons l ON ct.id = l.topic_id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    LEFT JOIN submissions s ON a.id = s.assignment_id
                    GROUP BY c.id
                """)
                params = {}

            # Выполняем запрос
            async with async_session_maker() as session:
                courses_result = await session.execute(courses_query, params)
                courses = courses_result.fetchall()

                synced_count = 0

                for course_row in courses:
                    course_dict = dict(course_row._mapping)
                    course_id = course_dict['id']

                    # Получаем темы для курса
                    topics_query = text("""
                        SELECT ct.*, COUNT(l.id) as total_lessons, COUNT(a.id) as total_assignments
                        FROM course_topics ct
                        LEFT JOIN lessons l ON ct.id = l.topic_id
                        LEFT JOIN assignments a ON ct.id = a.topic_id
                        WHERE ct.course_id = :course_id
                        GROUP BY ct.id
                        ORDER BY ct.order
                    """)
                    topics_result = await session.execute(
                        topics_query,
                        {"course_id": course_id}
                    )
                    topics = [dict(row._mapping) for row in topics_result.fetchall()]

                    # Получаем уроки для курса
                    lessons_query = text("""
                        SELECT l.*, ct.title as topic_title
                        FROM lessons l
                        JOIN course_topics ct ON l.topic_id = ct.id
                        WHERE ct.course_id = :course_id
                        ORDER BY ct.order, l.order
                    """)
                    lessons_result = await session.execute(
                        lessons_query,
                        {"course_id": course_id}
                    )
                    lessons = [dict(row._mapping) for row in lessons_result.fetchall()]

                    # Создаем документ Elasticsearch
                    doc_body = CourseDocument.from_domain_model(course_dict, topics, lessons)

                    # Сохраняем в Elasticsearch
                    await CourseDocument.save(es_client, str(course_id), doc_body)
                    synced_count += 1

                # Обновляем время последней синхронизации
                current_time = datetime.utcnow().isoformat()
                await redis_client.set(last_sync_key, current_time)

                logger.info(f"Синхронизировано {synced_count} курсов")

        except Exception as e:
            logger.error(f"Ошибка при синхронизации курсов: {e}")
            raise
        finally:
            await es_client.close()
            await redis_client.close()

    # Запускаем асинхронную функцию
    asyncio.run(run_sync())


def sync_topics_to_elastic():
    """
    Синхронизация тем курсов с Elasticsearch.
    """
    import asyncio
    from sqlalchemy import text
    from elasticsearch import AsyncElasticsearch
    import redis.asyncio as redis

    from src.db.postgres import async_session_maker
    from src.elasticsearch.models import TopicDocument

    async def run_sync():
        logger.info("Начинается синхронизация тем с Elasticsearch")

        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            last_sync_key = "sync:topics:last_updated_at"
            last_sync_time = await redis_client.get(last_sync_key)

            # SQL запрос для получения обновленных тем
            if last_sync_time:
                topics_query = text("""
                    SELECT ct.*, c.title as course_title, c.level as course_level, c.author_id as course_author_id,
                           COUNT(DISTINCT l.id) as total_lessons,
                           COUNT(DISTINCT a.id) as total_assignments
                    FROM course_topics ct
                    JOIN courses c ON ct.course_id = c.id
                    LEFT JOIN lessons l ON ct.id = l.topic_id
                    LEFT JOIN assignments a ON ct.id = a.topic_id
                    WHERE ct.updated_at > :last_sync_time
                    GROUP BY ct.id, c.title, c.level, c.author_id
                """)
                params = {"last_sync_time": last_sync_time}
            else:
                topics_query = text("""
                    SELECT ct.*, c.title as course_title, c.level as course_level, c.author_id as course_author_id,
                           COUNT(DISTINCT l.id) as total_lessons,
                           COUNT(DISTINCT a.id) as total_assignments
                    FROM course_topics ct
                    JOIN courses c ON ct.course_id = c.id
                    LEFT JOIN lessons l ON ct.id = l.topic_id
                    LEFT JOIN assignments a ON ct.id = a.topic_id
                    GROUP BY ct.id, c.title, c.level, c.author_id
                """)
                params = {}

            async with async_session_maker() as session:
                topics_result = await session.execute(topics_query, params)
                topics = topics_result.fetchall()

                synced_count = 0

                for topic_row in topics:
                    topic_dict = dict(topic_row._mapping)
                    course_data = {
                        'id': topic_dict['course_id'],
                        'title': topic_dict.pop('course_title'),
                        'level': topic_dict.pop('course_level'),
                        'author_id': topic_dict.pop('course_author_id')
                    }

                    # Создаем документ Elasticsearch
                    doc_body = TopicDocument.from_domain_model(topic_dict, course_data)

                    # Сохраняем в Elasticsearch
                    await TopicDocument.save(es_client, str(topic_dict['id']), doc_body)
                    synced_count += 1

                # Обновляем время последней синхронизации
                current_time = datetime.utcnow().isoformat()
                await redis_client.set(last_sync_key, current_time)

                logger.info(f"Синхронизировано {synced_count} тем")

        except Exception as e:
            logger.error(f"Ошибка при синхронизации тем: {e}")
            raise
        finally:
            await es_client.close()
            await redis_client.close()

    asyncio.run(run_sync())


def sync_lessons_to_elastic():
    """
    Синхронизация уроков с Elasticsearch.
    """
    import asyncio
    from sqlalchemy import text
    from elasticsearch import AsyncElasticsearch
    import redis.asyncio as redis

    from src.db.postgres import async_session_maker
    from src.elasticsearch.models import LessonDocument

    async def run_sync():
        logger.info("Начинается синхронизация уроков с Elasticsearch")

        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            last_sync_key = "sync:lessons:last_updated_at"
            last_sync_time = await redis_client.get(last_sync_key)

            # SQL запрос для получения обновленных уроков
            if last_sync_time:
                lessons_query = text("""
                    SELECT l.*, ct.title as topic_title, ct.course_id,
                           c.title as course_title, c.level as course_level, c.author_id as course_author_id,
                           COUNT(a.id) as total_assignments
                    FROM lessons l
                    JOIN course_topics ct ON l.topic_id = ct.id
                    JOIN courses c ON ct.course_id = c.id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    WHERE l.updated_at > :last_sync_time
                    GROUP BY l.id, ct.title, ct.course_id, c.title, c.level, c.author_id
                """)
                params = {"last_sync_time": last_sync_time}
            else:
                lessons_query = text("""
                    SELECT l.*, ct.title as topic_title, ct.course_id,
                           c.title as course_title, c.level as course_level, c.author_id as course_author_id,
                           COUNT(a.id) as total_assignments
                    FROM lessons l
                    JOIN course_topics ct ON l.topic_id = ct.id
                    JOIN courses c ON ct.course_id = c.id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    GROUP BY l.id, ct.title, ct.course_id, c.title, c.level, c.author_id
                """)
                params = {}

            async with async_session_maker() as session:
                lessons_result = await session.execute(lessons_query, params)
                lessons = lessons_result.fetchall()

                synced_count = 0

                for lesson_row in lessons:
                    lesson_dict = dict(lesson_row._mapping)
                    topic_data = {
                        'title': lesson_dict.pop('topic_title')
                    }
                    course_data = {
                        'id': lesson_dict.pop('course_id'),
                        'title': lesson_dict.pop('course_title'),
                        'level': lesson_dict.pop('course_level'),
                        'author_id': lesson_dict.pop('course_author_id')
                    }

                    # Создаем документ Elasticsearch
                    doc_body = LessonDocument.from_domain_model(lesson_dict, topic_data, course_data)

                    # Сохраняем в Elasticsearch
                    await LessonDocument.save(es_client, str(lesson_dict['id']), doc_body)
                    synced_count += 1

                # Обновляем время последней синхронизации
                current_time = datetime.utcnow().isoformat()
                await redis_client.set(last_sync_key, current_time)

                logger.info(f"Синхронизировано {synced_count} уроков")

        except Exception as e:
            logger.error(f"Ошибка при синхронизации уроков: {e}")
            raise
        finally:
            await es_client.close()
            await redis_client.close()

    asyncio.run(run_sync())


def health_check_elasticsearch():
    """
    Проверка доступности Elasticsearch.
    """
    import asyncio
    from elasticsearch import AsyncElasticsearch

    async def check():
        logger.info("Проверка доступности Elasticsearch")
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
        try:
            health = await es_client.cluster.health()
            logger.info(f"Elasticsearch health: {health['status']}")
            if health['status'] not in ['green', 'yellow']:
                raise Exception(f"Elasticsearch is not healthy: {health['status']}")
        except Exception as e:
            logger.error(f"Ошибка при проверке Elasticsearch: {e}")
            raise
        finally:
            await es_client.close()

    asyncio.run(check())


# Определение задач
start_task = DummyOperator(
    task_id='start_sync',
    dag=dag
)

health_check_task = PythonOperator(
    task_id='health_check_elasticsearch',
    python_callable=health_check_elasticsearch,
    dag=dag
)

sync_courses_task = PythonOperator(
    task_id='sync_courses_to_elasticsearch',
    python_callable=sync_courses_to_elastic,
    dag=dag
)

sync_topics_task = PythonOperator(
    task_id='sync_topics_to_elasticsearch',
    python_callable=sync_topics_to_elastic,
    dag=dag
)

sync_lessons_task = PythonOperator(
    task_id='sync_lessons_to_elasticsearch',
    python_callable=sync_lessons_to_elastic,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_sync',
    dag=dag
)

# Определение зависимостей между задачами
start_task >> health_check_task >> [sync_courses_task, sync_topics_task, sync_lessons_task] >> end_task
