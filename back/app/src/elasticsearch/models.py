"""
Модели Elasticsearch для синхронизации данных
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import json

from elasticsearch import AsyncElasticsearch


# Конфигурация подключения к Elasticsearch
ES_HOST = "http://elasticsearch:9200"


class CourseDocument:
    """Документ курса в Elasticsearch"""

    INDEX_NAME = 'courses'

    @classmethod
    def from_domain_model(cls, course_data: Dict[str, Any], topics: List[Dict] = None, lessons: List[Dict] = None):
        """Создаёт документ из модели домена"""
        return {
            'title': course_data.get('title', ''),
            'description': course_data.get('description', ''),
            'level': course_data.get('level', ''),
            'duration_hours': course_data.get('duration_hours', 0),
            'author_id': str(course_data.get('author_id', '')),
            'created_at': course_data.get('created_at').isoformat() if course_data.get('created_at') else None,
            'updated_at': course_data.get('updated_at').isoformat() if course_data.get('updated_at') else None,
            'total_enrollments': course_data.get('total_enrollments', 0),
            'average_rating': float(course_data.get('average_rating', 0.0)),
            'total_topics': len(topics) if topics else 0,
            'total_lessons': len(lessons) if lessons else 0,
            'topics': topics or [],
            'lessons': lessons or []
        }

    @classmethod
    async def save(cls, es_client: AsyncElasticsearch, doc_id: str, doc_body: Dict[str, Any]):
        """Сохраняет документ в Elasticsearch"""
        await es_client.index(
            index=cls.INDEX_NAME,
            id=doc_id,
            body=doc_body
        )


class TopicDocument:
    """Документ темы курса в Elasticsearch"""

    INDEX_NAME = 'topics'

    @classmethod
    def from_domain_model(cls, topic_data: Dict[str, Any], course_data: Dict[str, Any]):
        """Создаёт документ из модели домена"""
        return {
            'title': topic_data.get('title', ''),
            'description': topic_data.get('description', ''),
            'order': topic_data.get('order', 0),
            'course_id': str(topic_data.get('course_id', '')),
            'parent_id': str(topic_data.get('parent_id', '')) if topic_data.get('parent_id') else None,
            'course_title': course_data.get('title', ''),
            'course_level': course_data.get('level', ''),
            'course_author_id': str(course_data.get('author_id', '')),
            'created_at': topic_data.get('created_at').isoformat() if topic_data.get('created_at') else None,
            'updated_at': topic_data.get('updated_at').isoformat() if topic_data.get('updated_at') else None,
            'total_lessons': topic_data.get('total_lessons', 0),
            'total_assignments': topic_data.get('total_assignments', 0)
        }

    @classmethod
    async def save(cls, es_client: AsyncElasticsearch, doc_id: str, doc_body: Dict[str, Any]):
        """Сохраняет документ в Elasticsearch"""
        await es_client.index(
            index=cls.INDEX_NAME,
            id=doc_id,
            body=doc_body
        )


class LessonDocument:
    """Документ урока в Elasticsearch"""

    INDEX_NAME = 'lessons'

    @classmethod
    def from_domain_model(cls, lesson_data: Dict[str, Any], topic_data: Dict[str, Any], course_data: Dict[str, Any]):
        """Создаёт документ из модели домена"""
        return {
            'title': lesson_data.get('title', ''),
            'content': lesson_data.get('content', ''),
            'order': lesson_data.get('order', 0),
            'date': lesson_data.get('date').isoformat() if lesson_data.get('date') else None,
            'topic_id': str(lesson_data.get('topic_id', '')),
            'course_id': str(course_data.get('id', '')),
            'course_title': course_data.get('title', ''),
            'course_level': course_data.get('level', ''),
            'course_author_id': str(course_data.get('author_id', '')),
            'topic_title': topic_data.get('title', ''),
            'created_at': lesson_data.get('created_at').isoformat() if lesson_data.get('created_at') else None,
            'updated_at': lesson_data.get('updated_at').isoformat() if lesson_data.get('updated_at') else None,
            'total_assignments': lesson_data.get('total_assignments', 0)
        }

    @classmethod
    async def save(cls, es_client: AsyncElasticsearch, doc_id: str, doc_body: Dict[str, Any]):
        """Сохраняет документ в Elasticsearch"""
        await es_client.index(
            index=cls.INDEX_NAME,
            id=doc_id,
            body=doc_body
        )


async def create_indices():
    """Создаёт индексы Elasticsearch если их нет"""
    es_client = AsyncElasticsearch(hosts=[ES_HOST])

    # Настройки индексов с русским анализатором
    index_settings = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'russian': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop']
                    }
                }
            }
        },
        'mappings': {
            'properties': {
                'title': {'type': 'text', 'analyzer': 'russian'},
                'description': {'type': 'text', 'analyzer': 'russian'},
                'content': {'type': 'text', 'analyzer': 'russian'},
                'level': {'type': 'keyword'},
                'author_id': {'type': 'keyword'},
                'course_id': {'type': 'keyword'},
                'topic_id': {'type': 'keyword'},
                'parent_id': {'type': 'keyword'},
                'created_at': {'type': 'date'},
                'updated_at': {'type': 'date'},
                'date': {'type': 'date'},
                'order': {'type': 'integer'},
                'duration_hours': {'type': 'integer'},
                'total_enrollments': {'type': 'integer'},
                'total_lessons': {'type': 'integer'},
                'total_topics': {'type': 'integer'},
                'total_assignments': {'type': 'integer'},
                'average_rating': {'type': 'float'}
            }
        }
    }

    try:
        # Создаём индексы
        for document_class in [CourseDocument, TopicDocument, LessonDocument]:
            index_name = document_class.INDEX_NAME

            # Проверяем, существует ли индекс
            if not await es_client.indices.exists(index=index_name):
                await es_client.indices.create(
                    index=index_name,
                    body=index_settings
                )
                print(f"Индекс {index_name} создан")
            else:
                print(f"Индекс {index_name} уже существует")

    except Exception as e:
        print(f"Ошибка при создании индексов: {e}")
        raise
    finally:
        await es_client.close()


async def delete_indices():
    """Удаляет все индексы (используется для тестирования)"""
    es_client = AsyncElasticsearch(hosts=[ES_HOST])

    try:
        for document_class in [CourseDocument, TopicDocument, LessonDocument]:
            index_name = document_class.INDEX_NAME
            await es_client.indices.delete(index=index_name, ignore=[400, 404])
            print(f"Индекс {index_name} удалён")

    except Exception as e:
        print(f"Ошибка при удалении индексов: {e}")
        raise
    finally:
        await es_client.close()