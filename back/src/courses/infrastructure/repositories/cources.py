from courses.infrastructure.uow import CourseUoW

class CourseService:
    def __init__(self, uow: CourseUoW):
        self.uow = uow

    async def create_course(self, data: dict):
        async with self.uow as uow:
            return await uow.courses.create(data)