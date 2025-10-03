"""
Configuration de l'application Books API.
Charge les paramètres depuis les variables d'environnement avec des valeurs par défaut.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'monprojet', '.env')
print(f"Chargement du fichier .env depuis : {env_path}")
load_dotenv(env_path)

# Afficher les informations de débogage pour l'authentification
print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME')}")
print(f"ADMIN_PASSWORD: {'*' * 8 if os.getenv('ADMIN_PASSWORD') else 'Non défini'}")

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Racine du projet
DATA_DIR = os.path.join(BASE_DIR, 'monprojet')
SQLITE_TEMP_DIR = os.path.join(BASE_DIR, '.sqlite_temp')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(DATA_DIR, "books.db")}')
DB_TIMEOUT = int(os.getenv('DB_TIMEOUT', '30'))
DB_ISOLATION_LEVEL = os.getenv('DB_ISOLATION_LEVEL', None)

# Vérifier si le fichier de base de données existe
if DATABASE_URL.startswith('sqlite'):
    db_path = DATABASE_URL.split('///')[-1]
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"Avertissement : La base de données sera créée à l'emplacement : {db_path}")

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
    'title': os.getenv('API_TITLE', 'Books API'),
    'description': os.getenv('API_DESCRIPTION', 'API pour la gestion des livres'),
    'version': os.getenv('API_VERSION', '1.0.0'),
    'docs_url': os.getenv('API_DOCS_URL', '/docs'),
    'redoc_url': os.getenv('API_REDOC_URL', '/redoc'),
    'openapi_url': os.getenv('API_OPENAPI_URL', '/openapi.json'),
    'debug': os.getenv('API_DEBUG', 'False').lower() in ('true', '1', 't'),  # Désactiver le mode debug en production
    'swagger_ui_parameters': {
        'syntaxHighlight.theme': 'monokai',  # Thème plus lisible
        'filter': False,  # Désactiver complètement le filtre
        'persistAuthorization': True,  # Conserver l'autorisation
        'displayRequestDuration': True,  # Afficher la durée des requêtes
        'tryItOutEnabled': True,  # Activer le bouton "Try it out"
        'requestSnippetsEnabled': True,  # Activer les extraits de code
        'defaultModelsExpandDepth': 0,  # Masquer les modèles par défaut
        'defaultModelExpandDepth': 1,  # Profondeur d'expansion des modèles
        'tagsSorter': 'alpha',  # Trier les tags par ordre alphabétique
        'operationsSorter': 'alpha',  # Trier les opérations par ordre alphabétique
        'docExpansion': 'list',  # Afficher uniquement les tags au démarrage
        'showExtensions': False,  # Masquer les extensions
        'showCommonExtensions': False,  # Masquer les extensions communes
        'displayOperationId': False,  # Masquer les IDs des opérations
        'showMutatedRequest': False,  # Masquer les requêtes mutées
        'withCredentials': True,  # Activer l'envoi des credentials
        'layout': 'BaseLayout'  # Utiliser une mise en page plus simple
    }
}

# Configuration CORS optimisée
CORS_CONFIG = {
    'allow_origins': os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(','),
    'allow_credentials': os.getenv('CORS_ALLOW_CREDENTIALS', 'True').lower() in ('true', '1', 't'),
    'allow_methods': os.getenv('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','),
    'allow_headers': os.getenv(
        'CORS_ALLOW_HEADERS', 
        'Content-Type,Authorization,Accept,Origin,X-Requested-With'
    ).split(','),
    'max_age': int(os.getenv('CORS_MAX_AGE', '600')),  # Cache CORS en secondes
    'expose_headers': os.getenv('CORS_EXPOSE_HEADERS', 'Content-Length').split(',')
}
