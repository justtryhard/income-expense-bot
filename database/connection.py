import sqlite3
from contextlib import contextmanager


class SQLiteConnection:
    """Класс подключения к БД
    Отвечает за создание подключения, коммит и закрытие"""
    def __init__(self, db_name: str):
        self.db_name = db_name

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
            conn.commit()
        finally:
            # соединение закрывается, даже если произошла ошибка
            conn.close()