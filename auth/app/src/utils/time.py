import datetime


def utc_now() -> datetime.datetime:
    """
    Возвращает текущее UTC время
    """

    return datetime.datetime.now(datetime.UTC)