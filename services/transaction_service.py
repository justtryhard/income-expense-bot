class TransactionService:
    def __init__(self, transaction_repository, duplicate_guard):
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
        if self.duplicate_guard.is_recent_duplicate(
            user_id=user_id,
            category=category,
            amount=amount
        ):
            return {
                "success": False,
                "reason": "recent_duplicate"
            }

        inserted = self.transaction_repository.add_record(
            user_id=user_id,
            category=category,
            amount=amount,
            comment=comment,
            telegram_message_id=telegram_message_id
        )

        if not inserted:
            return {
                "success": False,
                "reason": "message_duplicate"
            }

        return {
            "success": True,
            "reason": None
        }

    def get_record_by_id(self, record_id: int, user_id: int):
        return self.transaction_repository.get_record_by_id(record_id, user_id)

    def switch_category(self, record_id: int, user_id: int):
        record = self.transaction_repository.get_record_by_id(record_id, user_id)

        if not record:
            return False

        _, category, _ = record
        new_category = "expense" if category == "income" else "income"

        self.transaction_repository.update_category(record_id, user_id, new_category)
        return True

    def update_amount(self, record_id: int, user_id: int, amount: int):
        self.transaction_repository.update_amount(record_id, user_id, amount)

    def delete_record(self, record_id: int, user_id: int):
        self.transaction_repository.delete_record(record_id, user_id)