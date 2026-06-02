from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from config import ALLOWED_USER_ID


class AccessMiddleware(BaseMiddleware):
    pass