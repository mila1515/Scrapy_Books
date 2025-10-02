from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging

from books_api.domain.book import Book
from books_api.domain.book_usecases import BookUseCases
from books_api.data.book_repository import BookRepository
from books_api.domain.user import User, verify_credentials

logger = logging.getLogger(__name__)

# Création du routeur
router = APIRouter(prefix="/api/v1", tags=["books"])

def get_book_usecases():
    """Dépendance pour obtenir une instance de BookUseCases."""
    repo = BookRepository()
    return BookUseCases(repo)

@router.get("/books", response_model=List[dict], 
             responses={
                 401: {"description": "Non autorisé - Identifiants manquants ou invalides"},
                 500: {"description": "Erreur serveur lors de la récupération des livres"}
             })
async def list_books(
    user: User = Depends(verify_credentials),
    skip: int = 0, 
    limit: int = 100,
    use_cases: BookUseCases = Depends(get_book_usecases)
):
    """
    Récupère une liste paginée de livres.
    
    Args:
        skip: Nombre d'éléments à sauter (pour la pagination).
        limit: Nombre maximum d'éléments à retourner (max 100).
        
    Returns:
        List[dict]: Liste des livres avec leurs détails.
    """
    try:
        books = use_cases.list_books(skip=skip, limit=limit)
        return [book.to_dict() for book in books]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des livres: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des livres")

@router.get("/books/{book_id}", response_model=Book,
             responses={
                 401: {"description": "Non autorisé - Authentification requise"},
                 404: {"description": "Livre non trouvé"}
             })
async def get_book(
    book_id: int,
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(verify_credentials)
):
    """
    Récupère les détails d'un livre par son ID.
    
    Args:
        book_id: L'identifiant unique du livre.
        
    Returns:
        dict: Les détails du livre demandé.
        
    Raises:
        HTTPException: Si le livre n'est pas trouvé.
    """
    try:
        book = use_cases.get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Livre non trouvé")
        return book.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du livre {book_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du livre")

@router.get("/books/search/", response_model=List[dict],
             responses={
                 400: {"description": "Le terme de recherche doit contenir au moins 2 caractères"},
                 401: {"description": "Non autorisé - Authentification requise"}
             })
async def search_books(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(verify_credentials)
):
    """
    Recherche des livres par titre ou catégorie.
    
    Args:
        q: Terme de recherche (au moins 2 caractères).
        
    Returns:
        List[dict]: Liste des livres correspondant à la recherche.
    """
    try:
        books = use_cases.search_books(q)
        return [book.to_dict() for book in books]
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de livres avec le terme '{q}': {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche de livres")

@router.get("/stats", response_model=dict,
             responses={
                 401: {"description": "Non autorisé - Authentification requise"},
                 500: {"description": "Erreur lors du calcul des statistiques"}
             })
async def get_stats(
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(verify_credentials)
):
    """
    Récupère des statistiques sur les livres.
    
    Returns:
        dict: Statistiques sur les livres (nombre total, prix moyen, etc.).
    """
    try:
        books = use_cases.list_books()
        if not books:
            return {
                "total_books": 0,
                "average_price": 0,
                "total_stock": 0,
                "categories": {}
            }
            
        total_books = len(books)
        total_price = sum(book.price for book in books)
        total_stock = sum(book.stock for book in books)
        
        # Compter les livres par catégorie
        categories = {}
        for book in books:
            if book.category:
                categories[book.category] = categories.get(book.category, 0) + 1
        
        return {
            "total_books": total_books,
            "average_price": round(total_price / total_books, 2) if total_books > 0 else 0,
            "total_stock": total_stock,
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des statistiques")
