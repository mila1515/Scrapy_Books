from contextlib import contextmanager
from typing import List, Optional, Any, Dict, Union, Tuple

from books_api.data.sqlite import get_connection, DatabaseError
from books_api.domain.book import Book
import logging

logger = logging.getLogger(__name__)

class BookRepository:
    """
    Repository pour gérer les opérations CRUD sur les livres dans la base de données.
    Utilise un gestionnaire de contexte pour la gestion des connexions.
    """
    
    def __init__(self):
        """Initialise le repository sans établir immédiatement de connexion."""
        pass
        
    @contextmanager
    def _get_cursor(self) -> Any:
        """
        Gestionnaire de contexte pour obtenir un curseur de base de données.
        
        Yields:
            sqlite3.Cursor: Un curseur de base de données configuré.
            
        Raises:
            DatabaseError: Si une erreur survient lors de l'obtention du curseur.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                yield cursor
                # La connexion est automatiquement fermée par le gestionnaire de contexte
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention du curseur: {e}")
            raise DatabaseError(f"Erreur d'accès à la base de données: {e}") from e
    
    def _execute_query(
        self, 
        query: str, 
        params: Union[tuple, Dict[str, Any], None] = None,
        fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Exécute une requête SQL et retourne les résultats.
        
        Args:
            query: La requête SQL à exécuter.
            params: Paramètres pour la requête (optionnel).
            fetch_all: Si True, retourne tous les résultats, sinon un seul.
            
        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any], None]: 
                Les résultats de la requête, ou None si aucun résultat.
                
        Raises:
            DatabaseError: Si une erreur survient lors de l'exécution de la requête.
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    columns = [col[0] for col in cursor.description]
                    if fetch_all:
                        results = cursor.fetchall()
                        return [dict(zip(columns, row)) for row in results]
                    else:
                        result = cursor.fetchone()
                        return dict(zip(columns, result)) if result else None
                else:
                    cursor.connection.commit()
                    return None
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            raise DatabaseError(f"Erreur lors de l'exécution de la requête: {e}") from e
    
    def create_tables(self) -> None:
        """Crée les tables nécessaires si elles n'existent pas."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            rating REAL,
            url TEXT,
            UNIQUE(title)
        )
        """
        self._execute_query(create_table_query, fetch_all=False)
        logger.info("Tables vérifiées/créées avec succès")
    
    def add_book(self, book: Book) -> Book:
        """
        Ajoute un nouveau livre à la base de données.
        
        Args:
            book: L'objet Book à ajouter.
            
        Returns:
            Book: Le livre ajouté avec son ID.
            
        Raises:
            DatabaseError: Si une erreur survient lors de l'ajout.
        """
        query = """
        INSERT INTO books (title, category, price, stock, created_at, rating, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            book.title, 
            book.category, 
            book.price, 
            book.stock, 
            book.created_at,
            book.rating,
            book.url
        )
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, params)
                book.id = cursor.lastrowid
                cursor.connection.commit()
                logger.info("Livre ajouté avec l'ID: %s", book.id)
                return book
        except Exception as e:
            logger.error("Erreur lors de l'ajout du livre: %s", str(e))
            raise DatabaseError(f"Impossible d'ajouter le livre: {e}") from e
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Récupère un livre par son ID.
        
        Args:
            book_id: L'ID du livre à récupérer.
            
        Returns:
            Optional[Book]: Le livre trouvé, ou None si non trouvé.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération.
        """
        query = """
        SELECT id, title, category, price, stock, created_at, rating, url
        FROM books
        WHERE id = ?
        """
        
        try:
            result = self._execute_query(query, (book_id,), fetch_all=False)
            if not result:
                return None
                
            # Convertir le dictionnaire en objet Book
            return Book(**result)
            
        except Exception as e:
            logger.error("Erreur lors de la récupération du livre ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de récupérer le livre avec l'ID {book_id}: {e}") from e
    
    def get_all_books(self) -> List[Book]:
        """
        Récupère tous les livres de la base de données.
        
        Returns:
            List[Book]: Une liste de tous les livres.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération.
        """
        query = """
        SELECT id, title, category, price, stock, created_at, rating, url
        FROM books
        ORDER BY title
        """
        
        try:
            results = self._execute_query(query)
            return [Book(**row) for row in results] if results else []
            
        except Exception as e:
            logger.error("Erreur lors de la récupération de tous les livres: %s", str(e))
            raise DatabaseError(f"Impossible de récupérer les livres: {e}") from e
    
    def update_book(self, book: Book) -> Optional[Book]:
        """
        Met à jour un livre existant.
        
        Args:
            book: L'objet Book avec les données mises à jour.
            
        Returns:
            Optional[Book]: Le livre mis à jour, ou None si non trouvé.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la mise à jour.
        """
        query = """
        UPDATE books
        SET title = ?, category = ?, price = ?, stock = ?, 
            created_at = ?, rating = ?, url = ?
        WHERE id = ?
        """
        params = (
            book.title, book.category, book.price, book.stock,
            book.created_at, book.rating, book.url, book.id
        )
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, params)
                if cursor.rowcount == 0:
                    return None
                cursor.connection.commit()
                return book
                
        except Exception as e:
            logger.error("Erreur lors de la mise à jour du livre ID %s: %s", book.id, str(e))
            raise DatabaseError(f"Impossible de mettre à jour le livre avec l'ID {book.id}: {e}") from e
    
    def delete_book(self, book_id: int) -> bool:
        """
        Supprime un livre par son ID.
        
        Args:
            book_id: L'ID du livre à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False si le livre n'existe pas.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la suppression.
        """
        query = "DELETE FROM books WHERE id = ?"
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, (book_id,))
                cursor.connection.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error("Erreur lors de la suppression du livre ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de supprimer le livre avec l'ID {book_id}: {e}") from e
    
    def search_books(self, query: str) -> List[Book]:
        """
        Recherche des livres par titre ou catégorie.
        
        Args:
            query: La chaîne de recherche.
            
        Returns:
            List[Book]: Une liste de livres correspondant à la recherche.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        search_query = """
        SELECT id, title, category, price, stock, created_at, rating, url
        FROM books
        WHERE title LIKE ? OR category LIKE ?
        ORDER BY title
        """
        search_param = f"%{query}%"
        
        try:
            results = self._execute_query(
                search_query, 
                (search_param, search_param)
            )
            return [Book(**row) for row in results] if results else []
            
        except Exception as e:
            logger.error("Erreur lors de la recherche de livres avec la requête '%s': %s", 
                        query, str(e))
            raise DatabaseError(
                f"Erreur lors de la recherche de livres avec la requête '{query}': {e}"
            ) from e
