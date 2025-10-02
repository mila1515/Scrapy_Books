"""
Package de gestion des données de l'API Books.

Ce package contient les composants d'accès aux données, y compris :
- Le repository pour les opérations CRUD sur les livres
- La configuration de l'authentification
"""

from .book_repo import BookRepository

__all__ = [
    'BookRepository'
]
