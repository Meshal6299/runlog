import os
import sqlite3
from pathlib import Path


def get_connection():
    path = os.getenv("DATABASE_PATH", "runlog.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = Path(__file__).with_name("schema.sql")      # the file next to database.py

def init_db():
    conn = get_connection()
    try:
        conn.executescript(SCHEMA.read_text())
        conn.commit()
    finally:
        conn.close()