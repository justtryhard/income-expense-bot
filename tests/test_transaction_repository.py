def test_add_record_saves_transaction(transaction_repository):
    result = transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    records = transaction_repository.get_records_by_date(
        user_id=1,
        date="2026-06-05",
    )

    assert result is True
    assert len(records) == 1
    assert records[0][1] == "expense"
    assert records[0][2] == 500


def test_add_record_ignores_duplicate_telegram_message_id(transaction_repository):
    first_result = transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    second_result = transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=700,
        comment="lunch",
        telegram_message_id=100,
        created_at="2026-06-05 11:00:00",
    )

    records = transaction_repository.get_records_by_date(
        user_id=1,
        date="2026-06-05",
    )

    assert first_result is True
    assert second_result is False
    assert len(records) == 1
    assert records[0][2] == 500


def test_get_record_by_id_returns_only_owner_record(transaction_repository):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    record = transaction_repository.get_record_by_id(
        record_id=1,
        user_id=1,
    )

    other_user_record = transaction_repository.get_record_by_id(
        record_id=1,
        user_id=2,
    )

    assert record is not None
    assert record[0] == 1
    assert record[1] == "expense"
    assert record[2] == 500
    assert other_user_record is None


def test_update_amount_changes_only_owner_record(transaction_repository):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    transaction_repository.update_amount(
        record_id=1,
        user_id=1,
        new_amount=900,
    )

    record = transaction_repository.get_record_by_id(
        record_id=1,
        user_id=1,
    )

    assert record[2] == 900


def test_update_category_changes_only_owner_record(transaction_repository):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    transaction_repository.update_category(
        record_id=1,
        user_id=1,
        new_category="income",
    )

    record = transaction_repository.get_record_by_id(
        record_id=1,
        user_id=1,
    )

    assert record[1] == "income"


def test_delete_record_removes_only_owner_record(transaction_repository):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
        created_at="2026-06-05 10:00:00",
    )

    transaction_repository.delete_record(
        record_id=1,
        user_id=1,
    )

    record = transaction_repository.get_record_by_id(
        record_id=1,
        user_id=1,
    )

    assert record is None