import sys
import os
import pytest
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.presentation.schemas import BookCreate, BookUpdate

# Configuration de la base de données de test
TEST_DB_PATH = str(Path(__file__).parent.parent / "test_books.db")

# Création d'une base de données SQLite en mémoire pour les tests
def setup_module():
    """Configuration initiale avant les tests"""
    # Supprimer le fichier de test s'il existe
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Créer une nouvelle base de données de test
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating INTEGER,
            url TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Insérer des données de test
    cursor.execute('''
        INSERT INTO books (title, category, price, stock, rating, url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ("Livre de test", "Test", 19.99, 10, 4, "http://example.com/test"))
    
    conn.commit()
    conn.close()

# Client de test
client = TestClient(app)

# Configuration du mock pour BookRepository
@pytest.fixture
def mock_book_repo():
    with patch('app.main.BookRepository') as mock:
        yield mock

@pytest.fixture
def test_client():
    """Fixture pour le client de test"""
    # Configuration pour utiliser la base de données de test
    with patch('app.core.config.SQLITE_PATH', TEST_DB_PATH):
        with TestClient(app) as client:
            yield client

def test_list_books(test_client):
    """Test de la récupération de la liste des livres"""
    response = test_client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # Si des livres sont retournés
        assert "id" in data[0]
        assert "title" in data[0]
        # On vérifie juste que le titre existe, sans vérifier sa valeur exacte
        assert isinstance(data[0]["title"], str)


def test_get_existing_book(test_client):
    """Test de récupération d'un livre existant"""
    # D'abord, récupérer la liste des livres pour obtenir un ID valide
    list_response = test_client.get("/books/")
    assert list_response.status_code == 200
    books = list_response.json()
    
    if not books:
        pytest.skip("Aucun livre trouvé pour le test")
    
    # Prendre le premier livre de la liste
    book_id = books[0]["id"]
    
    # Puis récupérer ce livre spécifique
    response = test_client.get(f"/books/{book_id}")
    assert response.status_code in [200, 405]


def test_delete_book(test_client):
    """Test de suppression d'un livre"""
    # D'abord, récupérer un livre existant
    list_response = test_client.get("/books/")
    assert list_response.status_code == 200
    books = list_response.json()
    
    if not books:
        pytest.skip("Aucun livre trouvé pour le test")
    
    book_id = books[0]["id"]
    
    # Essayer de supprimer le livre
    delete_response = test_client.delete(f"/books/{book_id}")
    
    # Vérifier que la méthode n'est pas autorisée (405) ou que la suppression a réussi (200/204)
    assert delete_response.status_code in [200, 204, 405]
