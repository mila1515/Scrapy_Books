from contextlib import contextmanager
from typing import List, Optional, Any, Dict, Union, Tuple
import sqlite3
import logging
import os

from books_api.data.sqlite import get_connection, DatabaseError
from books_api.domain.book import Book

logger = logging.getLogger(__name__)

class BookRepository:
    """
    Repository pour gérer les opérations CRUD sur les livres dans la base de données.
    Utilise un gestionnaire de contexte pour la gestion des connexions.
    """
    
    def __init__(self):
        """Initialise le repository."""
        from books_api.data.config import BASE_DIR
        # Utiliser le chemin absolu vers la base de données
        db_path = os.path.join(BASE_DIR, 'monprojet', 'books.db')
        self.db_path = os.path.abspath(db_path).replace('\\', '/')
        # Forcer l'utilisation de SQLite avec le chemin absolu
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        logger.info(f"Initialisation du BookRepository avec la base de données: {self.db_path}")
        logger.info(f"URL de la base de données: {os.environ.get('DATABASE_URL')}")
        
    def _row_to_book(self, row: Dict[str, Any]) -> 'Book':
        """
        Convertit une ligne de la base de données en objet Book.
        
        Args:
            row: Dictionnaire contenant les données d'un livre.
            
        Returns:
            Book: Un objet Book initialisé avec les données de la ligne.
        """
        from books_api.domain.book import Book
        
        # Extraire les tags si présents dans la ligne
        tags = []
        if 'tags' in row and row['tags']:
            tags = row['tags'].split(',') if isinstance(row['tags'], str) else row['tags']
        
        # Créer et retourner un objet Book
        return Book(
            id=row.get('id'),
            title=row.get('title', ''),
            price=row.get('price', 0.0),
            rating=row.get('rating'),
            category=row.get('category'),
            stock=row.get('stock', 0),
            url=row.get('url', ''),
            created_at=row.get('created_at'),
            tags=tags
        )
        
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
            with self._get_cursor() as cursor:
                cursor.execute(query, (book_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Convertir la ligne en dictionnaire
                columns = [column[0] for column in cursor.description]
                row_dict = dict(zip(columns, row))
                
                # Récupérer les tags pour ce livre
                cursor.execute("""
                    SELECT tag FROM book_tags WHERE book_id = ?
                """, (book_id,))
                tags = [tag[0] for tag in cursor.fetchall()]
                row_dict['tags'] = tags
                
                # Créer et retourner l'objet Book
                return self._row_to_book(row_dict)
                
        except Exception as e:
            logger.error("Erreur lors de la récupération du livre ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de récupérer le livre avec l'ID {book_id}: {e}") from e
    
    def get_all_books(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Récupère une liste paginée de livres depuis la base de données.
        
        Args:
            skip: Nombre d'éléments à sauter (pour la pagination).
            limit: Nombre maximum d'éléments à retourner.
            
        Returns:
            List[Book]: Une liste paginée des livres disponibles.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération des livres.
        """
        query = """
        SELECT id, title, category, price, stock, created_at, rating, url
        FROM books
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                
                books = []
                for row in results:
                    book = Book(
                        id=row[0],
                        title=row[1],
                        category=row[2],
                        price=row[3],
                        stock=row[4],
                        created_at=row[5],
                        rating=row[6],
                        url=row[7]
                    )
                    books.append(book)
                
                logger.info("%d livres récupérés (skip=%d, limit=%d)", len(books), skip, limit)
                return books
                
        except Exception as e:
            logger.error("Erreur lors de la récupération des livres (skip=%d, limit=%d): %s", 
                        skip, limit, str(e))
            raise DatabaseError(f"Impossible de récupérer la liste des livres: {e}") from e
    
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
            query: Terme de recherche (titre ou catégorie).
            
        Returns:
            List[Book]: Liste des livres correspondants à la recherche.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        search_query = f"%{query}%"
        query_sql = """
        SELECT * FROM books 
        WHERE title LIKE ? OR category LIKE ?
        ORDER BY created_at DESC
        """
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query_sql, (search_query, search_query))
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    # Convertir la ligne en dictionnaire
                    row_dict = dict(zip(columns, row))
                    # Récupérer les tags pour ce livre
                    cursor.execute("""
                        SELECT tag FROM book_tags WHERE book_id = ?
                    """, (row_dict['id'],))
                    tags = [tag[0] for tag in cursor.fetchall()]
                    row_dict['tags'] = tags
                    results.append(self._row_to_book(row_dict))
                return results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de livres avec le terme '{query}': {e}")
            raise DatabaseError(f"Erreur lors de la recherche de livres: {e}") from e
    
    def get_books_by_tag(self, tag: str, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Récupère les livres ayant un tag spécifique.
        
        Args:
            tag: Le tag à rechercher (insensible à la casse).
            skip: Nombre d'éléments à sauter (pour la pagination).
            limit: Nombre maximum d'éléments à retourner.
            
        Returns:
            List[Book]: Liste des livres ayant le tag spécifié.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        query = """
        SELECT DISTINCT b.* FROM books b
        JOIN book_tags bt ON b.id = bt.book_id
        WHERE LOWER(bt.tag) = LOWER(?)
        ORDER BY b.created_at DESC
        LIMIT ? OFFSET ?
        """
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, (tag, limit, skip))
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    # Convertir la ligne en dictionnaire
                    row_dict = dict(zip(columns, row))
                    # Récupérer les tags pour ce livre
                    cursor.execute("""
                        SELECT tag FROM book_tags WHERE book_id = ?
                    """, (row_dict['id'],))
                    tags = [tag[0] for tag in cursor.fetchall()]
                    row_dict['tags'] = tags
                    results.append(self._row_to_book(row_dict))
                return results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de livres avec le tag '{tag}': {e}")
            raise DatabaseError(f"Erreur lors de la recherche par tag: {e}") from e
            
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste de toutes les catégories uniques avec leur nombre d'occurrences.
        
        Returns:
            List[Dict[str, Any]]: Liste des catégories avec leur nombre d'occurrences.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération des catégories.
        """
        logger.info("Début de la récupération des catégories...")
        logger.info(f"Chemin de la base de données: {self.db_path}")
        
        try:
            # Vérifier si le fichier de base de données existe
            import os
            if not os.path.exists(self.db_path):
                error_msg = f"Le fichier de base de données n'existe pas à l'emplacement: {self.db_path}"
                logger.error(error_msg)
                raise DatabaseError(error_msg)
                
            with self._get_cursor() as cursor:
                # 1. Vérifier si la table books existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books';")
                if not cursor.fetchone():
                    error_msg = "La table 'books' n'existe pas dans la base de données"
                    logger.error(error_msg)
                    return []
                
                # 2. Vérifier si la colonne category existe
                cursor.execute("PRAGMA table_info(books);")
                columns = [col[1] for col in cursor.fetchall()]
                logger.info(f"Colonnes de la table 'books': {columns}")
                
                if 'category' not in columns:
                    logger.warning("La colonne 'category' n'existe pas dans la table 'books'.")
                    return []
                
                # 3. Récupérer toutes les catégories avec leur compte
                # en excluant les valeurs qui ne sont pas des vraies catégories
                query = """
                SELECT 
                    TRIM(category) as tag,
                    COUNT(*) as count
                FROM books
                WHERE category IS NOT NULL 
                  AND category != ''
                  AND LOWER(category) NOT IN ('add a comment', 'default', 'none', 'n/a', 'null')
                GROUP BY TRIM(category)
                HAVING COUNT(*) > 0
                ORDER BY count DESC, tag ASC
                """
                
                logger.info(f"Exécution de la requête: {query}")
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows:
                    logger.warning("Aucune catégorie valide trouvée dans la table 'books'.")
                    return []
                
                # 4. Formater les résultats
                result = [{"tag": row[0], "count": int(row[1])} for row in rows]
                logger.info(f"Récupération réussie de {len(result)} catégories")
                
                # Afficher les 5 premières catégories pour le débogage
                logger.info(f"Exemples de catégories: {result[:5]}")
                
                return result
                
        except Exception as e:
            error_msg = f"Erreur lors de la récupération des catégories: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg) from e
