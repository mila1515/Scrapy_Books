from typing import List, Optional, Dict, Any
import logging

from app.domain.models.book import Book
from app.data.repositories.book_repository import BookRepository, DatabaseError

# Configuration du logger
logger = logging.getLogger(__name__)

class BookUseCases:
    """
    Classe de cas d'utilisation pour la gestion des livres.
    
    Cette classe encapsule la logique métier liée aux opérations sur les livres
    et délègue les opérations de persistance au repository.
    """
    
    def __init__(self, repo: BookRepository):
        """
        Initialise les cas d'utilisation avec un repository de livres.
        
        Args:
            repo: Une instance de BookRepository pour les opérations de persistance.
        """
        self.repo = repo
        logger.info("BookUseCases initialisé avec le repository: %s", repr(repo))

    def list_books(self) -> List[Book]:
        """
        Récupère la liste de tous les livres.
        
        Returns:
            List[Book]: Une liste de tous les livres disponibles.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération des livres.
        """
        try:
            logger.debug("Récupération de tous les livres")
            books = self.repo.get_all_books()
            logger.info("%d livres récupérés avec succès", len(books))
            return books
        except Exception as e:
            logger.error("Erreur lors de la récupération de tous les livres: %s", str(e))
            raise DatabaseError(f"Impossible de récupérer la liste des livres: {e}") from e

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Récupère un livre par son identifiant unique.
        
        Args:
            book_id: L'identifiant unique du livre à récupérer.
            
        Returns:
            Optional[Book]: Le livre correspondant à l'ID, ou None si non trouvé.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la récupération du livre.
        """
        if not isinstance(book_id, int) or book_id <= 0:
            logger.warning("ID de livre invalide: %s", book_id)
            return None
            
        try:
            logger.debug("Récupération du livre avec l'ID: %d", book_id)
            book = self.repo.get_book(book_id)
            if book:
                logger.debug("Livre trouvé: %s", book.title)
            else:
                logger.debug("Aucun livre trouvé avec l'ID: %d", book_id)
            return book
        except Exception as e:
            logger.error("Erreur lors de la récupération du livre %d: %s", book_id, str(e))
            raise DatabaseError(f"Impossible de récupérer le livre avec l'ID {book_id}: {e}") from e
        
    def search_books_by_title(self, title: str) -> List[Book]:
        """
        Recherche des livres dont le titre contient le texte spécifié.
        
        La recherche est insensible à la casse.
        
        Args:
            title: Le texte à rechercher dans les titres des livres.
            
        Returns:
            List[Book]: Une liste de livres dont le titre contient le texte recherché.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        if not title or not isinstance(title, str) or not title.strip():
            logger.warning("Terme de recherche de titre invalide: %s", title)
            return []
            
        try:
            logger.debug("Recherche de livres avec le titre contenant: '%s'", title)
            books = self.repo.search_books_by_title(title)
            logger.info("%d livres trouvés pour la recherche de titre: '%s'", len(books), title)
            return books
        except Exception as e:
            logger.error("Erreur lors de la recherche de livres par titre '%s': %s", title, str(e))
            raise DatabaseError(f"Erreur lors de la recherche par titre: {e}") from e
        
    def search_books_by_category(self, category: str) -> List[Book]:
        """
        Recherche des livres par catégorie.
        
        La recherche est insensible à la casse.
        
        Args:
            category: La catégorie de livres à rechercher.
            
        Returns:
            List[Book]: Une liste de livres appartenant à la catégorie spécifiée.
            
        Raises:
            DatabaseError: Si une erreur survient lors de la recherche.
        """
        if not category or not isinstance(category, str) or not category.strip():
            logger.warning("Catégorie de recherche invalide: %s", category)
            return []
            
        try:
            logger.debug("Recherche de livres dans la catégorie: '%s'", category)
            books = self.repo.search_books_by_category(category)
            logger.info("%d livres trouvés dans la catégorie: '%s'", len(books), category)
            return books
        except Exception as e:
            logger.error("Erreur lors de la recherche de livres par catégorie '%s': %s", category, str(e))
            raise DatabaseError(f"Erreur lors de la recherche par catégorie: {e}") from e
            
    def get_books_statistics(self) -> Dict[str, Any]:
        """
        Calcule des statistiques avancées sur les livres.
        
        Returns:
            Dict[str, Any]: Un dictionnaire contenant diverses statistiques sur les livres,
            y compris des analyses détaillées par catégorie, prix et disponibilité.
            
        Raises:
            DatabaseError: Si une erreur survient lors du calcul des statistiques.
        """
        try:
            logger.debug("Calcul des statistiques avancées sur les livres")
            books = self.list_books()
            
            if not books:
                return {
                    "message": "Aucun livre trouvé dans la base de données",
                    "overview": {
                        "total_books": 0,
                        "total_in_stock": 0,
                        "out_of_stock_count": 0,
                        "total_value": 0.0
                    },
                    "price_analysis": {
                        "average_price": 0.0,
                        "min_price": 0.0,
                        "max_price": 0.0,
                        "price_distribution": {}
                    },
                    "category_analysis": {
                        "categories_count": {},
                        "top_category": None,
                        "category_price_avg": {}
                    },
                    "stock_analysis": {
                        "average_stock": 0.0,
                        "min_stock": 0,
                        "max_stock": 0,
                        "low_stock_books": []
                    },
                    "top_rated_books": None,
                    "recently_added": None
                }
            
            # Livres en stock et hors stock
            books_in_stock = [b for b in books if b.stock > 0]
            out_of_stock = [b for b in books if b.stock == 0]
            
            # Analyse des prix
            prices = [b.price for b in books]
            avg_price = sum(prices) / len(prices) if prices else 0
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0
            
            # Distribution des prix par tranches
            price_ranges = {
                "0-10": 0,
                "10-20": 0,
                "20-30": 0,
                "30-50": 0,
                "50-100": 0,
                "100+": 0
            }
            
            for price in prices:
                if price < 10:
                    price_ranges["0-10"] += 1
                elif price < 20:
                    price_ranges["10-20"] += 1
                elif price < 30:
                    price_ranges["20-30"] += 1
                elif price < 50:
                    price_ranges["30-50"] += 1
                elif price < 100:
                    price_ranges["50-100"] += 1
                else:
                    price_ranges["100+"] += 1
            
            # Analyse par catégorie
            categories = {}
            category_prices = {}
            category_counts = {}
            
            for book in books:
                if book.category:
                    # Comptage des livres par catégorie
                    categories[book.category] = categories.get(book.category, 0) + 1
                    
                    # Somme des prix par catégorie pour calculer la moyenne plus tard
                    if book.category not in category_prices:
                        category_prices[book.category] = 0.0
                        category_counts[book.category] = 0
                    category_prices[book.category] += book.price
                    category_counts[book.category] += 1
            
            # Calcul des moyennes par catégorie
            category_avg_price = {
                cat: round(category_prices[cat] / count, 2)
                for cat, count in category_counts.items()
            }
            
            # Catégorie la plus représentée
            top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else None
            
            # Analyse du stock
            stocks = [b.stock for b in books_in_stock]
            avg_stock = sum(stocks) / len(stocks) if stocks else 0
            min_stock = min(stocks) if stocks else 0
            max_stock = max(stocks) if stocks else 0
            
            # Livres avec faible stock (moins de 5 exemplaires) - on garde les 3 derniers
            low_stock_books = [
                {"id": b.id, "title": b.title, "stock": b.stock, "price": b.price, "category": b.category}
                for b in books_in_stock if 0 < b.stock < 5
            ][-3:]  # Prendre uniquement les 3 derniers
            
            # Livres les mieux notés (si la notation est disponible)
            top_rated = []
            if hasattr(books[0], 'rating') and books[0].rating is not None:
                top_rated = sorted(
                    [b for b in books if b.rating is not None],
                    key=lambda x: x.rating,
                    reverse=True
                )[:5]
            
            # Derniers livres ajoutés (si la date de création est disponible)
            recently_added = []
            if hasattr(books[0], 'created_at') and books[0].created_at is not None:
                recently_added = sorted(
                    [b for b in books if b.created_at is not None],
                    key=lambda x: x.created_at,
                    reverse=True
                )[:5]

            # Préparation des résultats
            stats = {
                "overview": {
                    "total_books": len(books),
                    "total_in_stock": len(books_in_stock),
                    "out_of_stock_count": len(out_of_stock),
                    "total_value": round(sum(b.price * b.stock for b in books_in_stock), 2)
                },
                "price_analysis": {
                    "average_price": round(avg_price, 2),
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2),
                    "price_distribution": price_ranges
                },
                "category_analysis": {
                    "categories_count": categories,
                    "top_category": top_category,
                    "category_price_avg": category_avg_price,
                    "total_categories": len(categories)
                },
                "stock_analysis": {
                    "average_stock": round(avg_stock, 2),
                    "min_stock": min_stock,
                    "max_stock": max_stock,
                    "low_stock_books": low_stock_books,
                    "low_stock_count": len(low_stock_books)
                },
                "rating_analysis": {
                    "books_with_rating": sum(1 for b in books if hasattr(b, 'rating') and b.rating is not None),
                    "average_rating": round(
                        sum(b.rating for b in books if hasattr(b, 'rating') and b.rating is not None) / 
                        sum(1 for b in books if hasattr(b, 'rating') and b.rating is not None), 2
                    ) if any(hasattr(b, 'rating') and b.rating is not None for b in books) else None
                }
            }

            # Ajout des meilleurs livres si disponibles
            if top_rated:
                stats["top_rated_books"] = [
                    {
                        "id": b.id,
                        "title": b.title,
                        "rating": b.rating,
                        "price": b.price,
                        "category": b.category,
                        "in_stock": b.stock > 0
                    }
                    for b in top_rated
                ]
            
            # Ajout des derniers livres ajoutés si disponibles
            if recently_added:
                stats["recently_added"] = [
                    {
                        "id": b.id,
                        "title": b.title,
                        "created_at": b.created_at,
                        "price": b.price,
                        "category": b.category,
                        "in_stock": b.stock > 0
                    }
                    for b in recently_added
                ]

            logger.info("Statistiques avancées calculées avec succès pour %d livres", len(books))
            return stats
            
        except Exception as e:
            logger.error("Erreur lors du calcul des statistiques avancées: %s", str(e))
            raise DatabaseError(f"Impossible de calculer les statistiques avancées: {e}") from e
