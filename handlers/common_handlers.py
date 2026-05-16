from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter

from config import ALLOWED_USER_ID
from keyboards.keyboards import main_menu

# Модуль отвечает за общие хендлеры (start, cancel, кнопка Назад
# Глобальные обработчики, которые работают из любого состояния


def is_allowed(user_id: int) -> bool:
    """Проверка доступа"""
    return user_id == ALLOWED_USER_ID


def register_common_handlers(dp: Dispatcher):
    """start. Полностью очищает и возвращает в главное меню"""
    @dp.message(CommandStart(), StateFilter("*"))
    async def start_handler(message: Message, state: FSMContext):
        await state.clear()

        if not is_allowed(message.from_user.id):
            await message.answer("🚫 Доступ запрещен!")
            return

        await message.answer("Выбери действие:", reply_markup=main_menu)


    # Далее кнопка Назад. Работает из любого состояния бота
    @dp.message(F.text == "🔙 Назад", StateFilter("*"))
    async def back_handler(message: Message, state: FSMContext):
        await state.clear()
        await message.delete()
        await message.answer("Выбери действие:", reply_markup=main_menu)

    # Команда /cancel - альтернатиный способ сбросить состояние
    @dp.message(F.text == "/cancel", StateFilter("*"))
    async def cancel_handler(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu)