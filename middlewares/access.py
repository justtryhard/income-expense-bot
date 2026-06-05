import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from config import ALLOWED_USER_ID

logger = logging.getLogger(__name__)


class AccessMiddleware(BaseMiddleware):
    """
    Глобальная проверка доступа.
    Бот предназначен для личного использования,
    поэтому обрабатывает сообщения только от пользователя,
    указанного в ALLOWED_USER_ID.
    Middleware позволяет убрать дублирующиеся проверки из каждого
    хендлера и централизовать контроль доступа.
    """
    async def __call__(self,
                       handler: Callable[
                           [TelegramObject, dict[str, Any]]
                           , Awaitable[Any]
                       ],
                       event: TelegramObject,
                       data: dict[str, Any]
                       ) -> Any:
            """
            Проверка пользователя до передачи события в handler.
            """
            user: User | None = data.get("event_from_user")
            if user is None:
                return await handler(event, data)
            if user.id != ALLOWED_USER_ID:
                logger.warning(
                    "Access denied for user_id=%s username=%s",
                    user.id,
                    user.username,
                )
                if isinstance(event, Message):
                    await event.answer("⛔ Доступ запрещён")
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⛔ Доступ запрещён",
                        show_alert=True,
                    )
                return None
            return await handler(event, data)