from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional, Dict, Any
import logging

from app.presentation.schemas import BookSchema, BookCreate, BookUpdate
from app.domain.use_cases.book_usecases import BookUseCases
from app.data.repositories.book_repository import BookRepository, DatabaseError

# Configuration du logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/books", 
    tags=["books"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Erreur interne du serveur"}
    }
)

# Initialisation du repository et des cas d'utilisation
try:
    repo = BookRepository()
    use_cases = BookUseCases(repo)
except DatabaseError as e:
    logger.critical(f"Impossible d'initialiser le repository de livres: {e}")
    raise

def handle_database_error(e: Exception) -> None:
    """
    Gère les erreurs de base de données et les convertit en HTTPException approprié.
    
    Args:
        e: L'exception à gérer.
        
    Raises:
        HTTPException: Une exception HTTP avec un message d'erreur approprié.
    """
    logger.error(f"Erreur de base de données: {e}")
    if "not found" in str(e).lower() or "introuvable" in str(e).lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ressource non trouvée"
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Une erreur est survenue lors de l'accès aux données"
    )

@router.get(
    "/", 
    response_model=List[BookSchema],
    status_code=status.HTTP_200_OK,
    summary="Liste tous les livres",
    description="""
    Récupère la liste de tous les livres disponibles dans la base de données.
    
    Retourne une liste vide si aucun livre n'est trouvé.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Liste des livres récupérée avec succès",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Titre du livre",
                            "category": "Fiction",
                            "price": 19.99,
                            "stock": 5,
                            "created_at": "2023-01-01T00:00:00",
                            "rating": 4,
                            "url": "http://example.com/book/1"
                        }
                    ]
                }
            }
        }
    }
)
async def get_books() -> List[BookSchema]:
    """
    Récupère tous les livres de la base de données.
    
    Returns:
        List[BookSchema]: Une liste de tous les livres disponibles.
        
    Raises:
        HTTPException: Si une erreur survient lors de la récupération des livres.
    """
    try:
        return use_cases.list_books()
    except Exception as e:
        handle_database_error(e)

@router.get(
    "/{book_id}",
    response_model=BookSchema,
    status_code=status.HTTP_200_OK,
    summary="Récupère un livre par son ID",
    description="""
    Récupère un livre spécifique à partir de son identifiant unique.
    
    Retourne une erreur 404 si le livre n'est pas trouvé.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Livre trouvé avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Titre du livre",
                        "category": "Fiction",
                        "price": 19.99,
                        "stock": 5,
                        "created_at": "2023-01-01T00:00:00",
                        "rating": 4,
                        "url": "http://example.com/book/1"
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Livre non trouvé",
            "content": {
                "application/json": {
                    "example": {"detail": "Livre non trouvé"}
                }
            }
        }
    }
)
async def get_book(book_id: int) -> BookSchema:
    """
    Récupère un livre spécifique par son identifiant unique.
    
    Args:
        book_id: L'identifiant unique du livre à récupérer.
        
    Returns:
        BookSchema: Les détails du livre demandé.
        
    Raises:
        HTTPException: 
            - 404 si le livre n'est pas trouvé.
            - 500 en cas d'erreur serveur.
    """
    try:
        book = use_cases.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livre avec l'ID {book_id} non trouvé"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e)

