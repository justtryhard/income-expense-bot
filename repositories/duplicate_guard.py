from database.connection import SQLiteConnection


class DuplicateGuard:
    """
    Класс отвечает за защиту от дублирования операций
    Проверяет одинаковые операции, защищает от сетевых лагов и дабл кликов
    """
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection

    def is_recent_duplicate(
        self,
        user_id: int,
        category: str,
        amount: int,
        seconds: int = 300   # значение в сек, по которому фильтруется поиск дубликатов
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