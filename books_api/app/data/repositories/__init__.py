"""
Package contenant les implémentations des dépôts pour l'accès aux données.

Ce module fournit des implémentations concrètes des dépôts pour interagir avec
des sources de données telles que des bases de données, des API, etc.

Classes exportées:
    BookRepository: Implémentation du dépôt pour les livres.
    DatabaseError: Exception pour les erreurs liées à la base de données.
"""

from .book_repository import BookRepository, DatabaseError

# Export public API
__all__ = [
    'BookRepository',
    'DatabaseError',
]
