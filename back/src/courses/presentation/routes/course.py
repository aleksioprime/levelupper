from typing import Annotated, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from src.courses.application.services import CourseService
from src.courses.application.schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseSchema,
    CourseSearchSchema, PaginationSchema
)
from src.courses.presentation.dependencies.course import get_course_service
from src.common.elasticsearch import get_elasticsearch_service
from src.common.elasticsearch.service import ElasticsearchService

router = APIRouter()


@router.post("/courses/", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseCreateSchema,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseSchema:
    """Создание нового курса."""
    return await service.create(body)


@router.get("/courses/{course_id}", response_model=CourseSchema)
async def get_course(
    course_id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseSchema:
    """Получение курса по ID."""
    return await service.get_by_id(course_id)


@router.put("/courses/{course_id}", response_model=CourseSchema)
async def update_course(
    course_id: UUID,
    body: CourseUpdateSchema,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseSchema:
    """Обновление курса."""
    return await service.update(course_id, body)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
):
    """Удаление курса."""
    deleted = await service.delete(course_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")


@router.get("/courses/", response_model=List[CourseSchema])
async def list_courses(
    service: Annotated[CourseService, Depends(get_course_service)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[CourseSchema]:
    """Получение списка курсов с пагинацией."""
    return await service.list(limit=limit, offset=offset)


@router.get("/authors/{author_id}/courses", response_model=List[CourseSchema])
async def get_courses_by_author(
    author_id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[CourseSchema]:
    """Получение курсов по автору."""
    return await service.get_by_author(author_id, limit=limit, offset=offset)


@router.post("/courses/search", response_model=Dict[str, Any])
async def search_courses(
    search_params: CourseSearchSchema,
    pagination: PaginationSchema,
    es_service: Annotated[ElasticsearchService, Depends(get_elasticsearch_service)],
) -> Dict[str, Any]:
    """Поиск курсов через Elasticsearch."""
    return await es_service.search_courses(search_params, pagination)


@router.get("/courses/popular/", response_model=List[Dict[str, Any]])
async def get_popular_courses(
    es_service: Annotated[ElasticsearchService, Depends(get_elasticsearch_service)],
    limit: int = Query(10, ge=1, le=50),
) -> List[Dict[str, Any]]:
    """Получение популярных курсов."""
    return await es_service.get_popular_courses(limit)


@router.get("/courses/recommend/{user_id}", response_model=List[Dict[str, Any]])
async def get_course_recommendations(
    user_id: UUID,
    es_service: Annotated[ElasticsearchService, Depends(get_elasticsearch_service)],
    service: Annotated[CourseService, Depends(get_course_service)],
    limit: int = Query(5, ge=1, le=20),
) -> List[Dict[str, Any]]:
    """Получение рекомендаций курсов для пользователя."""
    # Здесь можно получить список курсов, на которые записан пользователь
    # Для простоты пока передаем пустой список
    enrolled_course_ids = []
    return await es_service.get_recommendations(user_id, enrolled_course_ids, limit)
