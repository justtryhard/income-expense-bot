from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новый расход")],
        [KeyboardButton(text="Новый доход")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Редактировать")],
    ],
    resize_keyboard=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True,
)


def edit_actions_kb(record_id: int):
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