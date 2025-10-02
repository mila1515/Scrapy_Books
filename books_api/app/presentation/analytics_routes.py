"""
Routes d'analyse des données de livres.

Fournit des endpoints pour obtenir des statistiques et analyses sur les livres.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
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
    prefix="/api/analytics",
    tags=["Analytiques"]
)

# Import de la fonction d'authentification
from .auth_routes import verify_credentials

def get_db_connection():
    """Crée une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/price-stats", response_model=Dict[str, Any])
async def get_price_stats(_: bool = Depends(verify_credentials)):
    """
    Récupère les statistiques de prix des livres.
    
    Returns:
        Dict contenant les statistiques de prix (moyenne, min, max, écart-type)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pour les statistiques de prix
        cursor.execute('''
            SELECT 
                ROUND(AVG(price), 2) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                ROUND(AVG(CASE WHEN price > 0 THEN price ELSE NULL END), 2) as avg_non_zero_price,
                COUNT(*) as total_books,
                COUNT(DISTINCT category) as total_categories
            FROM books
        ''')
        
        stats = dict(cursor.fetchone())
        conn.close()
        
        return {
            "statistiques_prix": {
                "prix_moyen": stats["avg_price"],
                "prix_minimum": stats["min_price"],
                "prix_maximum": stats["max_price"],
                "prix_moyen_hors_zero": stats["avg_non_zero_price"],
                "nombre_total_livres": stats["total_books"],
                "nombre_categories": stats["total_categories"]
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques de prix: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques de prix"
        )

@router.get("/top-categories", response_model=List[Dict[str, Any]])
async def get_top_categories(limit: int = 5, _: bool = Depends(verify_credentials)):
    """
    Récupère les catégories les plus populaires par nombre de livres.
    
    Args:
        limit: Nombre maximum de catégories à retourner (par défaut: 5)
        
    Returns:
        Liste des catégories avec leur nombre de livres
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                category as categorie,
                COUNT(*) as nombre_livres,
                ROUND(AVG(price), 2) as prix_moyen,
                ROUND(AVG(rating), 1) as note_moyenne
            FROM books
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category
            ORDER BY COUNT(*) DESC
            LIMIT ?
        ''', (limit,))
        
        categories = []
        for row in cursor.fetchall():
            categories.append(dict(row))
            
        conn.close()
        return categories
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories"
        )

@router.get("/price-by-category", response_model=List[Dict[str, Any]])
async def get_price_by_category(_: bool = Depends(verify_credentials)):
    """
    Récupère les statistiques de prix par catégorie.
    
    Returns:
        Liste des catégories avec leurs statistiques de prix
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                category as categorie,
                COUNT(*) as nombre_livres,
                ROUND(MIN(price), 2) as prix_min,
                ROUND(MAX(price), 2) as prix_max,
                ROUND(AVG(price), 2) as prix_moyen,
                ROUND(SUM(price * stock) / NULLIF(SUM(stock), 0), 2) as prix_moyen_pondere
            FROM books
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category
            HAVING COUNT(*) > 0
            ORDER BY prix_moyen DESC
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append(dict(row))
            
        conn.close()
        return categories
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des prix par catégorie: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des prix par catégorie"
        )

@router.get("/stock-analysis", response_model=Dict[str, Any])
async def get_stock_analysis(_: bool = Depends(verify_credentials)):
    """
    Analyse du stock des livres.
    
    Returns:
        Dictionnaire contenant des statistiques sur le stock
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Statistiques générales sur le stock
        cursor.execute('''
            SELECT 
                SUM(stock) as total_stock,
                COUNT(*) as total_livres,
                SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as livres_rupture,
                ROUND(AVG(stock), 2) as stock_moyen,
                ROUND(AVG(price * stock), 2) as valeur_stock_moyenne
            FROM books
        ''')
        
        stats = dict(cursor.fetchone())
        
        # Livres en rupture de stock
        cursor.execute('''
            SELECT title, price, category
            FROM books
            WHERE stock = 0
            ORDER BY price DESC
            LIMIT 10
        ''')
        
        rupture_stock = [dict(row) for row in cursor.fetchall()]
        
        # Catégories avec le plus de stock
        cursor.execute('''
            SELECT 
                category as categorie,
                SUM(stock) as total_stock,
                ROUND(AVG(price), 2) as prix_moyen
            FROM books
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category
            ORDER BY total_stock DESC
            LIMIT 5
        ''')
        
        categories_stock = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "statistiques_stock": {
                "total_stock": stats["total_stock"],
                "stock_moyen_par_livre": stats["stock_moyen"],
                "livres_en_rupture": stats["livres_rupture"],
                "taux_rupture": round((stats["livres_rupture"] / stats["total_livres"]) * 100, 2) if stats["total_livres"] > 0 else 0,
                "valeur_stock_moyenne": stats["valeur_stock_moyenne"]
            },
            "top_ruptures": rupture_stock,
            "categories_plus_stock": categories_stock
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'analyse du stock"
        )
