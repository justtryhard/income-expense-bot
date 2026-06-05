import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import API_TOKEN, DB_NAME
from database.connection import SQLiteConnection
from database.schema import HistorySchema

from repositories.transaction_repository import TransactionRepository
from repositories.stats_repository import StatsRepository
from repositories.duplicate_guard import DuplicateGuard

from services.transaction_service import TransactionService
from services.stats_service import StatsService

from handlers.common_handlers import register_common_handlers
from handlers.add_handlers import register_add_handlers
from handlers.stats_handlers import register_stats_handlers
from handlers.edit_handlers import register_edit_handlers

from middlewares.access import AccessMiddleware


logging.basicConfig(level=logging.INFO)


async def main():
    """
    Главная функция приложения
    """
    bot = Bot(token=API_TOKEN)  # создание ТГ бота
    try:
        await healthcheck(bot)
        dp = Dispatcher(storage=MemoryStorage()) # создание диспетчера
        dp.message.middleware(AccessMiddleware())
        dp.callback_query.middleware(AccessMiddleware())

        connection = SQLiteConnection(DB_NAME) # подключение к БД

        schema = HistorySchema(connection) # создание таблиц БД
        schema.create_table()

        # создание репозиториев:
        transaction_repository = TransactionRepository(connection)
        stats_repository = StatsRepository(connection)
        duplicate_guard = DuplicateGuard(connection)

        # создание сервисов, которые используют репозитории
        transaction_service = TransactionService(
            transaction_repository=transaction_repository,
            duplicate_guard=duplicate_guard
        )

        stats_service = StatsService(
            stats_repository=stats_repository,
            transaction_repository=transaction_repository
        )

        # регистрация хендлеров каждый со своими роутами в диспетчере
        register_common_handlers(dp)
        register_add_handlers(dp, transaction_service)
        register_stats_handlers(dp, stats_service)
        register_edit_handlers(dp, transaction_service)

        # запуск поллинга
        await dp.start_polling(bot)
    finally:
        logging.info("Shutting down")
        await bot.session.close()


async def healthcheck(bot: Bot) -> None:
    """
    Проверка, что бот может подключиться к telegram api
    """
    me = await bot.get_me()
    logging.info("Bot started: @%s", me.username)

# точка входа
if __name__ == "__main__":
    asyncio.run(main())