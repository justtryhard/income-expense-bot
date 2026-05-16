from aiogram.fsm.state import State, StatesGroup


class AddEntry(StatesGroup):
    waiting_for_amount = State()


class StatsPeriod(StatesGroup):
    waiting_for_start = State()
    waiting_for_end = State()


class EditEntry(StatesGroup):
    waiting_for_id = State()


class EditAmount(StatesGroup):
    waiting_for_amount = State()