import sqlite3
from app.core.config import SQLITE_PATH

def get_connection():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
