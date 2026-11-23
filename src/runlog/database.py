import os
import sqlite3


def get_connection():
    path = os.getenv("DATABASE_PATH", "runlog.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn