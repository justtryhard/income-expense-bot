import sqlite3
from contextlib import contextmanager
from zoneinfo import ZoneInfo
from datetime import datetime


class SQLiteConnection:
    """
    Подключение к SQLite
    """
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


class HistorySchema:
    """
    Структура БД
    """
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
                created_at TIMESTAMP NOT NULL,
                telegram_message_id INTEGER NOT NULL,
                UNIQUE(user_id, telegram_message_id)
            );
            """)


class TransactionRepository:
    """
    CRUD
    """
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

    def add_record(
        self,
        user_id: int,
        category: str,
        amount: int,
        comment: str,
        telegram_message_id: int,
        created_at: str | None = None
    ) -> bool:
        if created_at is None:
            created_at = self._get_moscow_now()

        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO history (
                    user_id, category, amount, comment, created_at, telegram_message_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, category, amount, comment, created_at, telegram_message_id))

            return cursor.rowcount > 0

    def get_records_by_date(self, user_id: int, date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, category, amount
                FROM history
                WHERE user_id = ? AND date(created_at) = ?
                ORDER BY id
            """, (user_id, date))
            return cursor.fetchall()

    def get_record_by_id(self, record_id: int, user_id: int):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, category, amount
                FROM history
                WHERE id = ? AND user_id = ?
            """, (record_id, user_id))
            return cursor.fetchone()

    def update_amount(self, record_id: int, user_id: int, new_amount: int):
        with self.connection.get_connection() as conn:
            conn.execute("""
                UPDATE history
                SET amount = ?
                WHERE id = ? AND user_id = ?
            """, (new_amount, record_id, user_id))

    def update_category(self, record_id: int, user_id: int, new_category: str):
        with self.connection.get_connection() as conn:
            conn.execute("""
                UPDATE history
                SET category = ?
                WHERE id = ? AND user_id = ?
            """, (new_category, record_id, user_id))

    def delete_record(self, record_id: int, user_id: int):
        with self.connection.get_connection() as conn:
            conn.execute("""
                DELETE FROM history
                WHERE id = ? AND user_id = ?
            """, (record_id, user_id))

    @staticmethod
    def _get_moscow_now() -> str:
        msk_tz = ZoneInfo("Europe/Moscow")
        return datetime.now(msk_tz).strftime("%Y-%m-%d %H:%M:%S")


class StatsRepository:
    """
    Статистика
    """
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

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
                "income_sum": row[0] or 0,
                "income_count": row[1] or 0,
                "expense_sum": row[2] or 0,
                "expense_count": row[3] or 0
            }

    def get_daily_stats(self, user_id: int, start_date, end_date):
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


class DuplicateGuard:
    """
    Отвечает только за защиту от дублей.
    """
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

    def is_recent_duplicate(
        self,
        user_id: int,
        category: str,
        amount: int,
        seconds: int = 300
    ) -> bool:
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id
                FROM history
                WHERE user_id = ?
                  AND category = ?
                  AND amount = ?
                  AND datetime(created_at) >= datetime('now', 'localtime', ?)
                LIMIT 1
            """, (user_id, category, amount, f"-{seconds} seconds"))

            return cursor.fetchone() is not None