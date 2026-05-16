from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import ALLOWED_USER_ID
from keyboards.keyboards import main_menu


class StatsPeriod(StatesGroup):
    waiting_for_start = State()
    waiting_for_end = State()


def is_allowed(user_id: int) -> bool:
    return user_id == ALLOWED_USER_ID


def register_stats_handlers(dp: Dispatcher, stats_service):

    @dp.message(F.text == "Статистика")
    async def stats_start(message: Message, state: FSMContext):
        if not is_allowed(message.from_user.id):
            await message.answer("🚫 Доступ запрещен!")
            return

        await state.set_state(StatsPeriod.waiting_for_start)
        calendar = SimpleCalendar()

        await message.answer(
            "Выбери начальную дату:",
            reply_markup=await calendar.start_calendar()
        )

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