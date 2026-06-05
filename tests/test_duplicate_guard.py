def test_is_recent_duplicate_returns_true_for_same_operation(
    transaction_repository,
    duplicate_guard,
):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert duplicate_guard.is_recent_duplicate(
        user_id=1,
        category="expense",
        amount=500,
    ) is True


def test_is_recent_duplicate_returns_false_for_different_amount(
    transaction_repository,
    duplicate_guard,
):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert duplicate_guard.is_recent_duplicate(
        user_id=1,
        category="expense",
        amount=1000,
    ) is False


def test_is_recent_duplicate_returns_false_for_different_user(
    transaction_repository,
    duplicate_guard,
):
    transaction_repository.add_record(
        user_id=1,
        category="expense",
        amount=500,
        comment="coffee",
        telegram_message_id=100,
    )

    assert duplicate_guard.is_recent_duplicate(
        user_id=2,
        category="expense",
        amount=500,
    ) is False