@router.get(
    "/search/title/{title}",
    response_model=List[BookSchema],
    status_code=status.HTTP_200_OK,
    summary="Recherche des livres par titre",
    description="""
    Recherche des livres dont le titre contient le texte fourni (insensible à la casse).
    
    Paramètres de requête optionnels pour filtrer les résultats :
    - min_price: Prix minimum
    - max_price: Prix maximum
    - min_rating: Note minimale (1-5)
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Recherche effectuée avec succès",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Titre du livre",
                            "category": "Fiction",
                            "price": 19.99,
                            "stock": 5,
                            "created_at": "2023-01-01T00:00:00",
                            "rating": 4,
                            "url": "http://example.com/book/1"
                        }
                    ]
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Aucun livre ne correspond aux critères de recherche",
            "content": {
                "application/json": {
                    "example": {"detail": "Aucun livre trouvé avec un titre contenant 'python'"}
                }
            }
        }
    }
)
async def search_books_by_title(
    title: str,
    min_price: Optional[float] = Query(
        None, 
        ge=0, 
        description="Filtre les livres dont le prix est supérieur ou égal à cette valeur"
    ),
    max_price: Optional[float] = Query(
        None, 
        ge=0, 
        description="Filtre les livres dont le prix est inférieur ou égal à cette valeur"
    ),
    min_rating: Optional[int] = Query(
        None, 
        ge=1, 
        le=5, 
        description="Filtre les livres dont la note est supérieure ou égale à cette valeur (1-5)"
    )
) -> List[BookSchema]:
    """
    Recherche des livres par titre avec des filtres optionnels.
    
    Args:
        title: Texte à rechercher dans les titres des livres.
        min_price: Prix minimum des livres à inclure dans les résultats.
        max_price: Prix maximum des livres à inclure dans les résultats.
        min_rating: Note minimale des livres à inclure (1-5).
        
    Returns:
        List[BookSchema]: Liste des livres correspondant aux critères de recherche.
        
    Raises:
        HTTPException: 
            - 404 si aucun livre ne correspond aux critères.
            - 500 en cas d'erreur serveur.
    """
    try:
        # Validation des paramètres
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le prix minimum ne peut pas être supérieur au prix maximum"
            )
            
        books = use_cases.search_books_by_title(title)
        
        # Appliquer les filtres
        if min_price is not None:
            books = [b for b in books if b.price >= min_price]
        if max_price is not None:
            books = [b for b in books if b.price <= max_price]
        if min_rating is not None and hasattr(books[0], 'rating') and books[0].rating is not None:
            books = [b for b in books if b.rating and b.rating >= min_rating]
        
        if not books:
            error_detail = f"Aucun livre trouvé avec un titre contenant '{title}'"
            if any([min_price, max_price, min_rating]):
                error_detail += " et répondant aux critères de filtrage"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail
            )
            
        return books
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e)

@router.get(
    "/search/category/{category}",
    response_model=List[BookSchema],
    status_code=status.HTTP_200_OK,
    summary="Recherche des livres par catégorie",
    description="""
    Récupère tous les livres appartenant à une catégorie spécifique.
    
    Paramètres de requête optionnels :
    - in_stock: Si vrai, ne retourne que les livres en stock
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Recherche par catégorie effectuée avec succès",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Titre du livre",
                            "category": "Fiction",
                            "price": 19.99,
                            "stock": 5,
                            "created_at": "2023-01-01T00:00:00",
                            "rating": 4,
                            "url": "http://example.com/book/1"
                        }
                    ]
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Aucun livre trouvé dans cette catégorie",
            "content": {
                "application/json": {
                    "example": {"detail": "Aucun livre trouvé dans la catégorie 'Science-Fiction'"}
                }
            }
        }
    }
)
async def search_books_by_category(
    category: str,
    in_stock: Optional[bool] = Query(
        False, 
        description="Si vrai, ne retourne que les livres actuellement en stock"
    )
) -> List[BookSchema]:
    """
    Recherche des livres par catégorie avec un filtre optionnel pour les livres en stock.
    
    Args:
        category: La catégorie de livres à rechercher.
        in_stock: Si vrai, ne retourne que les livres en stock.
        
    Returns:
        List[BookSchema]: Liste des livres de la catégorie spécifiée.
        
    Raises:
        HTTPException: 
            - 404 si aucun livre n'est trouvé dans la catégorie.
            - 500 en cas d'erreur serveur.
    """
    try:
        books = use_cases.search_books_by_category(category)
        
        if in_stock:
            books = [b for b in books if b.stock > 0]
        
        if not books:
            error_detail = f"Aucun livre trouvé dans la catégorie '{category}'"
            if in_stock:
                error_detail += " en stock"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail
            )
            
        return books
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e)

@router.get(
    "/stats/summary",
    summary="Statistiques sur les livres",
    description="""
    Récupère des statistiques détaillées sur les livres, y compris :
    - Nombre total de livres
    - Nombre de livres en stock
    - Valeur totale du stock
    - Répartition par catégorie
    - Meilleurs livres par note
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Statistiques récupérées avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "total_books": 100,
                        "total_in_stock": 75,
                        "total_value": 1500.50,
                        "categories_count": {
                            "Fiction": 40,
                            "Science-Fiction": 30,
                            "Informatique": 30
                        },
                        "top_rated_books": [
                            {"title": "Meilleur Livre", "rating": 5, "price": 24.99},
                            {"title": "Second Meilleur", "rating": 4.8, "price": 19.99}
                        ]
                    }
                }
            }
        }
    }
)
async def get_books_stats() -> Dict[str, Any]:
    """
    Récupère des statistiques sur les livres.
    
    Returns:
        Dict[str, Any]: Un dictionnaire contenant diverses statistiques sur les livres.
        
    Raises:
        HTTPException: En cas d'erreur lors de la récupération des données.
    """
    try:
        # Utilisation de la méthode dédiée du cas d'utilisation
        return use_cases.get_books_statistics()
        
    except Exception as e:
        handle_database_error(e)
