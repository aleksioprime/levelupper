class BaseException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)


class NotFoundException(BaseException):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)