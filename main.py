import logging
import asyncio
import io
import matplotlib.pyplot as plt

from datetime import timedelta, datetime
from aiogram import types
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import API_TOKEN, DB_NAME, ALLOWED_USER_ID
from db import SQLiteConnection, HistoryRepository

# todo: Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
conn = SQLiteConnection(DB_NAME)
repository = HistoryRepository(conn)
repository.create_table()


#  FSM
class AddEntry(StatesGroup):
    """Состояние ожидания суммы при добавлении дохода/расхода"""
    waiting_for_amount = State()


class StatsPeriod(StatesGroup):
    """Состояния выбора начальной и конечной даты для статистики"""
    waiting_for_start = State()
    waiting_for_end = State()


class EditEntry(StatesGroup):
    """Состояние ожидания ID записи для редактирования"""
    waiting_for_id = State()


class EditAmount(StatesGroup):
    """Состояние ожидания новой суммы при редактировании"""
    waiting_for_amount = State()

# Кнопки основного меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новый расход")],
        [KeyboardButton(text="Новый доход")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Редактировать")]
    ],
    resize_keyboard=True  # кнопки подстраиваются под размер экрана
)

# Кнопка "назад"
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True
)


# Обработчики команд
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    if not is_allowed(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return
    await message.answer("Выбери действие:", reply_markup=main_menu)


# Отмена (должна быть выше обработчиков ввода)
@dp.message(F.text == "🔙 Назад")
async def cancel_any(message: Message, state: FSMContext):
    # очистка любого текущего состояния, если оно есть
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu)


@dp.message(F.text == "/cancel")
async def cancel_all(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного действия.", reply_markup=main_menu)
        return
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu)


