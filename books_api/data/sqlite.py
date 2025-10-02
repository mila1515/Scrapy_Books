import sqlite3
import logging
import os
from contextlib import contextmanager
from typing import Iterator
from books_api.data.config import DATABASE_PATH, DB_TIMEOUT, DB_ISOLATION_LEVEL, DATA_DIR

# Configuration du logger
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Contexte manager pour gérer les connexions à la base de données SQLite.
    
    Returns:
        sqlite3.Connection: Une connexion à la base de données.
        
    Raises:
        DatabaseError: Si la connexion échoue ou si le fichier n'est pas accessible.
    """
    # Création du répertoire s'il n'existe pas
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = None
    try:
        logger.debug(f"Connexion à la base de données : {DATABASE_PATH}")
        conn = sqlite3.connect(
            DATABASE_PATH,
            timeout=DB_TIMEOUT,
            isolation_level=DB_ISOLATION_LEVEL,
            check_same_thread=False
        )
        
        # Activer les clés étrangères
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Configuration pour de meilleures performances
        conn.execute("PRAGMA journal_mode = WAL")  # Mode Write-Ahead Logging
        conn.execute("PRAGMA synchronous = NORMAL")  # Meilleures performances
        conn.execute("PRAGMA cache_size = -2000")  # 2MB de cache
        
        yield conn
        
    except sqlite3.Error as e:
        error_msg = f"Erreur de connexion à la base de données: {e}"
        logger.error(error_msg)
        raise DatabaseError(error_msg) from e
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Connexion à la base de données fermée")
            except sqlite3.Error as e:
                logger.error(f"Erreur lors de la fermeture de la connexion: {e}")
