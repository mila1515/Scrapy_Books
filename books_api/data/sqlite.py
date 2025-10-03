import sqlite3
import logging
import os
import atexit
import shutil
from contextlib import contextmanager
from typing import Iterator
from books_api.data.config import DATABASE_URL, DB_TIMEOUT, DB_ISOLATION_LEVEL, DATA_DIR, SQLITE_TEMP_DIR

# Configuration du logger
logger = logging.getLogger(__name__)

# Liste pour garder une trace des connexions actives
_active_connections = []

# Fonction de nettoyage
def cleanup_sqlite_temp():
    """Nettoie les fichiers temporaires SQLite"""
    if not _active_connections:  # Ne nettoyer que si aucune connexion active
        try:
            if os.path.exists(SQLITE_TEMP_DIR):
                for filename in os.listdir(SQLITE_TEMP_DIR):
                    file_path = os.path.join(SQLITE_TEMP_DIR, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer {file_path}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des fichiers temporaires: {e}")

# Enregistrer la fonction de nettoyage à la fermeture de l'application
atexit.register(cleanup_sqlite_temp)

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass

# Création du répertoire temporaire s'il n'existe pas
def _setup_temp_dir():
    """Configure le répertoire temporaire pour les fichiers SQLite"""
    try:
        os.makedirs(SQLITE_TEMP_DIR, exist_ok=True)
        # Définir les permissions pour éviter les problèmes d'accès
        os.chmod(SQLITE_TEMP_DIR, 0o777)
        # Définir la variable d'environnement pour SQLite
        os.environ['SQLITE_TMPDIR'] = SQLITE_TEMP_DIR
    except Exception as e:
        logger.warning(f"Impossible de configurer le répertoire temporaire: {e}")

# Configurer le répertoire temporaire au démarrage
_setup_temp_dir()

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Contexte manager pour gérer les connexions à la base de données SQLite.
    
    Returns:
        sqlite3.Connection: Une connexion à la base de données.
        
    Raises:
        DatabaseError: Si la connexion échoue ou si le fichier n'est pas accessible.
    """
    # Création des répertoires nécessaires
    os.makedirs(DATA_DIR, exist_ok=True)
    _setup_temp_dir()
    
    global _active_connections
    conn = None
    try:
        # Extraire le chemin du fichier depuis DATABASE_URL (format: sqlite:///chemin/vers/la/base.db)
        db_path = DATABASE_URL.split('///')[-1]
        logger.debug(f"Connexion à la base de données : {db_path}")
        
        # Créer le répertoire parent si nécessaire
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        # Configuration de la connexion SQLite avec des paramètres optimisés
        conn = sqlite3.connect(
            db_path,
            timeout=DB_TIMEOUT,
            isolation_level=None,  # Désactive le mode de transaction par défaut
            check_same_thread=False
        )
        # Activer les clés étrangères
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Configuration optimisée pour les performances
        conn.execute("PRAGMA journal_mode = WAL")  # Mode Write-Ahead Logging
        conn.execute("PRAGMA cache_size = -10000")  # 10MB de cache
        conn.execute("PRAGMA temp_store = MEMORY")  # Stocker les tables temporaires en mémoire
        conn.execute("PRAGMA mmap_size = 300000000")  # 300MB de mémoire mappée
        conn.execute("PRAGMA busy_timeout = 30000")  # Timeout de 30 secondes
        conn.execute("PRAGMA optimize")  # Optimiser la base de données au démarrage
        
        _active_connections.append(conn)
        try:
            yield conn
        finally:
            _active_connections.remove(conn)
        
    except sqlite3.Error as e:
        error_msg = f"Erreur de connexion à la base de données: {e}"
        raise DatabaseError(error_msg) from e
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture de la connexion: {e}")
            finally:
                # Essayer de nettoyer les fichiers temporaires
                if conn in _active_connections:
                    _active_connections.remove(conn)
                cleanup_sqlite_temp()
