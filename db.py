import sqlite3
from contextlib import contextmanager
from config import DB_NAME
from zoneinfo import ZoneInfo
from datetime import datetime


class SQLiteConnection:
    """
    Подключение к БД
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


class HistoryRepository:
    """
    Работа с БД
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def add_record(self, user_id: int, category: str, amount: int, comment: str, created_at: str = None):
        if created_at is None:
            # Текущее московское время в формате SQLite
            msk_tz = ZoneInfo("Europe/Moscow")
            created_at = datetime.now(msk_tz).strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.get_connection() as conn:
            conn.execute("""
                INSERT INTO history (user_id, category, amount, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, category, amount, comment, created_at))

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

    def get_records_by_date(self, user_id, date):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, category, amount
                FROM history
                WHERE user_id = ? AND date(created_at) = ?
                ORDER BY id
            """, (user_id, date))
            return cursor.fetchall()

    def get_record_by_id(self, record_id, user_id):
        with self.connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, category, amount
                FROM history
                WHERE id = ? AND user_id = ?
            """, (record_id, user_id))
            return cursor.fetchone()

    def update_amount(self, record_id, user_id, new_amount):
        with self.connection.get_connection() as conn:
            conn.execute("""
                UPDATE history
                SET amount = ?
                WHERE id = ? AND user_id = ?
            """, (new_amount, record_id, user_id))

    def update_category(self, record_id, user_id, new_category):
        with self.connection.get_connection() as conn:
            conn.execute("""
                UPDATE history
                SET category = ?
                WHERE id = ? AND user_id = ?
            """, (new_category, record_id, user_id))

    def delete_record(self, record_id, user_id):
        with self.connection.get_connection() as conn:
            conn.execute("""
                DELETE FROM history
                WHERE id = ? AND user_id = ?
            """, (record_id, user_id))