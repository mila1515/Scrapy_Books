"""
Books API - Application Package

Ce package contient l'application FastAPI et ses composants principaux.
"""

# Import des composants principaux pour les rendre disponibles au niveau du package
from .main import app
from .data.book_repo import BookRepository
from .presentation.books_routes import router as books_router
from .presentation.auth_routes import router as auth_router

__all__ = [
    'app',
    'BookRepository',
    'books_router',
    'auth_router'
]
