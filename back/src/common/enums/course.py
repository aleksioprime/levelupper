import enum

class CourseLevel(enum.StrEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class CourseStatus(enum.StrEnum):
    draft = "draft"
    published = "published"
    archived = "archived"