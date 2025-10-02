"""
Package contenant les spiders du projet Scrapy.

Ce package contient les définitions des spiders utilisés pour le scraping.
"""

# Import des spiders pour les rendre disponibles lors de l'import du package
from .scrapybooks import ScrapybooksSpider

# Liste des spiders disponibles
__all__ = ['ScrapybooksSpider']
