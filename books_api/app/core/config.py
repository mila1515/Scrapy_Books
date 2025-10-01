import os
from dotenv import load_dotenv

# Chemin vers la base de données SQLite existante
DB_TYPE = "sqlite"
SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "monprojet", "books.db"))

# PostgreSQL
DB_NAME = os.getenv("PG_DB", "books_db")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASSWORD = os.getenv("PG_PASSWORD", "Youcef17")
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = int(os.getenv("PG_PORT", 5432))
