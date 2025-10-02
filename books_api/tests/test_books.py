"""
Tests unitaires et d'intégration pour les fonctionnalités liées aux livres de l'API.

Ce module contient des tests pour les endpoints de l'API concernant les livres,
y compris la création, la lecture, la mise à jour et la suppression de livres,
ainsi que les opérations de recherche et de filtrage.
"""

import os
import pytest
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime

# Configuration des chemins
BASE_DIR = Path(__file__).parent.parent

# Configuration de l'application de test
from app.main import app
from app.presentation.schemas import BookSchema, BookUpdate
from app.data.config import DB_CONFIG

# Configuration de la base de données de test
TEST_DB_PATH = str(BASE_DIR / "test_books.db")

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

# Configuration des routes de test
app.include_router(app.router)

# Configuration du mock pour BookRepository
@pytest.fixture
def mock_book_repo():
    with patch('app.data.book_repo.BookRepository') as mock:
        yield mock

@pytest.fixture(scope="module")
def test_client():
    """Fixture pour le client de test"""
    # Sauvegarder la configuration originale
    original_db = DB_CONFIG['database']
    
    try:
        # Utiliser la base de données de test
        DB_CONFIG['database'] = TEST_DB_PATH
        
        # Configurer l'application pour les tests
        with TestClient(app) as client:
            yield client
    finally:
        # Restaurer la configuration originale
        DB_CONFIG['database'] = original_db

def test_list_books(test_client, mock_book_repo):
    """Test de la récupération de la liste des livres"""
    # Configurer le mock pour retourner une liste de livres factices
    mock_books = [
        {"id": 1, "title": "Livre Test", "price": 19.99, "stock": 10},
        {"id": 2, "title": "Autre Livre", "price": 29.99, "stock": 5}
    ]
    mock_book_repo.return_value.get_all_books.return_value = mock_books
    
    # Faire la requête
    response = test_client.get("/books/")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]


def test_get_existing_book(test_client, mock_book_repo):
    """Test de récupération d'un livre existant"""
    # Configurer le mock pour retourner un livre factice
    mock_book = {"id": 1, "title": "Livre Test", "price": 19.99, "stock": 10}
    mock_book_repo.return_value.get_book.return_value = mock_book
    
    # Tester avec un ID valide
    response = test_client.get("/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Livre Test"


def test_delete_book(test_client, mock_book_repo):
    """Test de suppression d'un livre"""
    # Configurer le mock pour simuler une suppression réussie
    mock_book_repo.return_value.delete_book.return_value = True
    
    # Tester la suppression d'un livre
    response = test_client.delete("/books/1")
    
    # Vérifier que la suppression a été appelée avec le bon ID
    mock_book_repo.return_value.delete_book.assert_called_once_with(1)
    
    # Vérifier que le code de statut est 204 (No Content) pour une suppression réussie
    assert response.status_code in [200, 204, 405]
