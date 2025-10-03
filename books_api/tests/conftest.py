import pytest
import os
import sys
import base64
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Définir le chemin de la base de données de test
test_db_path = project_root / "test_books.db"

# Configurer les variables d'environnement pour les tests
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

test_username = "testuser"
test_password = "testpassword"
os.environ["ADMIN_USERNAME"] = test_username
os.environ["ADMIN_PASSWORD"] = test_password  # En production, ce serait un hash
os.environ["ADMIN_DISABLED"] = "false"

# Importer l'application après avoir configuré l'environnement
from domain.user import User, USERS_DB
from presentation.main import app, get_book_usecases
from data.book_repository import BookRepository

# Créer un mock pour get_book_usecases qui utilise la base de données de test
def mock_get_book_usecases():
    # S'assurer que le répertoire parent existe
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Créer une nouvelle instance de BookRepository avec l'URL de la base de test
    repo = BookRepository()
    
    # Configurer la base de données pour les tests
    repo.db_path = str(test_db_path)
    
    from domain.book_usecases import BookUseCases
    return BookUseCases(repo)

# Configurer l'application de test
app.dependency_overrides[get_book_usecases] = mock_get_book_usecases

# Importer les routes après avoir configuré les dépendances
import books_api.presentation.routes  # noqa: F401

@pytest.fixture(scope="module")
def client():
    """Fixture pour le client de test FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def auth_headers():
    """Retourne les en-têtes d'authentification pour les tests en utilisant Basic Auth."""
    credentials = f"{test_username}:{test_password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return {"Authorization": f"Basic {encoded_credentials}"}

@pytest.fixture(scope="module")
def test_db():
    """Configuration de la base de données de test."""
    import sqlite3
    
    # S'assurer que le répertoire parent existe
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Supprimer la base de données de test si elle existe
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Créer une nouvelle base de données de test
    conn = sqlite3.connect(str(test_db_path))
    
    # Créer une nouvelle base de données de test
    conn = sqlite3.connect(str(test_db_path))
    cursor = conn.cursor()
    
    # Créer les tables nécessaires
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        rating REAL,
        category TEXT,
        stock INTEGER,
        url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Créer la table users si elle n'existe pas déjà
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0
    )
    ''')
    
    # Créer la table book_tags pour les tests de recherche par tag
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_tags (
        book_id INTEGER,
        tag TEXT,
        FOREIGN KEY (book_id) REFERENCES books(id),
        PRIMARY KEY (book_id, tag)
    )
    ''')
    
    # Créer un utilisateur de test avec un mot de passe hashé
    # Le mot de passe est 'testpassword' hashé avec bcrypt
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 'testpassword' hashé
    cursor.execute('''
    INSERT OR REPLACE INTO users (username, email, hashed_password, is_active, is_admin)
    VALUES (?, ?, ?, ?, ?)
    ''', ("testuser", "test@example.com", hashed_password, 1, 1))
    
    # Créer des livres de test
    test_books = [
        ("Livre de Test", 19.99, 4.2, "programming", 5, "http://example.com/test-book"),
        ("Python Programming", 39.99, 4.7, "programming", 15, "http://example.com/python-book"),
        ("Test Book 2", 25.50, 4.0, "testing", 8, "http://example.com/test-book-2")
    ]
    
    for book in test_books:
        cursor.execute('''
        INSERT INTO books (title, price, rating, category, stock, url)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', book)
        
        # Ajouter des tags pour les livres de programmation
        if book[3] == "programming":
            book_id = cursor.lastrowid
            cursor.execute('''
            INSERT INTO book_tags (book_id, tag)
            VALUES (?, ?)
            ''', (book_id, "programming"))
            cursor.execute('''
            INSERT INTO book_tags (book_id, tag)
            VALUES (?, ?)
            ''', (book_id, "development"))
    
    conn.commit()
    yield conn
    
    # Nettoyage après les tests
    conn.close()
    
    # S'assurer que la connexion est bien fermée avant de supprimer le fichier
    import gc
    gc.collect()
    
    # Essayer de supprimer le fichier avec plusieurs tentatives
    import time
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            if test_db_path.exists():
                test_db_path.unlink()
            break
        except (PermissionError, OSError) as e:
            if attempt == max_attempts - 1:  # Dernière tentative
                print(f"Impossible de supprimer le fichier de test après {max_attempts} tentatives: {e}")
            time.sleep(0.1)  # Attendre un peu avant de réessayer
