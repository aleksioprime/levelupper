from fastapi import APIRouter
from .extra import ping
from .courses import course

router = APIRouter()
router.include_router(course.router, prefix="/courses", tags=["courses"])