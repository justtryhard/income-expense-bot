import pytest

from database.connection import SQLiteConnection
from database.schema import HistorySchema
from repositories.duplicate_guard import DuplicateGuard
from repositories.transaction_repository import TransactionRepository


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test.db"
    connection = SQLiteConnection(str(db_path))
    HistorySchema(connection).create_table()
    return connection


@pytest.fixture
def transaction_repository(test_db):
    return TransactionRepository(test_db)


@pytest.fixture
def duplicate_guard(test_db):
    return DuplicateGuard(test_db)