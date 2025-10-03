from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional, Dict, Any
import logging

from books_api.domain.book import Book
from books_api.domain.book_usecases import BookUseCases
from books_api.data.book_repository import BookRepository
from books_api.domain.user import User
from .auth import get_current_active_user

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
    user: User = Depends(get_current_active_user),
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
    user: User = Depends(get_current_active_user)
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
                 401: {"description": "Non autorisé - Authentification requise"},
                 500: {"description": "Erreur lors de la recherche de livres"}
             })
async def search_books(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(get_current_active_user)
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

@router.get("/tags", response_model=List[Dict[str, Any]],
             responses={
                 401: {"description": "Non autorisé - Authentification requise"},
                 500: {"description": "Erreur lors de la récupération des tags"}
             })
async def get_all_tags(
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(get_current_active_user)
):
    """
    Récupère la liste de tous les tags disponibles avec leur nombre d'occurrences.
    
    Returns:
        List[Dict[str, Any]]: Liste des tags avec leur nombre d'occurrences.
        Format: [{"tag": "nom_du_tag", "count": nombre_d_occurrences}, ...]
    """
    try:
        return use_cases.get_all_tags()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des tags"
        )

@router.get("/books/tag/{tag}", response_model=List[dict],
             responses={
                 400: {"description": "Le tag ne peut pas être vide"},
                 401: {"description": "Non autorisé - Authentification requise"},
                 404: {"description": "Aucun livre trouvé avec ce tag"},
                 500: {"description": "Erreur lors de la recherche par tag"}
             })
async def get_books_by_tag(
    tag: str = Path(..., description="Tag à rechercher"),
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments à retourner"),
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(get_current_active_user)
):
    """
    Recherche des livres par tag.
    
    Args:
        tag: Tag à rechercher (insensible à la casse).
        skip: Nombre d'éléments à sauter (pagination).
        limit: Nombre maximum d'éléments à retourner (max 1000).
        
    Returns:
        List[dict]: Liste des livres ayant le tag spécifié.
    """
    try:
        books = use_cases.get_books_by_tag(tag, skip=skip, limit=limit)
        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun livre trouvé avec le tag: {tag}"
            )
        return [book.to_dict() for book in books]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de livres avec le tag '{tag}': {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche par tag")

@router.get("/stats", response_model=dict,
             responses={
                 401: {"description": "Non autorisé - Authentification requise"},
                 500: {"description": "Erreur lors du calcul des statistiques"}
             })
async def get_stats(
    use_cases: BookUseCases = Depends(get_book_usecases),
    user: User = Depends(get_current_active_user)
):
    """
    Récupère des statistiques sur les livres.
    
    Returns:
        dict: Statistiques sur les livres (nombre total, prix moyen, etc.).
    """
    try:
        # Utiliser le repository directement pour de meilleures performances
        repo = BookRepository()
        
        # Récupérer le nombre total de livres
        with repo._get_cursor() as cursor:
            # Compter le nombre total de livres
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]
            
            # Calculer le prix moyen et le stock total
            cursor.execute("""
                SELECT 
                    AVG(price) as avg_price,
                    SUM(stock) as total_stock
                FROM books
            """)
            avg_price, total_stock = cursor.fetchone()
            
            # Compter les livres par catégorie
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM books
                WHERE category IS NOT NULL
                GROUP BY category
            """)
            categories = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "total_books": total_books,
            "average_price": round(float(avg_price or 0), 2),
            "total_stock": total_stock or 0,
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des statistiques")
