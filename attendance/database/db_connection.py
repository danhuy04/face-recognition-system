import sqlite3
import os

class DBConnection:
    _instance = None

    def __new__(cls, db_path="database/attendance.db"):
        if cls._instance is None:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cls._instance = conn
        return cls._instance
