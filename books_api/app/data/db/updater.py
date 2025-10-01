from app.core import config
if config.DB_TYPE == "sqlite":
    from .sqlite import get_connection
elif config.DB_TYPE == "postgres":
    from .postgres import get_connection
else:
    raise ValueError("DB_TYPE doit être 'sqlite' ou 'postgres'")

def update_books(new_books: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    if config.DB_TYPE == "sqlite":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                category TEXT,
                price REAL,
                stock INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author)
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                price NUMERIC,
                stock INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author)
            )
        """)

    for book in new_books:
        if config.DB_TYPE == "sqlite":
            cur.execute("""
                INSERT INTO books (title, author, category, price, stock)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(title, author) DO UPDATE SET
                    category=excluded.category,
                    price=excluded.price,
                    stock=excluded.stock
            """, (book['title'], book['author'], book.get('category'), book['price'], book.get('stock', 0)))
        else:
            cur.execute("""
                INSERT INTO books (title, author, category, price, stock)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (title, author) DO UPDATE SET
                    category=EXCLUDED.category,
                    price=EXCLUDED.price,
                    stock=EXCLUDED.stock
            """, (book['title'], book['author'], book.get('category'), book['price'], book.get('stock', 0)))

    conn.commit()
    conn.close()
