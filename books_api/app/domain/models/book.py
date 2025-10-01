from datetime import datetime
from typing import Optional, Dict, Any, Union
import re
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

class ValidationError(ValueError):
    """Exception levée lorsqu'une validation échoue."""
    pass

class Book:
    """
    Classe représentant un livre dans le système.
    
    Cette classe inclut des validations de données et des méthodes utilitaires
    pour manipuler les informations des livres.
    """
    
    def __init__(
        self, 
        id: int, 
        title: str, 
        category: Optional[str] = None, 
        price: float = 0.0, 
        stock: int = 0, 
        created_at: Optional[str] = None, 
        rating: Optional[Union[int, float]] = None, 
        url: Optional[str] = None
    ):
        """
        Initialise une instance de Book avec validation des données.
        
        Args:
            id: Identifiant unique du livre (doit être un entier positif).
            title: Titre du livre (ne peut pas être vide).
            category: Catégorie du livre (optionnel).
            price: Prix du livre (doit être un nombre positif ou zéro).
            stock: Quantité en stock (doit être un entier positif ou zéro).
            created_at: Date de création au format ISO (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS).
            rating: Note du livre entre 0 et 5 (optionnel).
            url: URL du livre (optionnel, doit être une URL valide si fournie).
            
        Raises:
            ValidationError: Si une des validations échoue.
        """
        self.id = self._validate_id(id)
        self.title = self._validate_title(title)
        self.category = self._validate_category(category) if category else None
        self.price = self._validate_price(price)
        self.stock = self._validate_stock(stock)
        self.created_at = self._validate_created_at(created_at) if created_at else None
        self.rating = self._validate_rating(rating) if rating is not None else None
        self.url = self._validate_url(url) if url else None
        
        logger.debug("Livre initialisé: %s (ID: %s)", self.title, self.id)
    
    def _validate_id(self, value: int) -> int:
        """Valide l'identifiant du livre."""
        if not isinstance(value, int) or value <= 0:
            error_msg = f"L'ID doit être un entier positif, reçu: {value}"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return value
    
    def _validate_title(self, value: str) -> str:
        """Valide le titre du livre."""
        if not isinstance(value, str) or not value.strip():
            error_msg = "Le titre ne peut pas être vide"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return value.strip()
    
    def _validate_category(self, value: str) -> str:
        """Valide la catégorie du livre."""
        if not isinstance(value, str) or not value.strip():
            error_msg = "La catégorie ne peut pas être vide"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return value.strip()
    
    def _validate_price(self, value: float) -> float:
        """Valide le prix du livre."""
        if not isinstance(value, (int, float)) or value < 0:
            error_msg = f"Le prix doit être un nombre positif, reçu: {value}"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return round(float(value), 2)
    
    def _validate_stock(self, value: int) -> int:
        """Valide la quantité en stock."""
        if not isinstance(value, int) or value < 0:
            error_msg = f"Le stock doit être un entier positif, reçu: {value}"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return value
    
    def _validate_created_at(self, value: str) -> str:
        """Valide la date de création."""
        try:
            # Essayer de parser la date
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        except (ValueError, TypeError) as e:
            error_msg = f"Format de date invalide: {value}. Utilisez le format ISO (ex: 2023-01-01T12:00:00)"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg) from e
    
    def _validate_rating(self, value: Union[int, float]) -> float:
        """Valide la note du livre."""
        if not isinstance(value, (int, float)) or not (0 <= value <= 5):
            error_msg = f"La note doit être un nombre entre 0 et 5, reçu: {value}"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return float(round(value * 2) / 2)  # Arrondi à 0.5 près
    
    def _validate_url(self, value: str) -> str:
        """Valide l'URL du livre."""
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ou une IP
            r'(?::\d+)?'  # port optionnel
            r'(?:/?|[/?]\S+)$', 
            re.IGNORECASE
        )
        
        if not re.match(url_pattern, value):
            error_msg = f"URL invalide: {value}"
            logger.error("Validation échouée - %s", error_msg)
            raise ValidationError(error_msg)
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le livre en dictionnaire.
        
        Returns:
            Dict[str, Any]: Une représentation en dictionnaire du livre.
        """
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at,
            'rating': self.rating,
            'url': self.url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """
        Crée une instance de Book à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du livre.
            
        Returns:
            Book: Une nouvelle instance de Book.
        """
        return cls(**data)
    
    def __repr__(self) -> str:
        """Représentation officielle de l'objet."""
        return f"<Book(id={self.id}, title='{self.title}', category='{self.category}')>"
    
    def __str__(self) -> str:
        """Représentation en chaîne de caractères."""
        return f"{self.title} ({self.category}) - {self.price}€"
    
    def is_available(self) -> bool:
        """
        Vérifie si le livre est en stock.
        
        Returns:
            bool: True si le livre est en stock, False sinon.
        """
        return self.stock > 0
    
    def update_stock(self, quantity: int) -> None:
        """
        Met à jour le stock du livre.
        
        Args:
            quantity: Quantité à ajouter (ou soustraire si négative) au stock.
            
        Raises:
            ValidationError: Si la mise à jour entraîne un stock négatif.
        """
        new_stock = self.stock + quantity
        if new_stock < 0:
            error_msg = f"Stock insuffisant. Tentative de passer de {self.stock} à {new_stock}"
            logger.error("Échec de la mise à jour du stock - %s", error_msg)
            raise ValidationError(error_msg)
        
        logger.info("Mise à jour du stock de '%s': %d -> %d", self.title, self.stock, new_stock)
        self.stock = new_stock
