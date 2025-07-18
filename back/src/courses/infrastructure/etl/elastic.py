from datetime import datetime
from typing import List

from elasticsearch import AsyncElasticsearch, helpers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from courses.infrastructure.models.course import Course
from courses.infrastructure.models.theme import Theme
from courses.infrastructure.models.lesson import Lesson


class CourseElasticSyncService:
    """
    Сервис для синхронизации курсов в Elasticsearch,
    включая темы и уроки, с поддержкой логического удаления.
    """

    def __init__(self, es: AsyncElasticsearch, session: AsyncSession):
        self.es = es
        self.session = session
        self.index = "courses_full"

    async def create_index_if_needed(self):
        if not await self.es.indices.exists(index=self.index):
            await self.es.indices.create(index=self.index, body={
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "level": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "category_id": {"type": "keyword"},
                        "author_id": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "is_deleted": {"type": "boolean"},
                        "themes": {
                            "type": "nested",
                            "properties": {
                                "id": {"type": "keyword"},
                                "title": {"type": "text"},
                                "description": {"type": "text"},
                                "order": {"type": "integer"},
                                "lessons": {
                                    "type": "nested",
                                    "properties": {
                                        "id": {"type": "keyword"},
                                        "title": {"type": "text"},
                                        "type": {"type": "keyword"},
                                        "duration": {"type": "integer"},
                                        "order": {"type": "integer"},
                                        "content": {"type": "text"}
                                    }
                                }
                            }
                        }
                    }
                }
            })

    async def fetch_courses_with_content(self, last_sync_time: datetime) -> List[Course]:
        stmt = (
            select(Course)
            .options(
                joinedload(Course.themes).joinedload(Theme.lessons)
            )
            .where(Course.updated_at > last_sync_time)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def serialize_course(self, course: Course) -> dict:
        return {
            "id": str(course.id),
            "title": course.title,
            "description": course.description,
            "level": course.level.value if course.level else None,
            "status": course.status.value if course.status else None,
            "category_id": str(course.category_id) if course.category_id else None,
            "author_id": str(course.author_id),
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat(),
            "is_deleted": course.is_deleted,  # добавлено
            "themes": [
                {
                    "id": str(theme.id),
                    "title": theme.title,
                    "description": theme.description,
                    "order": theme.order,
                    "lessons": [
                        {
                            "id": str(lesson.id),
                            "title": lesson.title,
                            "type": lesson.type.value if lesson.type else None,
                            "duration": lesson.duration,
                            "order": lesson.order,
                            "content": lesson.content
                        }
                        for lesson in theme.lessons
                    ]
                }
                for theme in course.themes
            ]
        }

    async def sync(self, last_sync_time: datetime) -> datetime:
        await self.create_index_if_needed()

        now = datetime.utcnow()
        courses = await self.fetch_courses_with_content(last_sync_time)

        actions = []
        for course in courses:
            if course.is_deleted:
                # Удаляем курс из Elasticsearch
                actions.append({
                    "_op_type": "delete",
                    "_index": self.index,
                    "_id": str(course.id),
                })
            else:
                # Индексируем актуальную версию курса
                doc = await self.serialize_course(course)
                actions.append({
                    "_op_type": "index",
                    "_index": self.index,
                    "_id": doc["id"],
                    "_source": doc
                })

        if actions:
            await helpers.async_bulk(self.es, actions)

        return now
