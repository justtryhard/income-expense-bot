from database.connection import SQLiteConnection


class HistorySchema:
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