from services.transaction_service import TransactionService


class FakeDuplicateGuard:
    def __init__(self, is_duplicate=False):
        self.is_duplicate = is_duplicate

    def is_recent_duplicate(self, user_id, category, amount):
        return self.is_duplicate


class FakeTransactionRepository:
    def __init__(self, inserted=True):
        self.inserted = inserted
        self.saved_record = None

    def add_record(self, user_id, category, amount, comment, telegram_message_id):
        self.saved_record = {
            "user_id": user_id,
            "category": category,
            "amount": amount,
            "comment": comment,
            "telegram_message_id": telegram_message_id,
        }
        return self.inserted


def test_add_transaction_success():
    service = TransactionService(
        transaction_repository=FakeTransactionRepository(inserted=True),
        duplicate_guard=FakeDuplicateGuard(is_duplicate=False),
    )

    result = service.add_transaction(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert result["success"] is True


def test_add_transaction_rejects_duplicate():
    service = TransactionService(
        transaction_repository=FakeTransactionRepository(),
        duplicate_guard=FakeDuplicateGuard(is_duplicate=True),
    )

    result = service.add_transaction(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert result["success"] is False
    assert "Одинаковый тип и сумма" in result["reason"]

def test_add_transaction_returns_error_when_repository_fails():
    service = TransactionService(
        transaction_repository=FakeTransactionRepository(inserted=False),
        duplicate_guard=FakeDuplicateGuard(is_duplicate=False),
    )

    result = service.add_transaction(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert result["success"] is False
    assert result["reason"] == "Дубликат сообщения"