"""
Configuration de l'application Books API.
"""
import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent  # Remonter d'un niveau pour atteindre la racine du projet
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Configuration de la base de données
DATABASE_PATH = os.path.join(DATA_DIR, 'books.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
DB_TIMEOUT = 30  # Timeout en secondes pour les opérations de base de données
DB_ISOLATION_LEVEL = None  # Utiliser le niveau d'isolation par défaut de SQLite

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration du logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(DATA_DIR, 'app.log'),
            'formatter': 'standard',
            'encoding': 'utf-8'
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'sqlalchemy': {
            'level': 'WARNING',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
    }
}

# Configuration de l'API
API_CONFIG = {
    'title': 'Books API',
    'description': 'API pour la gestion des livres',
    'version': '1.0.0',
    'docs_url': '/docs',
    'redoc_url': '/redoc',
    'openapi_url': '/openapi.json'
}

# Configuration CORS
CORS_CONFIG = {
    'allow_origins': ['*'],
    'allow_credentials': True,
    'allow_methods': ['*'],
    'allow_headers': ['*'],
}
