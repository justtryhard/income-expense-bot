from database.connection import SQLiteConnection
from database.schema import HistorySchema
from repositories.duplicate_guard import DuplicateGuard
from repositories.transaction_repository import TransactionRepository


def test_is_recent_duplicate_returns_true_for_same_operation(tmp_path):
    db_path = tmp_path / "test.db"

    connection = SQLiteConnection(str(db_path))
    HistorySchema(connection).create_table()

    repository = TransactionRepository(connection)
    guard = DuplicateGuard(connection)

    repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert guard.is_recent_duplicate(
        user_id=1,
        category="expense",
        amount=500,
    ) is True


def test_is_recent_duplicate_returns_false_for_different_amount(tmp_path):
    db_path = tmp_path / "test.db"

    connection = SQLiteConnection(str(db_path))
    HistorySchema(connection).create_table()

    repository = TransactionRepository(connection)
    guard = DuplicateGuard(connection)

    repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert guard.is_recent_duplicate(
        user_id=1,
        category="expense",
        amount=1000,
    ) is False


def test_is_recent_duplicate_returns_false_for_different_user(tmp_path):
    db_path = tmp_path / "test.db"

    connection = SQLiteConnection(str(db_path))
    HistorySchema(connection).create_table()

    repository = TransactionRepository(connection)
    guard = DuplicateGuard(connection)

    repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert guard.is_recent_duplicate(
        user_id=2,
        category="expense",
        amount=500,
    ) is False
