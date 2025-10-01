"""
Package contenant les modèles de domaine de l'application.

Ce module définit les classes de modèles qui représentent les entités métier
de l'application. Ces modèles contiennent la logique de validation et de
comportement des entités.

Classes exportées:
    Book: Modèle représentant un livre dans le système.
    ValidationError: Exception pour les erreurs de validation des modèles.
"""

from .book import Book, ValidationError

# Export public API
__all__ = [
    'Book',
    'ValidationError',
]
