import sqlite3
from contextlib import contextmanager


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