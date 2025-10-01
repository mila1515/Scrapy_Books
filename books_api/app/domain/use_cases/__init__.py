"""
Package contenant les cas d'utilisation (use cases) de l'application.

Ce module contient la logique métier de l'application, organisée en classes
qui implémentent les différentes opérations métier. Ces classes utilisent
les dépôts pour interagir avec les données.

Classes exportées:
    BookUseCases: Implémente les cas d'utilisation liés aux livres.
"""

from .book_usecases import BookUseCases

# Export public API
__all__ = [
    'BookUseCases',
]
