"""
Module de gestion des opérations de base de données pour les livres.

Ce module fournit une interface pour interagir avec la table 'books' de la base de données SQLite.
"""

import sqlite3
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import os

# Configuration du logger
logger = logging.getLogger(__name__)

# Chemin vers la base de données
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "monprojet", "books.db")

class BookRepository:
    """
    Repository pour gérer les opérations CRUD sur les livres.
    
    Cette classe fournit des méthodes pour interagir avec la table 'books'
    de manière sécurisée et encapsule la logique d'accès aux données.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialise le repository avec le chemin vers la base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
    
    def _get_connection(self):
        """Crée et retourne une connexion à la base de données."""
        return sqlite3.connect(self.db_path)
    
    def _execute_query(self, query: str, params: tuple = (), fetch_one: bool = False) -> Any:
        """Exécute une requête SQL et retourne le résultat."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                else:
                    return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur SQL: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un livre par son ID.
        
        Args:
            book_id: L'ID du livre à récupérer
            
        Returns:
            Un dictionnaire contenant les informations du livre, ou None si non trouvé
        """
        query = "SELECT * FROM books WHERE id = ?"
        return self._execute_query(query, (book_id,), fetch_one=True)
    
    def get_books(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère une liste de livres avec des filtres optionnels.
        
        Args:
            skip: Nombre d'éléments à sauter (pour la pagination)
            limit: Nombre maximum d'éléments à retourner
            category: Filtre par catégorie (optionnel)
            min_price: Prix minimum (optionnel)
            max_price: Prix maximum (optionnel)
            
        Returns:
            Une liste de dictionnaires contenant les informations des livres
        """
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
            
        query += f" LIMIT {limit} OFFSET {skip}"
        return self._execute_query(query, tuple(params))
    
    def get_categories(self) -> List[str]:
        """
        Récupère la liste des catégories distinctes de livres.
        
        Returns:
            Une liste des noms de catégories uniques
        """
        query = "SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category"
        result = self._execute_query(query)
        return [row['category'] for row in result if row['category']]
