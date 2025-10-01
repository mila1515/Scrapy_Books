import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Optional, Iterator

from app.data.config.config import SQLITE_PATH

logger = logging.getLogger(__name__)

# Configuration de la base de données
DB_TIMEOUT = 30.0  # secondes
DB_ISOLATION_LEVEL = "IMMEDIATE"  # Niveau d'isolation des transactions

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
    # Vérification du fichier de base de données
    if not os.path.exists(SQLITE_PATH):
        error_msg = f"Le fichier de base de données n'existe pas à l'emplacement : {SQLITE_PATH}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)
    
    # Vérification des permissions
    if not os.access(SQLITE_PATH, os.R_OK | os.W_OK):
        error_msg = f"Permissions insuffisantes pour accéder au fichier : {SQLITE_PATH}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)
    
    conn = None
    try:
        logger.debug(f"Connexion à la base de données : {SQLITE_PATH}")
        conn = sqlite3.connect(
            SQLITE_PATH,
            timeout=DB_TIMEOUT,
            isolation_level=DB_ISOLATION_LEVEL,
            check_same_thread=False
        )
        
        # Configuration de la connexion
        conn.row_factory = sqlite3.Row
        
        # Activer les clés étrangères
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Activer le mode WAL pour de meilleures performances
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Configuration du cache pour de meilleures performances
        conn.execute("PRAGMA cache_size = -2000")  # 2MB de cache
        
        logger.debug("Connexion à la base de données établie avec succès")
        yield conn
        
    except sqlite3.Error as e:
        error_msg = f"Erreur de base de données: {e}"
        logger.error(error_msg)
        raise DatabaseError(error_msg) from e
        
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Connexion à la base de données fermée")
            except sqlite3.Error as e:
                logger.error(f"Erreur lors de la fermeture de la connexion: {e}")
