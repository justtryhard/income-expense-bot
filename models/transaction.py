from dataclasses import dataclass
from enum import Enum

# Модель транзакции
# используется датакласс для упрощения создания модели

class TransactionCategory(str, Enum):
    """
    Типы транзакций
    Enum защищает от опечаток и случайных строк
    """
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    user_id: int
    category: TransactionCategory
    amount: int
    comment: str
    telegram_message_id: int