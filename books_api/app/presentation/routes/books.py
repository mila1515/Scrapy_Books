from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.presentation.schemas import BookSchema, BookCreate, BookUpdate
from app.domain.use_cases.book_usecases import BookUseCases
from app.data.repositories.book_repository import BookRepository

router = APIRouter(prefix="/books", tags=["books"])

# Initialisation du repository et des cas d'utilisation
repo = BookRepository()
use_cases = BookUseCases(repo)

@router.get(
    "/", 
    response_model=List[BookSchema],
    summary="Liste tous les livres",
    description="Récupère la liste de tous les livres disponibles dans la base de données."
)
async def get_books():
    """
    Récupère tous les livres de la base de données.
    """
    return use_cases.list_books()

@router.get(
    "/{book_id}",
    response_model=BookSchema,
    summary="Récupère un livre par son ID",
    responses={
        200: {"description": "Livre trouvé"},
        404: {"description": "Livre non trouvé"}
    }
)
async def get_book(book_id: int):
    """
    Récupère un livre spécifique par son identifiant unique.
    """
    book = use_cases.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@router.get(
    "/search/title/{title}",
    response_model=List[BookSchema],
    summary="Recherche des livres par titre",
    description="Recherche des livres dont le titre contient le texte fourni (insensible à la casse)."
)
async def search_books_by_title(
    title: str,
    min_price: Optional[float] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="Prix maximum"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Note minimum (1-5)")
):
    """
    Recherche des livres par titre avec des filtres optionnels.
    """
    books = use_cases.search_books_by_title(title)
    
    # Appliquer les filtres
    if min_price is not None:
        books = [b for b in books if b.price >= min_price]
    if max_price is not None:
        books = [b for b in books if b.price <= max_price]
    if min_rating is not None and hasattr(books[0], 'rating') and books[0].rating is not None:
        books = [b for b in books if b.rating and b.rating >= min_rating]
    
    if not books:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun livre trouvé avec un titre contenant '{title}'" + 
                  (f" et répondant aux critères de filtrage" if any([min_price, max_price, min_rating]) else "")
        )
    return books

@router.get(
    "/search/category/{category}",
    response_model=List[BookSchema],
    summary="Recherche des livres par catégorie",
    description="Récupère tous les livres appartenant à une catégorie spécifique."
)
async def search_books_by_category(
    category: str,
    in_stock: Optional[bool] = Query(False, description="Filtrer uniquement les livres en stock")
):
    """
    Recherche des livres par catégorie avec un filtre optionnel pour les livres en stock.
    """
    books = use_cases.search_books_by_category(category)
    
    if in_stock:
        books = [b for b in books if b.stock > 0]
    
    if not books:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun livre trouvé dans la catégorie '{category}'" +
                  (" en stock" if in_stock else "")
        )
    return books

# Statistiques
@router.get("/stats/summary", summary="Statistiques sur les livres")
async def get_books_stats():
    """
    Récupère des statistiques sur les livres (nombre total, en stock, par catégorie, etc.)
    """
    books = use_cases.list_books()
    
    if not books:
        return {"message": "Aucun livre trouvé dans la base de données"}
    
    total_books = len(books)
    total_in_stock = sum(1 for b in books if b.stock > 0)
    total_value = sum(b.price * b.stock for b in books if b.stock > 0)
    
    # Comptage par catégorie
    categories = {}
    for book in books:
        if book.category:
            categories[book.category] = categories.get(book.category, 0) + 1
    
    # Livres les mieux notés
    if hasattr(books[0], 'rating') and books[0].rating is not None:
        top_rated = sorted(
            [b for b in books if b.rating],
            key=lambda x: x.rating,
            reverse=True
        )[:5]
    else:
        top_rated = []
    
    return {
        "total_books": total_books,
        "total_in_stock": total_in_stock,
        "total_value": round(total_value, 2),
        "categories_count": categories,
        "top_rated_books": [
            {"title": b.title, "rating": b.rating, "price": b.price}
            for b in top_rated
        ] if top_rated else None
    }
