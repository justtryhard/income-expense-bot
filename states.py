from aiogram.fsm.state import State, StatesGroup

# FSM состояния приложения. Используется для пошагового общения с юзером


class AddEntry(StatesGroup):
    """
    Состояния добавления операций
    """
    waiting_for_amount = State()


class StatsPeriod(StatesGroup):
    """
    Состояния выбора периода статистики
    """
    waiting_for_start = State()
    waiting_for_end = State()


class EditEntry(StatesGroup):
    """
    Состояния редактирования записи
    """
    waiting_for_id = State()


class EditAmount(StatesGroup):
    """
    Состояния изменения сумм
    """
    waiting_for_amount = State()