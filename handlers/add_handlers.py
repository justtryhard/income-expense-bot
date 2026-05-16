from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from config import ALLOWED_USER_ID
from keyboards.keyboards import main_menu, cancel_kb
from states import AddEntry
from utils.validators import is_positive_int


# Этот модуль отвечает за хендлеры добавления операций
# старт добавления дохода, расхода, ввод суммы, валидацию суммы, вызов transaction_service
# Хэндлеры не работают напрямую с Б

def is_allowed(user_id: int) -> bool:
    """Проверка доступа польщователя"""
    return user_id == ALLOWED_USER_ID


def register_add_handlers(dp: Dispatcher, transaction_service):
    """Регистрация хэндлеров добавления"""
    @dp.message(F.text.in_(["Новый расход", "Новый доход"]))
    async def add_start(message: Message, state: FSMContext):
        if not is_allowed(message.from_user.id):
            await message.answer("🚫 Доступ запрещен!")
            return

        category = "expense" if message.text == "Новый расход" else "income"

        await state.update_data(category=category)
        await state.set_state(AddEntry.waiting_for_amount)
        await message.answer("Введи сумму:", reply_markup=cancel_kb)

    @dp.message(AddEntry.waiting_for_amount)
    async def add_amount(message: Message, state: FSMContext):
        """Обработка введённой суммы"""
        if not is_positive_int(message.text):
            await message.answer("❌ Сумма должна быть целым положительным числом.")
            return

        data = await state.get_data()
        category = data["category"]
        amount = int(message.text)

        # ниже добавление операции через service (проверка дубликатов, идемпотентности)
        result = transaction_service.add_transaction(
            user_id=message.from_user.id,
            category=category,
            amount=amount,
            telegram_message_id=message.message_id
        )

        if not result["success"]:
            await message.answer(f"⚠️ Не сохранено, причина: {result["reason"]}", reply_markup=main_menu)
            await state.clear()
            return

        # далее подбор картинки под тип операции
        if category == "income":
            photo_file = FSInputFile("media/get.jpg")
            caption = "✅ Доход получен!"
        else:
            photo_file = FSInputFile("media/post.jpg")
            caption = "✅ Расход засчитан!"

        await message.answer_photo(
            photo=photo_file,
            caption=caption,
            reply_markup=main_menu
        )

        await state.clear()