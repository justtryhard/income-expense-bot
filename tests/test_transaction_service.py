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
        self.record = None
        self.updated_category = None
        self.updated_amount = None
        self.deleted_record = None

    def get_record_by_id(self, record_id, user_id):
        return self.record

    def update_category(self, record_id, user_id, new_category):
        self.updated_category = {
            "record_id": record_id,
            "user_id": user_id,
            "new_category": new_category,
        }

    def update_amount(self, record_id, user_id, amount):
        self.updated_amount = {
            "record_id": record_id,
            "user_id": user_id,
            "amount": amount,
        }

    def delete_record(self, record_id, user_id):
        self.deleted_record = {
            "record_id": record_id,
            "user_id": user_id,
        }

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


def test_get_record_by_id_returns_repository_result():
    repository = FakeTransactionRepository()
    repository.record = (1, "expense", 500)

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    assert service.get_record_by_id(record_id=1, user_id=1) == (1, "expense", 500)


def test_switch_category_returns_false_when_record_not_found():
    repository = FakeTransactionRepository()
    repository.record = None

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    assert service.switch_category(record_id=1, user_id=1) is False


def test_switch_category_changes_income_to_expense():
    repository = FakeTransactionRepository()
    repository.record = (1, "income", 1000)

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    result = service.switch_category(record_id=1, user_id=1)

    assert result is True
    assert repository.updated_category == {
        "record_id": 1,
        "user_id": 1,
        "new_category": "expense",
    }


def test_switch_category_changes_expense_to_income():
    repository = FakeTransactionRepository()
    repository.record = (1, "expense", 500)

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    result = service.switch_category(record_id=1, user_id=1)

    assert result is True
    assert repository.updated_category == {
        "record_id": 1,
        "user_id": 1,
        "new_category": "income",
    }


def test_update_amount_calls_repository():
    repository = FakeTransactionRepository()

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    service.update_amount(record_id=1, user_id=1, amount=900)

    assert repository.updated_amount == {
        "record_id": 1,
        "user_id": 1,
        "amount": 900,
    }


def test_delete_record_calls_repository():
    repository = FakeTransactionRepository()

    service = TransactionService(
        transaction_repository=repository,
        duplicate_guard=FakeDuplicateGuard(),
    )

    service.delete_record(record_id=1, user_id=1)

    assert repository.deleted_record == {
        "record_id": 1,
        "user_id": 1,
    }