import enum

class EnrollmentStatus(enum.StrEnum):
    enrolled = "enrolled"
    completed = "completed"
    dropped = "dropped"