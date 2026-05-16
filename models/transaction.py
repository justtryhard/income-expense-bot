from dataclasses import dataclass
from enum import Enum


class TransactionCategory(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    user_id: int
    category: TransactionCategory
    amount: int
    comment: str
    telegram_message_id: int