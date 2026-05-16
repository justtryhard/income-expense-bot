class StatsService:
    def __init__(self, stats_repository, transaction_repository):
        self.stats_repository = stats_repository
        self.transaction_repository = transaction_repository

    def get_period_stats(self, user_id: int, start_date, end_date):
        return self.stats_repository.get_stats_for_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_daily_stats(self, user_id: int, start_date, end_date):
        return self.stats_repository.get_daily_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_records_for_day(self, user_id: int, date):
        return self.transaction_repository.get_records_by_date(user_id, date)