from app.core import config 
if config.DB_TYPE == "sqlite":
    from app.data.db.sqlite import get_connection
else:
    from app.data.db.postgres import get_connection
from typing import List
from app.domain.models import Book

class BookRepository:
    def __init__(self):
        self.conn = get_connection()

    def get_all_books(self) -> List[Book]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                id, 
                title, 
                NULL as author,  -- Champ non disponible dans la table
                category, 
                price, 
                stock, 
                created_at,
                rating,
                url
            FROM books
        """)
        rows = cur.fetchall()
        return [Book(**dict(row)) for row in rows]

    def get_book(self, book_id: int) -> Book:
        cur = self.conn.cursor()
        if config.DB_TYPE == "sqlite":
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE id=?
            """, (book_id,))
        else:
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE id=%s
            """, (book_id,))
        row = cur.fetchone()
        return Book(**dict(row)) if row else None
        
    def search_books_by_title(self, title: str) -> List[Book]:
        cur = self.conn.cursor()
        if config.DB_TYPE == "sqlite":
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE LOWER(title) LIKE LOWER(?)
            """, (f"%{title}%",))
        else:
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE LOWER(title) LIKE LOWER(%s)
            """, (f"%{title}%",))
        rows = cur.fetchall()
        return [Book(**dict(row)) for row in rows]
        
    def search_books_by_category(self, category: str) -> List[Book]:
        cur = self.conn.cursor()
        if config.DB_TYPE == "sqlite":
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE LOWER(category) = LOWER(?)
            """, (category,))
        else:
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    NULL as author,  -- Champ non disponible dans la table
                    category, 
                    price, 
                    stock, 
                    created_at,
                    rating,
                    url
                FROM books 
                WHERE LOWER(category) = LOWER(%s)
            """, (category,))
        rows = cur.fetchall()
        return [Book(**dict(row)) for row in rows]
