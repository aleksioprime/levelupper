"""
Сервис для работы с Elasticsearch.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q

from src.common.core.config import settings
from src.common.elasticsearch.models import CourseDocument, LessonDocument
from src.courses.application.schemas import CourseSearchSchema, PaginationSchema


class ElasticsearchService:
    """Сервис для работы с Elasticsearch."""

    def __init__(self):
        # Подготавливаем параметры подключения для новых версий Elasticsearch
        connection_params = {
            'hosts': [settings.elasticsearch.url],
        }
        
        # Добавляем аутентификацию если есть
        if settings.elasticsearch.username:
            connection_params['basic_auth'] = (
                settings.elasticsearch.username, 
                settings.elasticsearch.password
            )
        
        self.client = AsyncElasticsearch(**connection_params)

    async def close(self):
        """Закрывает соединение с Elasticsearch."""
        await self.client.close()

    async def health_check(self) -> bool:
        """Проверяет доступность Elasticsearch."""
        try:
            health = await self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except Exception:
            return False

    async def search_courses(
        self,
        search_params: CourseSearchSchema,
        pagination: PaginationSchema
    ) -> Dict[str, Any]:
        """
        Поиск курсов в Elasticsearch с фильтрацией и пагинацией.
        """
        s = Search(using=self.client, index='courses')

        # Базовый поиск по тексту
        if search_params.query:
            s = s.query(
                'multi_match',
                query=search_params.query,
                fields=['title^3', 'description^2', 'tags^2', 'lessons.title', 'lessons.content'],
                type='best_fields',
                fuzziness='AUTO'
            )

        # Фильтры
        filters = []

        if search_params.level:
            filters.append(Q('term', level=search_params.level))

        if search_params.status:
            filters.append(Q('term', status=search_params.status))

        if search_params.is_free is not None:
            filters.append(Q('term', is_free=search_params.is_free))

        if search_params.author_id:
            filters.append(Q('term', author_id=str(search_params.author_id)))

        if search_params.tags:
            for tag in search_params.tags:
                filters.append(Q('term', tags=tag))

        # Фильтрация по цене
        if search_params.price_from is not None or search_params.price_to is not None:
            price_range = {}
            if search_params.price_from is not None:
                price_range['gte'] = float(search_params.price_from)
            if search_params.price_to is not None:
                price_range['lte'] = float(search_params.price_to)
            filters.append(Q('range', price=price_range))

        # Применяем фильтры
        if filters:
            s = s.filter('bool', must=filters)

        # Сортировка (по умолчанию по релевантности, затем по дате создания)
        if not search_params.query:
            s = s.sort('-created_at')
        else:
            s = s.sort('_score', '-created_at')

        # Пагинация
        s = s[pagination.offset:pagination.offset + pagination.limit]

        # Агрегации для статистики
        s.aggs.bucket('levels', 'terms', field='level') \
              .bucket('free_courses', 'terms', field='is_free') \
              .bucket('authors', 'terms', field='author_id')

        try:
            response = await s.execute()

            # Формируем результат
            courses = []
            for hit in response.hits:
                course_data = hit.to_dict()
                course_data['score'] = hit.meta.score if hasattr(hit.meta, 'score') else None
                courses.append(course_data)

            return {
                'courses': courses,
                'total': response.hits.total.value,
                'aggregations': {
                    'levels': [bucket.to_dict() for bucket in response.aggregations.levels.buckets],
                    'free_courses': [bucket.to_dict() for bucket in response.aggregations.free_courses.buckets],
                    'top_authors': [bucket.to_dict() for bucket in response.aggregations.authors.buckets[:5]]
                }
            }

        except Exception as e:
            # Логируем ошибку и возвращаем пустой результат
            print(f"Elasticsearch search error: {e}")
            return {
                'courses': [],
                'total': 0,
                'aggregations': {
                    'levels': [],
                    'free_courses': [],
                    'top_authors': []
                }
            }

    async def search_lessons(
        self,
        query: str,
        course_id: Optional[UUID] = None,
        pagination: Optional[PaginationSchema] = None
    ) -> Dict[str, Any]:
        """
        Поиск уроков в Elasticsearch.
        """
        s = Search(using=self.client, index='lessons')

        # Базовый поиск по тексту
        if query:
            s = s.query(
                'multi_match',
                query=query,
                fields=['title^3', 'content^2', 'course_title'],
                type='best_fields',
                fuzziness='AUTO'
            )

        # Фильтр по курсу
        if course_id:
            s = s.filter('term', course_id=str(course_id))

        # Фильтр только опубликованных уроков
        s = s.filter('term', status='published')

        # Пагинация
        if pagination:
            s = s[pagination.offset:pagination.offset + pagination.limit]
        else:
            s = s[:50]  # Ограничение по умолчанию

        # Сортировка
        if not query:
            s = s.sort('course_id', 'order_index')
        else:
            s = s.sort('_score', 'course_id', 'order_index')

        try:
            response = await s.execute()

            lessons = []
            for hit in response.hits:
                lesson_data = hit.to_dict()
                lesson_data['score'] = hit.meta.score if hasattr(hit.meta, 'score') else None
                lessons.append(lesson_data)

            return {
                'lessons': lessons,
                'total': response.hits.total.value
            }

        except Exception as e:
            print(f"Elasticsearch lessons search error: {e}")
            return {
                'lessons': [],
                'total': 0
            }

    async def suggest_courses(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """
        Автодополнение для курсов.
        """
        suggest_body = {
            'course_suggest': {
                'prefix': query,
                'completion': {
                    'field': 'title.suggest',
                    'size': size
                }
            }
        }

        try:
            response = await self.client.search(
                index='courses',
                body={'suggest': suggest_body}
            )

            suggestions = []
            if 'suggest' in response and 'course_suggest' in response['suggest']:
                for suggestion in response['suggest']['course_suggest'][0]['options']:
                    suggestions.append({
                        'text': suggestion['text'],
                        'score': suggestion['_score'],
                        'source': suggestion['_source']
                    })

            return suggestions

        except Exception as e:
            print(f"Elasticsearch suggest error: {e}")
            return []

    async def get_popular_courses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получение популярных курсов (по количеству записей).
        """
        s = Search(using=self.client, index='courses')
        s = s.filter('term', status='published')
        s = s.sort('-total_enrollments', '-average_rating', '-created_at')
        s = s[:limit]

        try:
            response = await s.execute()

            courses = []
            for hit in response.hits:
                courses.append(hit.to_dict())

            return courses

        except Exception as e:
            print(f"Elasticsearch popular courses error: {e}")
            return []

    async def get_recommendations(
        self,
        user_id: UUID,
        enrolled_course_ids: List[UUID],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Получение рекомендаций курсов на основе записанных курсов.
        """
        if not enrolled_course_ids:
            return await self.get_popular_courses(limit)

        # Получаем теги из записанных курсов
        s = Search(using=self.client, index='courses')
        s = s.filter('terms', id=[str(cid) for cid in enrolled_course_ids])
        s = s.source(['tags', 'level'])

        try:
            enrolled_response = await s.execute()

            # Собираем теги и уровни
            all_tags = set()
            levels = set()
            for hit in enrolled_response.hits:
                course = hit.to_dict()
                all_tags.update(course.get('tags', []))
                levels.add(course.get('level'))

            # Ищем похожие курсы
            rec_search = Search(using=self.client, index='courses')
            rec_search = rec_search.filter('term', status='published')

            # Исключаем уже записанные курсы
            rec_search = rec_search.exclude('terms', id=[str(cid) for cid in enrolled_course_ids])

            # Буст по тегам и уровням
            should_queries = []
            for tag in all_tags:
                should_queries.append(Q('term', tags__boost=2.0, tags=tag))
            for level in levels:
                should_queries.append(Q('term', level__boost=1.5, level=level))

            if should_queries:
                rec_search = rec_search.query('bool', should=should_queries)

            rec_search = rec_search.sort('-_score', '-total_enrollments')
            rec_search = rec_search[:limit]

            response = await rec_search.execute()

            recommendations = []
            for hit in response.hits:
                course_data = hit.to_dict()
                course_data['recommendation_score'] = hit.meta.score if hasattr(hit.meta, 'score') else 0
                recommendations.append(course_data)

            return recommendations

        except Exception as e:
            print(f"Elasticsearch recommendations error: {e}")
            return await self.get_popular_courses(limit)