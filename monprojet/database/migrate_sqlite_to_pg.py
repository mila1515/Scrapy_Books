import sqlite3
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import os

# Charger les variables depuis le fichier .env
load_dotenv()

# 1️⃣ Connexion SQLite
sqlite_path = os.getenv("SQLITE_PATH")
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cur = sqlite_conn.cursor()

# 2️⃣ Connexion PostgreSQL
pg_conn = psycopg2.connect(
    dbname=os.getenv("PG_DB"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT")
)
pg_cur = pg_conn.cursor()

# 3️⃣ Créer la table si elle n'existe pas
pg_cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT,
    price NUMERIC,
    rating INTEGER,
    category TEXT,
    stock INTEGER,
    url TEXT,
    UNIQUE(title, url)
);
""")

pg_conn.commit()

# 4️⃣ Lire les données SQLite
sqlite_cur.execute("SELECT title, price, rating, category, stock, url FROM books")
rows = sqlite_cur.fetchall()

# 5️⃣ Insérer dans PostgreSQL
insert_query = """
INSERT INTO books (title, price, rating, category, stock, url)
VALUES %s
ON CONFLICT (title, url) DO NOTHING;
"""

execute_values(pg_cur, insert_query, rows)
pg_conn.commit()


print(f"Migration terminée ✅ {len(rows)} livres transférés")

# 6️⃣ Fermer les connexions
sqlite_cur.close()
sqlite_conn.close()
pg_cur.close()
pg_conn.close()

