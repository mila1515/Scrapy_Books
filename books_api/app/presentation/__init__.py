"""
Package de présentation de l'application.

Ce package contient les routes et les schémas de l'API.
"""

from .schemas import BookSchema, BookUpdate
from .books_routes import router as books_router

__all__ = [
    'BookSchema',
    'BookUpdate',
    'books_router'
]
