from datetime import datetime
from zoneinfo import ZoneInfo


MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def get_moscow_now_str() -> str:
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d %H:%M:%S")