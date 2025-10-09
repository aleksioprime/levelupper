"""Репозиторий для работы с курсами в Elasticsearch"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import date

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from src.core.config import settings
from src.schemas.course import (
    CourseElasticsearchSchema,
    CourseQueryParams,
)

logger = logging.getLogger(__name__)


class CourseElasticSearchRepository:
    """Репозиторий для поиска курсов в Elasticsearch (только чтение)"""

    def __init__(self, client: AsyncElasticsearch):
        self.client = client
        self.es_config = settings.elasticsearch

    async def get_course(self, course_id: uuid.UUID) -> Optional[CourseElasticsearchSchema]:
        """Получить курс по ID"""
        try:
            response = await self.client.get(
                index=self.es_config.courses_index,
                id=str(course_id)
            )
            return CourseElasticsearchSchema(**response['_source'])
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get course {course_id}: {e}")
            return None

    async def search_courses(
        self,
        params: CourseQueryParams
    ) -> tuple[List[CourseElasticsearchSchema], int]:
        """Поиск курсов"""
        try:
            query = self._build_course_search_query(params)

            from_offset = (params.page - 1) * params.size

            response = await self.client.search(
                index=self.es_config.courses_index,
                body={
                    "query": query,
                    "from": from_offset,
                    "size": params.size,
                    "sort": [{"created_at": {"order": "desc"}}]
                }
            )

            courses = [
                CourseElasticsearchSchema(**hit['_source'])
                for hit in response['hits']['hits']
            ]
            total = response['hits']['total']['value']

            return courses, total

        except Exception as e:
            logger.error(f"Failed to search courses: {e}")
            return [], 0

    def _build_course_search_query(self, params: CourseQueryParams) -> Dict[str, Any]:
        """Построить запрос поиска курсов"""
        must_clauses = []

        if params.query:
            must_clauses.append({
                "multi_match": {
                    "query": params.query,
                    "fields": ["title^2", "description"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })

        if params.group_ids:
            must_clauses.append({
                "nested": {
                    "path": "groups",
                    "query": {
                        "terms": {
                            "groups.id": [str(gid) for gid in params.group_ids]
                        }
                    }
                }
            })

        if params.moderator_ids:
            must_clauses.append({
                "nested": {
                    "path": "moderators",
                    "query": {
                        "terms": {
                            "moderators.user_id": [str(mid) for mid in params.moderator_ids]
                        }
                    }
                }
            })

        if not must_clauses:
            return {"match_all": {}}

        return {"bool": {"must": must_clauses}}




__all__ = ["ElasticsearchCourseRepository"]