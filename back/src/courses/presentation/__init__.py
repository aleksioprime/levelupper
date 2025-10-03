from fastapi import APIRouter

from .routes.course import router as course_router
from .routes.lesson import router as lesson_router
from .routes.assignment import router as assignment_router
from .routes.enrollment import router as enrollment_router

# Создаем главный роутер для курсов
router = APIRouter()

# Включаем все под-роутеры
router.include_router(course_router, tags=["courses"])
router.include_router(lesson_router, tags=["lessons"])
router.include_router(assignment_router, tags=["assignments"])
router.include_router(enrollment_router, tags=["enrollments"])

__all__ = ["router"]
