from typing import List, Optional, Dict, Any
import logging

from books_api.domain.book import Book
from books_api.data.book_repository import BookRepository, DatabaseError

# Configuration du logger
logger = logging.getLogger(__name__)

class BookUseCases:
    """
    Classe de cas d'utilisation pour la gestion des livres.
    
    Cette classe encapsule la logique métier liée aux opérations sur les livres
    et délègue les opérations de persistance au repository.
    """
    
    def __init__(self, repo: BookRepository):
        """
        Initialise les cas d'utilisation avec un repository de livres.
        
        Args:
            repo: Une instance de BookRepository pour les opérations de persistance.
        """
        self.repo = repo
        logger.info("BookUseCases initialisé avec le repository: %s", repr(repo))

    def list_books(self) -> List[Book]:
        """
        Récupère la liste de tous les livres.
        
        Returns:
            List[Book]: Une liste de tous les livres disponibles.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération des livres.
        """
        try:
            logger.debug("Récupération de tous les livres")
            books = self.repo.get_all_books()
            logger.info("%d livres récupérés avec succès", len(books))
            return books
        except Exception as e:
            logger.error("Erreur lors de la récupération de tous les livres: %s", str(e))
            raise DatabaseError(f"Impossible de récupérer la liste des livres: {e}") from e

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Récupère un livre par son identifiant unique.
        
        Args:
            book_id: L'identifiant unique du livre à récupérer.
            
        Returns:
            Optional[Book]: Le livre correspondant à l'ID, ou None si non trouvé.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération du livre.
        """
        try:
            logger.debug("Récupération du livre avec l'ID: %s", book_id)
            book = self.repo.get_book_by_id(book_id)
            if book:
                logger.info("Livre avec l'ID %s récupéré avec succès", book_id)
            else:
                logger.warning("Aucun livre trouvé avec l'ID: %s", book_id)
            return book
        except Exception as e:
            logger.error("Erreur lors de la récupération du livre avec l'ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de récupérer le livre avec l'ID {book_id}: {e}") from e

    def create_book(self, book_data: Dict[str, Any]) -> Book:
        """
        Crée un nouveau livre.
        
        Args:
            book_data: Dictionnaire contenant les données du livre à créer.
            
        Returns:
            Book: Le livre créé avec son nouvel ID.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la création du livre.
        """
        try:
            logger.debug("Création d'un nouveau livre avec les données: %s", book_data)
            new_book = Book.from_dict(book_data)
            created_book = self.repo.add_book(new_book)
            logger.info("Nouveau livre créé avec l'ID: %s", created_book.id)
            return created_book
        except Exception as e:
            logger.error("Erreur lors de la création du livre: %s", str(e))
            raise DatabaseError(f"Impossible de créer le livre: {e}") from e

    def update_book(self, book_id: int, book_data: Dict[str, Any]) -> Optional[Book]:
        """
        Met à jour un livre existant.
        
        Args:
            book_id: L'identifiant du livre à mettre à jour.
            book_data: Dictionnaire contenant les données à mettre à jour.
            
        Returns:
            Optional[Book]: Le livre mis à jour, ou None si le livre n'existe pas.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la mise à jour du livre.
        """
        try:
            logger.debug("Mise à jour du livre avec l'ID %s avec les données: %s", book_id, book_data)
            
            # Vérifier si le livre existe
            existing_book = self.repo.get_book_by_id(book_id)
            if not existing_book:
                logger.warning("Tentative de mise à jour d'un livre inexistant avec l'ID: %s", book_id)
                return None
                
            # Mettre à jour les champs fournis
            for key, value in book_data.items():
                if hasattr(existing_book, key) and value is not None:
                    setattr(existing_book, key, value)
            
            updated_book = self.repo.update_book(existing_book)
            if updated_book:
                logger.info("Livre avec l'ID %s mis à jour avec succès", book_id)
            else:
                logger.warning("Échec de la mise à jour du livre avec l'ID: %s", book_id)
                
            return updated_book
            
        except Exception as e:
            logger.error("Erreur lors de la mise à jour du livre avec l'ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de mettre à jour le livre avec l'ID {book_id}: {e}") from e

    def delete_book(self, book_id: int) -> bool:
        """
        Supprime un livre par son identifiant.
        
        Args:
            book_id: L'identifiant du livre à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False si le livre n'existe pas.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la suppression du livre.
        """
        try:
            logger.debug("Suppression du livre avec l'ID: %s", book_id)
            result = self.repo.delete_book(book_id)
            if result:
                logger.info("Livre avec l'ID %s supprimé avec succès", book_id)
            else:
                logger.warning("Aucun livre trouvé avec l'ID à supprimer: %s", book_id)
            return result
        except Exception as e:
            logger.error("Erreur lors de la suppression du livre avec l'ID %s: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de supprimer le livre avec l'ID {book_id}: {e}") from e

    def search_books(self, query: str) -> List[Book]:
        """
        Recherche des livres par titre ou catégorie.
        
        Args:
            query: Chaîne de recherche pour filtrer les livres par titre ou catégorie.
            
        Returns:
            List[Book]: Liste des livres correspondant aux critères de recherche.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        try:
            logger.debug("Recherche de livres avec la requête: %s", query)
            books = self.repo.search_books(query)
            logger.info("%d livres trouvés pour la requête '%s'", len(books), query)
            return books
        except Exception as e:
            logger.error("Erreur lors de la recherche de livres avec la requête '%s': %s", query, str(e))
            raise DatabaseError(f"Erreur lors de la recherche de livres avec la requête '{query}': {e}") from e
