from contextlib import contextmanager
from typing import List, Optional, Any, Dict, Union, Tuple

from app.data.db.sqlite import get_connection, DatabaseError
from app.domain.models.book import Book
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
            params: Les paramètres à lier à la requête.
            fetch_all: Si True, retourne tous les résultats, sinon un seul.
            
        Returns:
            Les résultats de la requête sous forme de liste de dictionnaires ou d'un seul dictionnaire.
            
        Raises:
            DatabaseError: Si une erreur survient lors de l'exécution de la requête.
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch_all:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    row = cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            raise DatabaseError(f"Erreur d'exécution de requête: {e}") from e

    def get_all_books(self) -> List[Book]:
        """
        Récupère tous les livres de la base de données.
        
        Returns:
            List[Book]: Une liste de tous les livres.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération des livres.
        """
        query = """
            SELECT 
                id, 
                title, 
                category, 
                price, 
                stock, 
                created_at,
                rating,
                url
            FROM books
            ORDER BY title
        """
        try:
            results = self._execute_query(query)
            return [Book(**book_data) for book_data in results]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de tous les livres: {e}")
            raise DatabaseError(f"Impossible de récupérer les livres: {e}") from e

    def get_book(self, book_id: int) -> Optional[Book]:
        """
        Récupère un livre par son ID.
        
        Args:
            book_id: L'identifiant du livre à récupérer.
            
        Returns:
            Optional[Book]: Le livre correspondant à l'ID, ou None si non trouvé.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération du livre.
        """
        query = """
            SELECT 
                id, 
                title, 
                category, 
                price, 
                stock, 
                created_at,
                rating,
                url
            FROM books 
            WHERE id = :book_id
            LIMIT 1
        """
        try:
            result = self._execute_query(
                query, 
                params={"book_id": book_id},
                fetch_all=False
            )
            return Book(**result) if result else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du livre {book_id}: {e}")
            raise DatabaseError(f"Impossible de récupérer le livre: {e}") from e
        
    def search_books_by_title(self, title: str) -> List[Book]:
        """
        Recherche des livres par titre (insensible à la casse).
        
        Args:
            title: Le terme de recherche pour le titre.
            
        Returns:
            List[Book]: Une liste de livres correspondant au critère de recherche.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        query = """
            SELECT 
                id, 
                title, 
                category, 
                price, 
                stock, 
                created_at,
                rating,
                url
            FROM books 
            WHERE LOWER(title) LIKE LOWER(:search_term)
            ORDER BY title
        """
        try:
            results = self._execute_query(
                query, 
                params={"search_term": f"%{title}%"}
            )
            return [Book(**book_data) for book_data in results]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par titre '{title}': {e}")
            raise DatabaseError(f"Recherche par titre échouée: {e}") from e
        
    def search_books_by_category(self, category: str) -> List[Book]:
        """
        Recherche des livres par catégorie (insensible à la casse).
        
        Args:
            category: La catégorie de livres à rechercher.
            
        Returns:
            List[Book]: Une liste de livres de la catégorie spécifiée.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche par catégorie.
        """
        query = """
            SELECT 
                id, 
                title, 
                category, 
                price, 
                stock, 
                created_at,
                rating,
                url
            FROM books 
            WHERE LOWER(category) = LOWER(:category)
            ORDER BY title
        """
        try:
            results = self._execute_query(
                query, 
                params={"category": category}
            )
            return [Book(**book_data) for book_data in results]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par catégorie '{category}': {e}")
            raise DatabaseError(f"Recherche par catégorie échouée: {e}") from e
