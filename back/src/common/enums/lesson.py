import enum

class LessonType(enum.StrEnum):
    video = "video"
    text = "text"
    quiz = "quiz"
    external_link = "external_link"