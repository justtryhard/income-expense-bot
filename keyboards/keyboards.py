from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton


main_menu = ReplyKeyboardMarkup(    # Основная клавиатура бота, показывается пользователю после /start
    keyboard=[
        [KeyboardButton(text="Новый расход")],
        [KeyboardButton(text="Новый доход")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Редактировать")],
    ],
    resize_keyboard=True, # автоматически подгоняет размер кнопок
)



# Клавиатура отмены/возврата
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True,
)


def edit_actions_kb(record_id: int):
    """
    Клавиатура действий над записью
    Появляется после выбора ID операции
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
            ],
        ]
    )