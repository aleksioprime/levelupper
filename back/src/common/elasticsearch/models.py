"""
Модели Elasticsearch для индексации курсов и поиска.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from elasticsearch_dsl import Document, Text, Keyword, Integer, Float, Date, Boolean, Object, Nested
from elasticsearch_dsl.connections import connections

from src.common.core.config import settings


# Настройка подключения к Elasticsearch
try:
    # Для новых версий elasticsearch-dsl (8.x+)
    connections.create_connection(
        alias='default',
        hosts=[settings.elasticsearch.url],
        basic_auth=(settings.elasticsearch.username, settings.elasticsearch.password) if settings.elasticsearch.username else None,
    )
except TypeError:
    # Fallback для старых версий
    connections.create_connection(
        alias='default',
        hosts=[settings.elasticsearch.url],
        http_auth=(settings.elasticsearch.username, settings.elasticsearch.password) if settings.elasticsearch.username else None,
    )


class CourseDocument(Document):
    """Документ курса в Elasticsearch."""

    # Основная информация
    id = Keyword()
    title = Text(analyzer='standard')
    description = Text(analyzer='standard')
    author_id = Keyword()

    # Категоризация
    level = Keyword()
    status = Keyword()
    tags = Keyword(multi=True)

    # Ценообразование
    price = Float()
    is_free = Boolean()

    # Дополнительная информация
    duration_hours = Integer()
    max_students = Integer()
    image_url = Keyword()

    # Временные метки
    created_at = Date()
    updated_at = Date()

    # Связанные данные
    lessons = Nested(properties={
        'id': Keyword(),
        'title': Text(analyzer='standard'),
        'content': Text(analyzer='standard'),
        'lesson_type': Keyword(),
        'status': Keyword(),
        'order_index': Integer(),
        'duration_minutes': Integer(),
        'is_free_preview': Boolean(),
        'created_at': Date(),
        'updated_at': Date()
    })

    # Агрегированная статистика
    total_lessons = Integer()
    published_lessons = Integer()
    total_enrollments = Integer()
    average_rating = Float()

    class Index:
        name = 'courses'
        settings = {
            'number_of_shards': 2,
            'number_of_replicas': 1,
            'analysis': {
                'analyzer': {
                    'custom_text_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop', 'snowball']
                    }
                }
            }
        }

    @classmethod
    def from_domain_model(cls, course_data: Dict[str, Any], lessons_data: List[Dict[str, Any]] = None) -> 'CourseDocument':
        """Создает документ Elasticsearch из доменной модели."""
        lessons_data = lessons_data or []

        # Подготавливаем данные уроков
        lessons = []
        for lesson in lessons_data:
            lessons.append({
                'id': str(lesson['id']),
                'title': lesson['title'],
                'content': lesson['content'][:500] if lesson['content'] else '',  # Ограничиваем длину
                'lesson_type': lesson['lesson_type'],
                'status': lesson['status'],
                'order_index': lesson['order_index'],
                'duration_minutes': lesson['duration_minutes'],
                'is_free_preview': lesson['is_free_preview'],
                'created_at': lesson['created_at'],
                'updated_at': lesson['updated_at']
            })

        return cls(
            meta={'id': str(course_data['id'])},
            id=str(course_data['id']),
            title=course_data['title'],
            description=course_data['description'],
            author_id=str(course_data['author_id']),
            level=course_data['level'],
            status=course_data['status'],
            tags=course_data.get('tags', []),
            price=float(course_data['price']) if course_data['price'] else None,
            is_free=course_data['is_free'],
            duration_hours=course_data['duration_hours'],
            max_students=course_data['max_students'],
            image_url=course_data['image_url'],
            created_at=course_data['created_at'],
            updated_at=course_data['updated_at'],
            lessons=lessons,
            total_lessons=len(lessons),
            published_lessons=len([l for l in lessons if l['status'] == 'published']),
            total_enrollments=course_data.get('total_enrollments', 0),
            average_rating=course_data.get('average_rating', 0.0)
        )


class LessonDocument(Document):
    """Документ урока в Elasticsearch для детального поиска."""

    # Основная информация
    id = Keyword()
    course_id = Keyword()
    title = Text(analyzer='standard')
    content = Text(analyzer='standard')

    # Тип и статус
    lesson_type = Keyword()
    status = Keyword()
    order_index = Integer()

    # Дополнительная информация
    duration_minutes = Integer()
    video_url = Keyword()
    is_free_preview = Boolean()

    # Временные метки
    created_at = Date()
    updated_at = Date()

    # Информация о курсе
    course_title = Text(analyzer='standard')
    course_level = Keyword()
    course_author_id = Keyword()

    class Index:
        name = 'lessons'
        settings = {
            'number_of_shards': 2,
            'number_of_replicas': 1
        }

    @classmethod
    def from_domain_model(cls, lesson_data: Dict[str, Any], course_data: Dict[str, Any] = None) -> 'LessonDocument':
        """Создает документ Elasticsearch из доменной модели."""
        course_data = course_data or {}

        return cls(
            meta={'id': str(lesson_data['id'])},
            id=str(lesson_data['id']),
            course_id=str(lesson_data['course_id']),
            title=lesson_data['title'],
            content=lesson_data['content'],
            lesson_type=lesson_data['lesson_type'],
            status=lesson_data['status'],
            order_index=lesson_data['order_index'],
            duration_minutes=lesson_data['duration_minutes'],
            video_url=lesson_data['video_url'],
            is_free_preview=lesson_data['is_free_preview'],
            created_at=lesson_data['created_at'],
            updated_at=lesson_data['updated_at'],
            course_title=course_data.get('title', ''),
            course_level=course_data.get('level', ''),
            course_author_id=str(course_data['author_id']) if course_data.get('author_id') else ''
        )


def create_indices():
    """Создает индексы Elasticsearch."""
    CourseDocument.init()
    LessonDocument.init()


def delete_indices():
    """Удаляет индексы Elasticsearch."""
    try:
        CourseDocument._index.delete()
    except:
        pass

    try:
        LessonDocument._index.delete()
    except:
        pass


def recreate_indices():
    """Пересоздает индексы Elasticsearch."""
    delete_indices()
    create_indices()