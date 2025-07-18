from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.course.application.services import CourseService
from src.course.application.schemas import CourseCreateSchema, CourseSchema
from src.course.presentation.dependencies.course import get_course_service

router = APIRouter()


@router.post("/courses/", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseCreateSchema,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseSchema:
    return await service.create(body)


@router.get("/courses/{course_id}", response_model=CourseSchema)
async def get_course(
    course_id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseSchema:
    return await service.get_by_id(course_id)


@router.get("/courses/", response_model=List[CourseSchema])
async def list_courses(
    service: Annotated[CourseService, Depends(get_course_service)],
    limit: int = 10,
    offset: int = 0,
) -> List[CourseSchema]:
    return await service.list(limit=limit, offset=offset)
