# Сервис работы с транзакциями
# Здесь находится бизнес-логика
# Хендлеры НЕ работают напрямую с БД, а обращаются к service-слою.

class TransactionService:
    def __init__(self, transaction_repository, duplicate_guard):
        """ Dependency Injection
        Передаю repository и duplicate_guard извне"""
        self.transaction_repository = transaction_repository
        self.duplicate_guard = duplicate_guard

    def add_transaction(
        self,
        user_id: int,
        category: str,
        amount: int,
        telegram_message_id: int,
        comment: str = ""
    ):
        """Добавление новой операции
        Перед записью проверяем:
        1 - не было ли похожей операции недавно
        2 - не отправвлялось ли это же телеграм сообщение"""
        if self.duplicate_guard.is_recent_duplicate(user_id=user_id, category=category, amount=amount):
            return {"success": False, "reason": "Одинаковый тип и сумма за установленное время"}
        # проверка на одинаковые операции за последние N секунд

        inserted = self.transaction_repository.add_record(              # попытка сохранить запись
            user_id=user_id,
            category=category,
            amount=amount,
            comment=comment,
            telegram_message_id=telegram_message_id      # защита от повторной обработки одного telegram message
        )

        # если add_record вернул False, значит это дубликат telegram message_id
        if not inserted:
            return {
                "success": False,
                "reason": "Дубликат сообщения"
            }
        # успешное сохранение
        return {"success": True, "reason": None}

    def get_record_by_id(self, record_id: int, user_id: int):
        """Получение записи по ID"""
        return self.transaction_repository.get_record_by_id(record_id, user_id)

    def switch_category(self, record_id: int, user_id: int):
        """Переключение типа операции"""
        record = self.transaction_repository.get_record_by_id(record_id, user_id)

        if not record:
            return False

        _, category, _ = record
        new_category = "expense" if category == "income" else "income"

        self.transaction_repository.update_category(record_id, user_id, new_category)
        return True

    def update_amount(self, record_id: int, user_id: int, amount: int):
        """Обновление суммы"""
        self.transaction_repository.update_amount(record_id, user_id, amount)

    def delete_record(self, record_id: int, user_id: int):
        """Удаление записи"""
        self.transaction_repository.delete_record(record_id, user_id)