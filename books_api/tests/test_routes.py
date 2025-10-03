import pytest
import os
import sys
from fastapi import status

# Charger la configuration de test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Données de test
TEST_BOOK = {
    "title": "Livre de Test",
    "price": 19.99,
    "rating": 4,  # Changed from 4.5 to integer
    "category": "Test",
    "stock": 10,
    "url": "http://example.com/test"
}

def test_read_books_empty(client, test_db, auth_headers):
    """Teste la récupération de la liste des livres."""
    # Vider la table des livres pour ce test
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM books")
    test_db.commit()
    
    response = client.get("/api/v1/books", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_create_and_get_book(client, test_db, auth_headers):
    """Teste la création et la récupération d'un livre."""
    # Créer un livre directement dans la base de données
    cursor = test_db.cursor()
    cursor.execute(
        """
        INSERT INTO books (title, price, rating, category, stock, url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (TEST_BOOK["title"], TEST_BOOK["price"], TEST_BOOK["rating"], 
         TEST_BOOK["category"], TEST_BOOK["stock"], TEST_BOOK["url"])
    )
    book_id = cursor.lastrowid
    test_db.commit()
    
    # Récupérer le livre via l'API
    response = client.get(f"/api/v1/books/{book_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == TEST_BOOK["title"]
    assert data["price"] == TEST_BOOK["price"]
    assert data["id"] == book_id

def test_search_books(client, test_db, auth_headers):
    """Teste la recherche de livres."""
    # Ajouter un livre spécifique pour le test de recherche
    cursor = test_db.cursor()
    cursor.execute("""
    INSERT INTO books (title, price, rating, category, stock, url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("Python Programming", 35.99, 5, "Programming", 10, "http://example.com/python"))
    test_db.commit()
    
    # Tester la recherche
    response = client.get("/api/v1/books/search/?q=Python", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0, "Aucun livre trouvé avec le terme de recherche 'Python'"
    assert any("Python" in book.get("title", "") for book in data), "Aucun livre avec 'Python' dans le titre trouvé"

def test_get_all_tags(client, auth_headers):
    """Teste la récupération des tags."""
    response = client.get("/api/v1/tags", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    # Vérifie que la réponse est une liste
    assert isinstance(response.json(), list)

def test_get_books_by_tag(client, test_db, auth_headers):
    """Teste la récupération des livres par tag."""
    # Ajouter un livre avec un tag pour le test
    cursor = test_db.cursor()
    
    # Ajouter un livre
    cursor.execute("""
    INSERT INTO books (title, price, rating, category, stock, url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("Python Book", 29.99, 5, "Programming", 5, "http://example.com/python-book"))
    book_id = cursor.lastrowid
    
    # Ajouter un tag pour ce livre
    cursor.execute("""
    INSERT INTO book_tags (book_id, tag)
    VALUES (?, ?)
    """, (book_id, "programming"))
    
    test_db.commit()
    
    # Tester la récupération par tag
    response = client.get("/api/v1/books/tag/programming", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0, "Aucun livre trouvé avec le tag 'programming'"
    assert any(book.get("title") == "Python Book" for book in data), "Le livre attendu n'a pas été trouvé dans les résultats"
