""" Зависимость для получения экземпляра CourseService """

from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import Depends, Query

from src.schemas.pagination import BasePaginationParams
from src.schemas.course import CourseQueryParams
from src.dependencies.uow import get_unit_of_work
from src.dependencies.pagination import get_pagination_params
from src.repositories.uow import UnitOfWork
from src.services.course import CourseService
from src.elasticsearch.client import get_elasticsearch_client
from src.repositories.elasticsearch.course import CourseElasticSearchRepository


def get_course_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        query: Optional[str] = Query(None, description="Поисковый запрос по названию и описанию"),
        group_ids: Optional[List[UUID]] = Query(None, description="Список ID групп для фильтрации"),
        moderator_ids: Optional[List[UUID]] = Query(None, description="Список ID модераторов для фильтрации"),
) -> CourseQueryParams:
    """ Dependency для получения параметров запроса курсов """

    return CourseQueryParams(
        limit=pagination.limit,
        offset=pagination.offset,
        query=query,
        group_ids=group_ids,
        moderator_ids=moderator_ids,
    )

async def get_elasticsearch_course_repository(
    es_client=Depends(get_elasticsearch_client)
) -> CourseElasticSearchRepository:
    """Dependency для получения репозитория Elasticsearch курсов"""
    return CourseElasticSearchRepository(es_client)

async def get_course_service(
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
        es_repo: CourseElasticSearchRepository = Depends(get_elasticsearch_course_repository),
) -> CourseService:
    """ Dependency для получения сервиса управления курсами """
    return CourseService(uow=uow, elasticsearch=es_repo)