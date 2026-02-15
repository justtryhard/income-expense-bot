import sqlite3
from contextlib import contextmanager
from config import DB_NAME


class SQLiteConnection:
    def __init__(self, db_name: str):
        self.db_name = db_name

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


class HistoryRepository:
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

    def create_table(self):
        with self.connection.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def add_record(self, user_id: int, category: str, amount: int, comment: str):
        with self.connection.get_connection() as conn:
            conn.execute("""
            INSERT INTO history (user_id, category, amount, comment)
            VALUES (?, ?, ?, ?)
            """, (user_id, category, amount, comment))


    def get_stats_for_period(self, user_id: int, start_date, end_date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
            SELECT 
                SUM(CASE WHEN category='income' THEN amount ELSE 0 END) as total_income,
                COUNT(CASE WHEN category='income' THEN 1 END) as count_income,
                SUM(CASE WHEN category='expense' THEN amount ELSE 0 END) as total_expense,
                COUNT(CASE WHEN category='expense' THEN 1 END) as count_expense
            FROM history
            WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
            """, (user_id, start_date, end_date))

            row = cursor.fetchone()
            return {
                'income_sum': row[0] or 0,
                'income_count': row[1] or 0,
                'expense_sum': row[2] or 0,
                'expense_count': row[3] or 0
            }

    def get_daily_stats(self, user_id, start_date, end_date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    date(created_at) as day,
                    SUM(CASE WHEN category='income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN category='expense' THEN amount ELSE 0 END) as expense
                FROM history
                WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
                GROUP BY date(created_at)
                ORDER BY day
            """, (user_id, start_date, end_date))
            rows = cursor.fetchall()
        return [(row[0], row[1] or 0, row[2] or 0) for row in rows]

    # def get_stats_for_period(self, user_id: int, start_date, end_date):
    #     with self.connection.get_connection() as conn:
    #         cursor = conn.execute("""
    #         SELECT
    #             COALESCE(SUM(CASE WHEN category='income' THEN amount END), 0),
    #             COALESCE(SUM(CASE WHEN category='expense' THEN amount END), 0)
    #         FROM history
    #         WHERE user_id = ?
    #         AND date(created_at) BETWEEN ? AND ?
    #         """, (user_id, start_date, end_date))
    #
    #         return cursor.fetchone()