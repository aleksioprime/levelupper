from fastapi import Depends
from shared.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from courses.infrastructure.uow import CourseUoW
from courses.application.services import CourseService

def get_course_service(session: AsyncSession = Depends(get_session)) -> CourseService:
    return CourseService(CourseUoW(session))