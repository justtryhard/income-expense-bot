from datetime import datetime
from zoneinfo import ZoneInfo

# Работа с московским временем
# Используется при создании записей в БД, чтобы серверное время не ломало даты
# Даже если сервер находится в другом часовом поясе - запись всегда будет по МСК

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def get_moscow_now_str() -> str:
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d %H:%M:%S")