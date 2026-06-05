from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.keyboards import cancel_kb, edit_actions_kb, main_menu
from states import EditAmount, EditEntry
from utils.validators import is_positive_int

# Хендлеры редактирования операций
# Не работают напрямую с БД

def register_edit_handlers(dp: Dispatcher, transaction_service):
    """Начало редактирования (нажатие кнопки)"""
    @dp.message(F.text == "Редактировать")
    async def edit_start(message: Message, state: FSMContext):
        # ожидание ввода айди
        await state.set_state(EditEntry.waiting_for_id)
        await message.answer("Введи ID записи:", reply_markup=cancel_kb)

    # далее получение ID записи
    @dp.message(EditEntry.waiting_for_id)
    async def edit_get_id(message: Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer("❌ ID должен быть целым числом.")
            return

        record_id = int(message.text)
        record = transaction_service.get_record_by_id(
            record_id,
            message.from_user.id
        )

        if not record:
            await message.answer("❌ Запись не найдена.")
            return

        id_, category, amount = record
        type_label = "Доход" if category == "income" else "Расход"

        await message.answer(
            f"ID: {id_}\nТип: {type_label}\nСумма: {amount} ₽",
            reply_markup=edit_actions_kb(id_)
        )

        await state.clear()

    # Изменение типа операции
    @dp.callback_query(F.data.startswith("edit_type:"))
    async def edit_type_callback(callback: CallbackQuery):
        record_id = int(callback.data.split(":")[1])

        success = transaction_service.switch_category(
            record_id,
            callback.from_user.id
        )

        if not success:
            await callback.answer("Запись не найдена", show_alert=True)
            return

        await callback.message.answer_photo(
            photo=FSInputFile("media/red.jpg"),
            caption="✅ Тип успешно изменён.",
            reply_markup=main_menu
        )
        await callback.answer()

    # Удаление записи
    @dp.callback_query(F.data.startswith("delete:"))
    async def delete_callback(callback: CallbackQuery):
        record_id = int(callback.data.split(":")[1])

        transaction_service.delete_record(
            record_id,
            callback.from_user.id
        )

        await callback.message.answer_photo(
            photo=FSInputFile("media/delete.jpg"),
            caption="🗑 Запись удалена.",
            reply_markup=main_menu
        )
        await callback.answer()

    # Начало изменения суммы
    @dp.callback_query(F.data.startswith("edit_amount:"))
    async def edit_amount_callback(callback: CallbackQuery, state: FSMContext):
        record_id = int(callback.data.split(":")[1])

        await state.update_data(record_id=record_id)
        await state.set_state(EditAmount.waiting_for_amount)

        await callback.message.answer("Введи новую сумму:", reply_markup=cancel_kb)
        await callback.answer()

    # Обработка новой суммы
    @dp.message(EditAmount.waiting_for_amount)
    async def process_new_amount(message: Message, state: FSMContext):
        if not is_positive_int(message.text):
            await message.answer("❌ Сумма должна быть положительным числом.")
            return

        data = await state.get_data()
        record_id = data["record_id"]

        transaction_service.update_amount(
            record_id,
            message.from_user.id,
            int(message.text)
        )

        await message.answer_photo(
            photo=FSInputFile("media/red_value.jpg"),
            caption="✅ Сумма обновлена.",
            reply_markup=main_menu
        )

        await state.clear()