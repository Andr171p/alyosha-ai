from datetime import datetime

import pytz

TIMEZONE = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получение текущего времени в заданном часовом поясе"""

    return datetime.now(TIMEZONE)
