"""
DAG для синхронизации данных курсов с Elasticsearch.
Включает полную синхронизацию курсов, уроков и агрегированных данных.
"""

import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/usr/src/app')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago

# Настройки по умолчанию для всех задач
default_args = {
    'owner': 'smart-learning',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Создание DAG
dag = DAG(
    'sync_courses_to_elasticsearch',
    default_args=default_args,
    description='Синхронизация данных курсов с Elasticsearch',
    schedule_interval='*/15 * * * *',  # Каждые 15 минут
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'elasticsearch', 'courses']
)


def sync_courses_to_elastic():
    """
    Синхронизация курсов с Elasticsearch.
    """
    import asyncio
    from sqlalchemy import text
    from elasticsearch import AsyncElasticsearch
    import redis.asyncio as redis

    from src.common.db.postgres import async_session_maker
    from src.common.elasticsearch.models import CourseDocument, create_indices

    async def run_sync():
        # Создаем индексы если их нет
        create_indices()

        # Инициализация клиентов
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            # Получаем время последней синхронизации
            last_sync_key = "sync:courses:last_updated_at"
            last_sync_time = await redis_client.get(last_sync_key)

            # SQL запрос для получения обновленных курсов
            if last_sync_time:
                courses_query = text("""
                    SELECT c.*,
                           COUNT(e.id) as total_enrollments,
                           COALESCE(AVG(CAST(ar.score AS FLOAT) / CAST(a.max_score AS FLOAT) * 5), 0) as average_rating
                    FROM courses c
                    LEFT JOIN enrollments e ON c.id = e.course_id
                    LEFT JOIN lesson_progress lp ON e.id = lp.enrollment_id
                    LEFT JOIN lessons l ON lp.lesson_id = l.id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    LEFT JOIN assignment_submissions ar ON a.id = ar.assignment_id AND e.id = ar.enrollment_id
                    WHERE c.updated_at > :last_sync_time OR e.enrolled_at > :last_sync_time
                    GROUP BY c.id
                """)
                params = {"last_sync_time": last_sync_time}
            else:
                courses_query = text("""
                    SELECT c.*,
                           COUNT(e.id) as total_enrollments,
                           COALESCE(AVG(CAST(ar.score AS FLOAT) / CAST(a.max_score AS FLOAT) * 5), 0) as average_rating
                    FROM courses c
                    LEFT JOIN enrollments e ON c.id = e.course_id
                    LEFT JOIN lesson_progress lp ON e.id = lp.enrollment_id
                    LEFT JOIN lessons l ON lp.lesson_id = l.id
                    LEFT JOIN assignments a ON l.id = a.lesson_id
                    LEFT JOIN assignment_submissions ar ON a.id = ar.assignment_id AND e.id = ar.enrollment_id
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

                    # Получаем уроки для курса
                    lessons_query = text("""
                        SELECT l.* FROM lessons l
                        WHERE l.course_id = :course_id
                        ORDER BY l.order_index
                    """)
                    lessons_result = await session.execute(
                        lessons_query,
                        {"course_id": course_dict['id']}
                    )
                    lessons = [dict(row._mapping) for row in lessons_result.fetchall()]

                    # Создаем документ Elasticsearch
                    doc = CourseDocument.from_domain_model(course_dict, lessons)

                    # Сохраняем в Elasticsearch
                    await doc.save(using=es_client)
                    synced_count += 1

                # Обновляем время последней синхронизации
                current_time = datetime.utcnow().isoformat()
                await redis_client.set(last_sync_key, current_time)

                print(f"Синхронизировано {synced_count} курсов")

        finally:
            await es_client.close()
            await redis_client.close()

    # Запускаем асинхронную функцию
    asyncio.run(run_sync())


def sync_lessons_to_elastic():
    """
    Синхронизация уроков с Elasticsearch.
    """
    import asyncio
    from sqlalchemy import text
    from elasticsearch import AsyncElasticsearch
    import redis.asyncio as redis

    from src.common.db.postgres import async_session_maker
    from src.common.elasticsearch.models import LessonDocument

    async def run_sync():
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

        try:
            last_sync_key = "sync:lessons:last_updated_at"
            last_sync_time = await redis_client.get(last_sync_key)

            # SQL запрос для получения обновленных уроков
            if last_sync_time:
                lessons_query = text("""
                    SELECT l.*, c.title as course_title, c.level as course_level, c.author_id as course_author_id
                    FROM lessons l
                    JOIN courses c ON l.course_id = c.id
                    WHERE l.updated_at > :last_sync_time
                """)
                params = {"last_sync_time": last_sync_time}
            else:
                lessons_query = text("""
                    SELECT l.*, c.title as course_title, c.level as course_level, c.author_id as course_author_id
                    FROM lessons l
                    JOIN courses c ON l.course_id = c.id
                """)
                params = {}

            async with async_session_maker() as session:
                lessons_result = await session.execute(lessons_query, params)
                lessons = lessons_result.fetchall()

                synced_count = 0

                for lesson_row in lessons:
                    lesson_dict = dict(lesson_row._mapping)
                    course_data = {
                        'title': lesson_dict.pop('course_title'),
                        'level': lesson_dict.pop('course_level'),
                        'author_id': lesson_dict.pop('course_author_id')
                    }

                    # Создаем документ Elasticsearch
                    doc = LessonDocument.from_domain_model(lesson_dict, course_data)

                    # Сохраняем в Elasticsearch
                    await doc.save(using=es_client)
                    synced_count += 1

                # Обновляем время последней синхронизации
                current_time = datetime.utcnow().isoformat()
                await redis_client.set(last_sync_key, current_time)

                print(f"Синхронизировано {synced_count} уроков")

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
        es_client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
        try:
            health = await es_client.cluster.health()
            print(f"Elasticsearch health: {health['status']}")
            if health['status'] not in ['green', 'yellow']:
                raise Exception(f"Elasticsearch is not healthy: {health['status']}")
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
start_task >> health_check_task >> [sync_courses_task, sync_lessons_task] >> end_task
