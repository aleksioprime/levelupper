"""
DAG для синхронизации индексов Elasticsearch с базой данных
"""
from datetime import datetime, timedelta
import sys
import logging
import json
from typing import Dict, List, Any

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/opt/airflow/app')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.base import BaseSensorOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'smart-learning',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'sync_elasticsearch',
    default_args=default_args,
    description='Синхронизация индексов Elasticsearch с базой данных',
    schedule_interval='@daily',  # Запускается каждый день в полночь
    catchup=False,
    max_active_runs=1,  # Только одна активная задача в любой момент времени
    tags=['sync', 'elasticsearch', 'database']
)


def check_elasticsearch_health():
    """Проверяет здоровье Elasticsearch кластера"""
    import asyncio
    from src.elasticsearch.client import elasticsearch_client

    async def check_health():
        logger.info("Проверка здоровья Elasticsearch кластера...")
        try:
            client = await elasticsearch_client.get_client()
            health = await client.cluster.health()

            if health['status'] not in ['green', 'yellow']:
                raise Exception(f"Elasticsearch кластер нездоров: {health['status']}")

            logger.info(f"Elasticsearch кластер в порядке: {health['status']}")
            return True

        except Exception as e:
            logger.error(f"Ошибка проверки здоровья Elasticsearch: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    return asyncio.run(check_health())


def setup_elasticsearch_indices():
    """Создает или обновляет индексы Elasticsearch"""
    import asyncio
    from src.elasticsearch.client import elasticsearch_client

    async def setup_indices():
        logger.info("Настройка индексов Elasticsearch...")
        try:
            await elasticsearch_client.connect()
            success = await elasticsearch_client.setup_indices()

            if not success:
                raise Exception("Не удалось создать все необходимые индексы")

            logger.info("Индексы Elasticsearch настроены успешно")

        except Exception as e:
            logger.error(f"Ошибка настройки индексов: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(setup_indices())


def sync_courses_to_elasticsearch():
    """Синхронизирует курсы из БД в Elasticsearch"""
    import asyncio
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from src.db.postgres import async_session_maker
    from src.elasticsearch.client import elasticsearch_client
    from src.models.course import Course

    async def sync_courses():
        logger.info("Синхронизация курсов с Elasticsearch...")

        try:
            # Подключение к БД и Elasticsearch
            await elasticsearch_client.connect()
            client = await elasticsearch_client.get_client()

            async with async_session_maker() as session:
                # Получаем все курсы из БД
                stmt = select(Course).options(
                    selectinload(Course.topics),
                    selectinload(Course.moderators)
                )
                result = await session.execute(stmt)
                courses = result.scalars().all()

                logger.info(f"Найдено {len(courses)} курсов для синхронизации")

                # Подготавливаем документы для индексации
                documents = []
                for course in courses:
                    doc = {
                        'id': str(course.id),
                        'title': course.title,
                        'description': course.description,
                        'created_at': course.created_at.isoformat() if course.created_at else None,
                        'updated_at': course.updated_at.isoformat() if course.updated_at else None,
                        'topics_count': len(course.topics),
                        'moderators_count': len(course.moderators),
                        'topic_ids': [str(topic.id) for topic in course.topics],
                        'moderator_ids': [str(mod.user_id) for mod in course.moderators]
                    }
                    documents.append(doc)

                # Batch индексация в Elasticsearch
                if documents:
                    body = []
                    for doc in documents:
                        # Заголовок для индексации
                        body.append({
                            "index": {
                                "_index": "courses",
                                "_id": doc['id']
                            }
                        })
                        # Сам документ
                        body.append(doc)

                    await client.bulk(body=body, refresh=True)
                    logger.info(f"Проиндексировано {len(documents)} курсов")
                else:
                    logger.info("Нет курсов для индексации")

        except Exception as e:
            logger.error(f"Ошибка синхронизации курсов: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(sync_courses())


def sync_course_topics_to_elasticsearch():
    """Синхронизирует темы курсов из БД в Elasticsearch"""
    import asyncio
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from src.db.postgres import async_session_maker
    from src.elasticsearch.client import elasticsearch_client
    from src.models.course import CourseTopic

    async def sync_topics():
        logger.info("Синхронизация тем курсов с Elasticsearch...")

        try:
            await elasticsearch_client.connect()
            client = await elasticsearch_client.get_client()

            async with async_session_maker() as session:
                # Получаем все темы курсов из БД
                stmt = select(CourseTopic).options(
                    selectinload(CourseTopic.course),
                    selectinload(CourseTopic.parent),
                    selectinload(CourseTopic.subtopics),
                    selectinload(CourseTopic.lessons)
                )
                result = await session.execute(stmt)
                topics = result.scalars().all()

                logger.info(f"Найдено {len(topics)} тем курсов для синхронизации")

                # Подготавливаем документы для индексации
                documents = []
                for topic in topics:
                    doc = {
                        'id': str(topic.id),
                        'title': topic.title,
                        'description': topic.description,
                        'order': topic.order,
                        'course_id': str(topic.course_id),
                        'course_title': topic.course.title if topic.course else None,
                        'parent_id': str(topic.parent_id) if topic.parent_id else None,
                        'parent_title': topic.parent.title if topic.parent else None,
                        'created_at': topic.created_at.isoformat() if topic.created_at else None,
                        'updated_at': topic.updated_at.isoformat() if topic.updated_at else None,
                        'subtopics_count': len(topic.subtopics),
                        'lessons_count': len(topic.lessons),
                        'subtopic_ids': [str(subtopic.id) for subtopic in topic.subtopics],
                        'lesson_ids': [str(lesson.id) for lesson in topic.lessons]
                    }
                    documents.append(doc)

                # Batch индексация в Elasticsearch
                if documents:
                    body = []
                    for doc in documents:
                        body.append({
                            "index": {
                                "_index": "course_topics",
                                "_id": doc['id']
                            }
                        })
                        body.append(doc)

                    await client.bulk(body=body, refresh=True)
                    logger.info(f"Проиндексировано {len(documents)} тем курсов")
                else:
                    logger.info("Нет тем курсов для индексации")

        except Exception as e:
            logger.error(f"Ошибка синхронизации тем курсов: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(sync_topics())


def sync_lessons_to_elasticsearch():
    """Синхронизирует уроки из БД в Elasticsearch"""
    import asyncio
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from src.db.postgres import async_session_maker
    from src.elasticsearch.client import elasticsearch_client
    from src.models.course import Lesson

    async def sync_lessons():
        logger.info("Синхронизация уроков с Elasticsearch...")

        try:
            await elasticsearch_client.connect()
            client = await elasticsearch_client.get_client()

            async with async_session_maker() as session:
                # Получаем все уроки из БД
                stmt = select(Lesson).options(
                    selectinload(Lesson.topic).selectinload("course"),
                    selectinload(Lesson.assignments)
                )
                result = await session.execute(stmt)
                lessons = result.scalars().all()

                logger.info(f"Найдено {len(lessons)} уроков для синхронизации")

                # Подготавливаем документы для индексации
                documents = []
                for lesson in lessons:
                    doc = {
                        'id': str(lesson.id),
                        'title': lesson.title,
                        'content': lesson.content,
                        'order': lesson.order,
                        'date': lesson.date.isoformat() if lesson.date else None,
                        'topic_id': str(lesson.topic_id),
                        'topic_title': lesson.topic.title if lesson.topic else None,
                        'course_id': str(lesson.topic.course_id) if lesson.topic else None,
                        'course_title': lesson.topic.course.title if lesson.topic and lesson.topic.course else None,
                        'created_at': lesson.created_at.isoformat() if lesson.created_at else None,
                        'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None,
                        'assignments_count': len(lesson.assignments),
                        'assignment_ids': [str(assignment.id) for assignment in lesson.assignments]
                    }
                    documents.append(doc)

                # Batch индексация в Elasticsearch
                if documents:
                    body = []
                    for doc in documents:
                        body.append({
                            "index": {
                                "_index": "lessons",
                                "_id": doc['id']
                            }
                        })
                        body.append(doc)

                    await client.bulk(body=body, refresh=True)
                    logger.info(f"Проиндексировано {len(documents)} уроков")
                else:
                    logger.info("Нет уроков для индексации")

        except Exception as e:
            logger.error(f"Ошибка синхронизации уроков: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(sync_lessons())


def cleanup_orphaned_documents():
    """Удаляет документы из Elasticsearch, которые больше не существуют в БД"""
    import asyncio
    from sqlalchemy import select

    from src.db.postgres import async_session_maker
    from src.elasticsearch.client import elasticsearch_client
    from src.models.course import Course, CourseTopic, Lesson

    async def cleanup_documents():
        logger.info("Очистка устаревших документов в Elasticsearch...")

        try:
            await elasticsearch_client.connect()
            client = await elasticsearch_client.get_client()

            async with async_session_maker() as session:
                # Получаем ID всех записей из БД
                course_ids = {str(id_) for id_, in await session.execute(select(Course.id))}
                topic_ids = {str(id_) for id_, in await session.execute(select(CourseTopic.id))}
                lesson_ids = {str(id_) for id_, in await session.execute(select(Lesson.id))}

                # Проверяем каждый индекс на устаревшие документы
                indices_to_check = [
                    ('courses', course_ids),
                    ('course_topics', topic_ids),
                    ('lessons', lesson_ids)
                ]

                total_deleted = 0

                for index_name, valid_ids in indices_to_check:
                    try:
                        # Получаем все документы из индекса
                        search_body = {
                            "query": {"match_all": {}},
                            "_source": False,
                            "size": 10000
                        }

                        response = await client.search(
                            index=index_name,
                            body=search_body
                        )

                        # Находим документы для удаления
                        docs_to_delete = []
                        for hit in response['hits']['hits']:
                            doc_id = hit['_id']
                            if doc_id not in valid_ids:
                                docs_to_delete.append(doc_id)

                        # Удаляем устаревшие документы
                        if docs_to_delete:
                            delete_body = []
                            for doc_id in docs_to_delete:
                                delete_body.append({
                                    "delete": {
                                        "_index": index_name,
                                        "_id": doc_id
                                    }
                                })

                            await client.bulk(body=delete_body, refresh=True)
                            total_deleted += len(docs_to_delete)
                            logger.info(f"Удалено {len(docs_to_delete)} устаревших документов из индекса {index_name}")

                    except Exception as e:
                        logger.error(f"Ошибка очистки индекса {index_name}: {e}")

                logger.info(f"Всего удалено устаревших документов: {total_deleted}")

        except Exception as e:
            logger.error(f"Ошибка очистки документов: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(cleanup_documents())


def validate_sync_completeness():
    """Проверяет полноту синхронизации между БД и Elasticsearch"""
    import asyncio
    from sqlalchemy import select, func

    from src.db.postgres import async_session_maker
    from src.elasticsearch.client import elasticsearch_client
    from src.models.course import Course, CourseTopic, Lesson

    async def validate_sync():
        logger.info("Проверка полноты синхронизации...")

        try:
            await elasticsearch_client.connect()
            client = await elasticsearch_client.get_client()

            async with async_session_maker() as session:
                # Подсчитываем записи в БД
                db_counts = {}
                db_counts['courses'] = await session.scalar(select(func.count(Course.id)))
                db_counts['course_topics'] = await session.scalar(select(func.count(CourseTopic.id)))
                db_counts['lessons'] = await session.scalar(select(func.count(Lesson.id)))

                # Подсчитываем документы в Elasticsearch
                es_counts = {}
                for index_name in ['courses', 'course_topics', 'lessons']:
                    try:
                        response = await client.count(index=index_name)
                        es_counts[index_name] = response['count']
                    except Exception as e:
                        logger.error(f"Не удалось подсчитать документы в индексе {index_name}: {e}")
                        es_counts[index_name] = 0

                # Сравниваем количества
                sync_status = True
                for index_name in db_counts:
                    db_count = db_counts[index_name]
                    es_count = es_counts.get(index_name, 0)

                    if db_count != es_count:
                        logger.warning(
                            f"Несоответствие в {index_name}: БД={db_count}, ES={es_count}"
                        )
                        sync_status = False
                    else:
                        logger.info(f"✓ {index_name}: {db_count} записей синхронизировано")

                if sync_status:
                    logger.info("Синхронизация прошла успешно!")
                else:
                    logger.warning("Обнаружены несоответствия в синхронизации")

        except Exception as e:
            logger.error(f"Ошибка проверки синхронизации: {e}")
            raise
        finally:
            await elasticsearch_client.disconnect()

    asyncio.run(validate_sync())


# Определение задач DAG
health_check_task = PythonOperator(
    task_id='check_elasticsearch_health',
    python_callable=check_elasticsearch_health,
    dag=dag
)

setup_indices_task = PythonOperator(
    task_id='setup_elasticsearch_indices',
    python_callable=setup_elasticsearch_indices,
    dag=dag
)

sync_courses_task = PythonOperator(
    task_id='sync_courses_to_elasticsearch',
    python_callable=sync_courses_to_elasticsearch,
    dag=dag
)

sync_topics_task = PythonOperator(
    task_id='sync_course_topics_to_elasticsearch',
    python_callable=sync_course_topics_to_elasticsearch,
    dag=dag
)

sync_lessons_task = PythonOperator(
    task_id='sync_lessons_to_elasticsearch',
    python_callable=sync_lessons_to_elasticsearch,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_orphaned_documents',
    python_callable=cleanup_orphaned_documents,
    dag=dag
)

validation_task = PythonOperator(
    task_id='validate_sync_completeness',
    python_callable=validate_sync_completeness,
    dag=dag
)

# Определение зависимостей между задачами
health_check_task >> setup_indices_task

setup_indices_task >> [sync_courses_task, sync_topics_task, sync_lessons_task]

[sync_courses_task, sync_topics_task, sync_lessons_task] >> cleanup_task

cleanup_task >> validation_task