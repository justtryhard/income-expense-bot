from database.connection import SQLiteConnection


class StatsRepository:
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

    def get_stats_for_period(self, user_id: int, start_date, end_date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
            SELECT 
                SUM(CASE WHEN category='income' THEN amount ELSE 0 END),
                COUNT(CASE WHEN category='income' THEN 1 END),
                SUM(CASE WHEN category='expense' THEN amount ELSE 0 END),
                COUNT(CASE WHEN category='expense' THEN 1 END)
            FROM history
            WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
            """, (user_id, start_date, end_date))

            row = cursor.fetchone()

            return {
                "income_sum": row[0] or 0,
                "income_count": row[1] or 0,
                "expense_sum": row[2] or 0,
                "expense_count": row[3] or 0,
            }

    def get_daily_stats(self, user_id: int, start_date, end_date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    date(created_at),
                    SUM(CASE WHEN category='income' THEN amount ELSE 0 END),
                    SUM(CASE WHEN category='expense' THEN amount ELSE 0 END)
                FROM history
                WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
                GROUP BY date(created_at)
                ORDER BY date(created_at)
            """, (user_id, start_date, end_date))

            rows = cursor.fetchall()

        return [(row[0], row[1] or 0, row[2] or 0) for row in rows]