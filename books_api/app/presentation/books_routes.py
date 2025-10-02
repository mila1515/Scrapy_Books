"""
Routes pour la gestion des livres.

Fournit des endpoints pour accéder aux données des livres.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import sqlite3
import logging
from pathlib import Path
import os

# Configuration du logger
logger = logging.getLogger(__name__)

# Chemin vers la base de données
BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "monprojet", "books.db")

# Création du routeur
router = APIRouter(
    prefix="/api/books",
    tags=["Livres"]
)

# Import de la fonction d'authentification
from .auth_routes import verify_credentials

# Fonction utilitaire pour la connexion à la base de données
def get_db_connection():
    """Crée une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints
@router.get("/", response_model=List[Dict[str, Any]])
async def get_books(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    _: bool = Depends(verify_credentials)
):
    """
    Récupère la liste des livres avec des filtres optionnels.
    
    Args:
        category: Filtrer par catégorie
        min_price: Prix minimum
        max_price: Prix maximum
        
    Returns:
        Liste des livres correspondant aux critères
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
            
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
            
        cursor.execute(query, params)
        books = cursor.fetchall()
        conn.close()
        
        return [dict(book) for book in books]
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des livres: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des livres"
        )

@router.get("/{book_id}", response_model=Dict[str, Any])
async def get_book(
    book_id: int,
    _: bool = Depends(verify_credentials)
):
    """
    Récupère un livre par son ID.
    
    Args:
        book_id: L'ID du livre à récupérer
        
    Returns:
        Les détails du livre demandé
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        conn.close()
        
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livre non trouvé"
            )
            
        return dict(book)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du livre {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du livre"
        )

@router.get("/categories/", response_model=List[str])
async def get_categories(_: bool = Depends(verify_credentials)):
    """
    Récupère la liste de toutes les catégories de livres disponibles.
    
    Returns:
        Liste des catégories uniques
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM books ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories"
        )
