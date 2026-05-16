from database.connection import SQLiteConnection
from utils.time_utils import get_moscow_now_str


class TransactionRepository:
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
            created_at = get_moscow_now_str()

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