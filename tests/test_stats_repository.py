from repositories.stats_repository import StatsRepository


def test_get_stats_for_period_returns_income_and_expense_totals(
    test_db,
    transaction_repository,
):
    stats_repository = StatsRepository(test_db)

    transaction_repository.add_record(
        user_id=1,
        category="income",
        amount=1000,
        comment="salary",
        telegram_message_id=1,
        created_at="2026-06-05 10:00:00",
    )
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=300,
        comment="food",
        telegram_message_id=2,
        created_at="2026-06-05 11:00:00",
    )
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=200,
        comment="coffee",
        telegram_message_id=3,
        created_at="2026-06-06 11:00:00",
    )

    result = stats_repository.get_stats_for_period(
        user_id=1,
        start_date="2026-06-05",
        end_date="2026-06-06",
    )

    assert result == {
        "income_sum": 1000,
        "income_count": 1,
        "expense_sum": 500,
        "expense_count": 2,
    }


def test_get_stats_for_period_returns_zeroes_without_records(test_db):
    stats_repository = StatsRepository(test_db)

    result = stats_repository.get_stats_for_period(
        user_id=1,
        start_date="2026-06-05",
        end_date="2026-06-06",
    )

    assert result == {
        "income_sum": 0,
        "income_count": 0,
        "expense_sum": 0,
        "expense_count": 0,
    }


def test_get_daily_stats_groups_records_by_day(test_db, transaction_repository):
    stats_repository = StatsRepository(test_db)

    transaction_repository.add_record(
        user_id=1,
        category="income",
        amount=1000,
        comment="salary",
        telegram_message_id=1,
        created_at="2026-06-05 10:00:00",
    )
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=300,
        comment="food",
        telegram_message_id=2,
        created_at="2026-06-05 11:00:00",
    )
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=200,
        comment="coffee",
        telegram_message_id=3,
        created_at="2026-06-06 11:00:00",
    )

    result = stats_repository.get_daily_stats(
        user_id=1,
        start_date="2026-06-05",
        end_date="2026-06-06",
    )

    assert result == [
        ("2026-06-05", 1000, 300),
        ("2026-06-06", 0, 200),
    ]