# Добавление записи
@dp.message(F.text.in_(["Новый расход", "Новый доход"]))
async def add_start(message: Message, state: FSMContext):
    """
    Начало добавления новой операции.
    Устанавливает категорию (income/expense) в зависимости от нажатой кнопки
    и переводит бота в состояние ожидания суммы.
    """
    if not is_allowed(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return
    category = "expense" if message.text == "Новый расход" else "income"
    await state.update_data(category=category)
    await state.set_state(AddEntry.waiting_for_amount)
    await message.answer("Введи сумму:", reply_markup=cancel_kb)


# обработка введённой суммы
@dp.message(AddEntry.waiting_for_amount)
async def add_amount(message: Message, state: FSMContext):
    """
    Обработка введённой суммы, сохранение записи в БД и отправка картинки-подтверждения.
    """
    if not valid_input(message.text):
        await message.answer("❌ Сумма должна быть целым положительным числом.")
        return

    data = await state.get_data()
    category = data["category"]

    # Сохранение записи в БД (комментарий пустой, т.к. по ТЗ не нужен)
    repository.add_record(
        user_id=message.from_user.id,
        category=data["category"],
        amount=int(message.text),
        comment=""  # комментарий пустой т.к. не нужен по ТЗ, можно убрать поле из БД, но пока так
    )

    if category == "income":  # доход
        photo_file = FSInputFile("media/get.jpg")
        caption_text = "✅ Доход получен!"
    else:  # расход
        photo_file = FSInputFile("media/post.jpg")
        caption_text = "✅ Расход засчитан!"

    await message.answer_photo(photo=photo_file, caption=caption_text, reply_markup=main_menu)

    # await message.answer("Сохранено ✅", reply_markup=main_menu) # без картинки
    await state.clear()


# Статистика
calendar = SimpleCalendar()   # объект для работы с календарём


@dp.message(F.text == "Статистика")
async def stats_start(message: Message, state: FSMContext):
    """
    Запуск сбора статистики: запрос начальной даты через календарь.
    """
    if not is_allowed(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return
    await state.set_state(StatsPeriod.waiting_for_start)
    await message.answer("Выбери начальную дату:",
                         reply_markup=await calendar.start_calendar())


@dp.message(F.text == "Редактировать")
async def edit_start(message: Message, state: FSMContext):
    """
    Падаем в редактирование. Запрос ID записи.
    """
    if not is_allowed(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return

    await state.set_state(EditEntry.waiting_for_id)
    await message.answer("Введи ID записи для редактирования:", reply_markup=cancel_kb)


@dp.callback_query(F.data.startswith("edit_type:"))
async def edit_type_callback(callback: CallbackQuery):
    """
    Обработка нажатия на кнопку "Изменить тип" в инлайн-меню.
    Меняет категорию записи на противоположную (доход -> расход и наоборот).
    """
    record_id = int(callback.data.split(":")[1])

    record = repository.get_record_by_id(
        record_id, callback.from_user.id
    )

    if not record:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    _, category, _ = record
    new_category = "expense" if category == "income" else "income"

    repository.update_category(
        record_id,
        callback.from_user.id,
        new_category
    )

    photo_file = FSInputFile("media/red.jpg")
    caption_text = "✅ Тип успешно изменён."

    await callback.message.answer_photo(photo=photo_file, caption=caption_text, reply_markup=main_menu)
    await callback.answer()


@dp.message(EditEntry.waiting_for_id)
async def edit_get_id(message: Message, state: FSMContext):
    """
    Получаем ID записи от пользователя, проверяем существование и показываем
    инлайн-меню с действиями (изменить тип, сумму, удалить).
    """
    if not message.text.isdigit():
        await message.answer("❌ ID должен быть целым числом.")
        return

    record_id = int(message.text)

    record = repository.get_record_by_id(
        record_id, message.from_user.id
    )

    if not record:
        await message.answer("❌ Запись не найдена.")
        return

    id_, category, amount = record
    type_label = "Доход" if category == "income" else "Расход"

    await message.answer(
        f"ID: {id_}\n"
        f"Тип: {type_label}\n"
        f"Сумма: {amount} ₽",
        reply_markup=edit_actions_kb(id_)
    )

    await state.clear()


@dp.callback_query(F.data.startswith("delete:"))
async def delete_callback(callback: CallbackQuery):
    """
    Обработка кнопки "Удалить" – удаляем запись из БД.
    """
    record_id = int(callback.data.split(":")[1])

    repository.delete_record(
        record_id,
        callback.from_user.id
    )
    photo_file = FSInputFile("media/delete.jpg")
    caption_text = "🗑 Запись удалена."

    await callback.message.answer_photo(photo=photo_file, caption=caption_text, reply_markup=main_menu)
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_amount:"))
async def edit_amount_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработка кнопки "Изменить сумму". Сохраняем ID записи в состояние
    и переводим бота в режим ожидания новой суммы.
    """
    record_id = int(callback.data.split(":")[1])

    await state.update_data(record_id=record_id)
    await state.set_state(EditAmount.waiting_for_amount)

    await callback.message.answer("Введи новую сумму:", reply_markup=cancel_kb)
    await callback.answer()


@dp.message(EditAmount.waiting_for_amount)
async def process_new_amount(message: Message, state: FSMContext):
    """
    Получаем новую сумму, обновляем запись в БД.
    """
    if not valid_input(message.text):
        await message.answer("❌ Сумма должна быть положительным числом.")
        return

    data = await state.get_data()
    record_id = data["record_id"]

    repository.update_amount(
        record_id,
        message.from_user.id,
        int(message.text)
    )

    photo_file = FSInputFile("media/red_value.jpg")
    caption_text = "✅ Сумма обновлена."

    await message.answer_photo(photo=photo_file, caption=caption_text, reply_markup=main_menu)
    await state.clear()


# инпут начальной даты
@dp.callback_query(SimpleCalendarCallback.filter(), StatsPeriod.waiting_for_start)
async def stats_start_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """
    Получаем начальную дату из календаря, сохраняем в состояние и запрашиваем конечную.
    """
    selected, start_date = await calendar.process_selection(callback, callback_data)
    if selected:
        start_date = start_date.date()
        await state.update_data(start=start_date)
        await state.set_state(StatsPeriod.waiting_for_end)
        await callback.message.answer(
            "Выбери конечную дату:",
            reply_markup=await calendar.start_calendar()
        )
    await callback.answer()


# инпут конечной даты
@dp.callback_query(SimpleCalendarCallback.filter(), StatsPeriod.waiting_for_end)
async def stats_end_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """
    Получаем конечную дату, проверяем, что она не раньше начальной,
    формируем текстовый отчёт, а также список операций за день (если выбран один день)
    и график (если диапазон от недели до месяца).
    """
    selected, end_date = await calendar.process_selection(callback, callback_data)
    if selected:
        end_date = end_date.date()
        data = await state.get_data()
        start_date = data["start"]

        if end_date < start_date:
            await callback.message.answer("❌ Конечная дата меньше начальной!")
            await state.clear()
            return

        stats = repository.get_stats_for_period(
            callback.from_user.id, start_date, end_date
        )
        income_sum = stats['income_sum']
        income_count = stats['income_count']
        expense_sum = stats['expense_sum']
        expense_count = stats['expense_count']
        balance = income_sum - expense_sum

        text = (
            f"📊 Статистика за \n{start_date.strftime('%Y-%m-%d')} — {end_date.strftime('%Y-%m-%d')}\n\n"
            f"Доходы: {income_sum} ₽ (операций: {income_count})\n"
            f"Расходы: {expense_sum} ₽ (операций: {expense_count})\n\n"
            f"Итог: {balance} ₽"
        )

        await callback.message.answer(text, reply_markup=main_menu)

        if start_date == end_date:
            records = repository.get_records_by_date(
                callback.from_user.id, start_date
            )

            if records:
                text_records = f"\n\n📋 Операции за {start_date}:\n"
                for record_id, category, amount in records:
                    type_label = "Доход" if category == "income" else "Расход"
                    text_records += f"ID {record_id} — {type_label} — {amount} ₽\n"

                await callback.message.answer(text_records)
            else:
                await callback.message.answer("Операций за этот день нет.")


        # если пользователь запросил от недели до месяца, выдаём график:
        if 6 <= (end_date - start_date).days <= 31:
            daily_data = repository.get_daily_stats(
                callback.from_user.id, start_date, end_date
            )

            if daily_data:
                data_dict = {}
                for row in daily_data:
                    d, inc, exp = row
                    if isinstance(d, str):
                        d = datetime.strptime(d, '%Y-%m-%d').date()
                    data_dict[d] = (inc, exp)

                dates = []
                incomes = []
                expenses = []
                current = start_date
                while current <= end_date:
                    dates.append(current.strftime('%Y-%m-%d'))
                    inc, exp = data_dict.get(current, (0, 0))
                    incomes.append(inc)
                    expenses.append(exp)
                    current += timedelta(days=1)

                plt.figure(figsize=(12, 6))
                x = range(len(dates))
                width = 0.35

                plt.bar([i - width / 2 for i in x], incomes, width, label='Доход', color='green', alpha=0.7)
                plt.bar([i + width / 2 for i in x], expenses, width, label='Расход', color='red', alpha=0.7)

                plt.xlabel('Дата')
                plt.ylabel('Сумма')
                plt.title('Доходы и расходы по дням')
                plt.xticks(x, dates, rotation=45)
                plt.legend()
                plt.tight_layout()

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plt.close()

                await callback.message.answer_photo(
                    photo=types.BufferedInputFile(buf.read(), filename='chart.png'),
                    caption="Диаграмма доходов и расходов"
                )
            else:
                await callback.message.answer("Нет данных для построения графика.")

        await state.clear()
    await callback.answer()


def edit_actions_kb(record_id: int):
    """
    Создаёт инлайн-клавиатуру с кнопками действий для конкретной записи.
    Принимает ID записи, подставляет его в callback_data.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔁 Изменить тип",
                    callback_data=f"edit_type:{record_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Изменить сумму",
                    callback_data=f"edit_amount:{record_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete:{record_id}"
                )
            ]
        ]
    )


def valid_input(summ: str) -> bool:
    """
    проверяем валидность введённой суммы
    """
    if summ.isdigit() and int(summ) > 0:
        return True
    return False


def is_allowed(user_id: int) -> bool:
    """
    проверка, что бота использует user из config
    """
    return user_id == ALLOWED_USER_ID


# Запуск
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
