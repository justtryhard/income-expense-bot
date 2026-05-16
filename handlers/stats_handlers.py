import io
from datetime import timedelta, datetime

import matplotlib.pyplot as plt
from aiogram import Dispatcher, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import ALLOWED_USER_ID
from keyboards.keyboards import main_menu
from states import StatsPeriod

# Хендлеры статистики
# Не работают напрямую с БД
# stats_service инкапсулирует всю бизнес логику статистики


def is_allowed(user_id: int) -> bool:
    """Проверка пользователя"""
    return user_id == ALLOWED_USER_ID


def register_stats_handlers(dp: Dispatcher, stats_service):
    """Регистрация хендлеров статистики"""
    @dp.message(F.text == "Статистика")
    async def stats_start(message: Message, state: FSMContext):
        if not is_allowed(message.from_user.id):
            await message.answer("🚫 Доступ запрещен!")
            return

        # переход в состояние выбора начальной даты
        await state.set_state(StatsPeriod.waiting_for_start)
        calendar = SimpleCalendar()

        await message.answer(
            "Выбери начальную дату:",
            reply_markup=await calendar.start_calendar()
        )

    # выбор начальной даты
    @dp.callback_query(SimpleCalendarCallback.filter(), StatsPeriod.waiting_for_start)
    async def stats_start_date(
        callback: CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
    ):
        calendar = SimpleCalendar()
        selected, start_date = await calendar.process_selection(callback, callback_data)

        if selected:
            await state.update_data(start=start_date.date())
            await state.set_state(StatsPeriod.waiting_for_end)

            await callback.message.answer(
                "Выбери конечную дату:",
                reply_markup=await calendar.start_calendar()
            )

        await callback.answer()

    # выбор конечной даты
    @dp.callback_query(SimpleCalendarCallback.filter(), StatsPeriod.waiting_for_end)
    async def stats_end_date(
            callback: CallbackQuery,
            callback_data: SimpleCalendarCallback,
            state: FSMContext
    ):
        calendar = SimpleCalendar()
        selected, end_date = await calendar.process_selection(callback, callback_data)

        if selected:
            end_date = end_date.date()
            data = await state.get_data()
            start_date = data["start"]

            if end_date < start_date:
                await callback.message.answer("❌ Конечная дата меньше начальной!")
                await state.clear()
                await callback.answer()
                return

            # получение статистики
            stats = stats_service.get_period_stats(
                callback.from_user.id,
                start_date,
                end_date
            )

            income_sum = stats["income_sum"]
            income_count = stats["income_count"]
            expense_sum = stats["expense_sum"]
            expense_count = stats["expense_count"]
            balance = income_sum - expense_sum

            text = (
                f"📊 Статистика за\n"
                f"{start_date.strftime('%Y-%m-%d')} — {end_date.strftime('%Y-%m-%d')}\n\n"
                f"Доходы: {income_sum} ₽ (операций: {income_count})\n"
                f"Расходы: {expense_sum} ₽ (операций: {expense_count})\n\n"
                f"Итог: {balance} ₽"
            )

            await callback.message.answer(text, reply_markup=main_menu)

            # если выбран 1 день, показывается список операций
            if start_date == end_date:
                records = stats_service.get_records_for_day(
                    callback.from_user.id,
                    start_date
                )

                if records:
                    text_records = f"\n\n📋 Операции за {start_date}:\n"
                    for record_id, category, amount in records:
                        type_label = "Доход" if category == "income" else "Расход"
                        text_records += f"ID {record_id} — {type_label} — {amount} ₽\n"

                    await callback.message.answer(text_records)
                else:
                    await callback.message.answer("Операций за этот день нет.")

            # если срок от 7 до 31 дня - строится график
            if 6 <= (end_date - start_date).days <= 31:
                daily_data = stats_service.get_daily_stats(
                    callback.from_user.id,
                    start_date,
                    end_date
                )

                if daily_data:
                    data_dict = {}

                    for row in daily_data:
                        d, inc, exp = row

                        if isinstance(d, str):
                            d = datetime.strptime(d, "%Y-%m-%d").date()

                        data_dict[d] = (inc, exp)

                    # данные для matplotlib
                    dates = []
                    incomes = []
                    expenses = []

                    current = start_date
                    while current <= end_date:
                        dates.append(current.strftime("%Y-%m-%d"))

                        inc, exp = data_dict.get(current, (0, 0))
                        incomes.append(inc)
                        expenses.append(exp)

                        current += timedelta(days=1)

                    plt.figure(figsize=(12, 6))

                    x = range(len(dates))
                    width = 0.35

                    plt.bar(
                        [i - width / 2 for i in x],
                        incomes,
                        width,
                        label="Доход",
                        color="green",
                        alpha=0.7
                    )

                    plt.bar(
                        [i + width / 2 for i in x],
                        expenses,
                        width,
                        label="Расход",
                        color="red",
                        alpha=0.7
                    )

                    plt.xlabel("Дата")
                    plt.ylabel("Сумма")
                    plt.title("Доходы и расходы по дням")
                    plt.xticks(x, dates, rotation=45)
                    plt.legend()
                    plt.tight_layout()

                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)
                    plt.close()

                    await callback.message.answer_photo(
                        photo=types.BufferedInputFile(
                            buf.read(),
                            filename="chart.png"
                        ),
                        caption="Диаграмма доходов и расходов"
                    )
                else:
                    await callback.message.answer("Нет данных для построения графика.")

            await state.clear()

        await callback.answer()