from datetime import datetime
from typing import Optional, Dict, Any, Union, List
import re
import logging
from pydantic import BaseModel, validator, Field

# Configuration du logger
logger = logging.getLogger(__name__)

class ValidationError(ValueError):
    """Exception levée lorsqu'une validation échoue."""
    pass

class BookBase(BaseModel):
    """Modèle de base pour un livre."""
    id: int
    title: str
    category: Optional[str] = None
    price: float = 0.0
    stock: int = 0
    created_at: Optional[str] = None
    rating: Optional[Union[int, float]] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True

class Book(BookBase):
    """
    Classe représentant un livre dans le système.
    
    Cette classe inclut des validations de données et des méthodes utilitaires
    pour manipuler les informations des livres.
    """
    
    def __init__(
        self, 
        id: int, 
        title: str, 
        price: float = 0.0, 
        stock: int = 0, 
        created_at: Optional[str] = None, 
        rating: Optional[Union[int, float]] = None, 
        url: Optional[str] = None
    ) -> None:
        """
        Initialise un nouveau livre avec validation des données.
        
        Args:
            id: Identifiant unique du livre.
            title: Titre du livre (obligatoire).
            category: Catégorie du livre (optionnel).
            price: Prix du livre (par défaut 0.0).
            stock: Quantité en stock (par défaut 0).
            created_at: Date de création au format ISO (optionnel).
            rating: Note du livre entre 0 et 5 (optionnel).
            url: URL de la page du livre (optionnel).
            
        Raises:
            ValidationError: Si une des validations échoue.
        """
        # Appel au constructeur de la classe parente (BookBase)
        super().__init__(
            id=id,
            title=title,
            category=category,
            price=price,
            stock=stock,
            created_at=created_at,
            rating=rating,
            url=url
        )
        
        # Validation des données
        self._validate_id(id)
        self._validate_title(title)
        self._validate_price(price)
        self._validate_stock(stock)
        self._validate_created_at(created_at) if created_at else datetime.utcnow().isoformat()
        self._validate_rating(rating)
        self._validate_url(url) if url else None

    def _validate_id(self, id: int) -> int:
        """Valide que l'ID est un entier positif."""
        if not isinstance(id, int) or id <= 0:
            raise ValidationError(f"L'ID doit être un entier positif, reçu: {id}")
        return id

    def _validate_title(self, title: str) -> str:
        """Valide que le titre n'est pas vide."""
        if not title or not title.strip():
            raise ValidationError("Le titre ne peut pas être vide")
        return title.strip()

    def _validate_category(self, category: str) -> str:
        """Valide la catégorie."""
        if not category or not category.strip():
            raise ValidationError("La catégorie ne peut pas être vide")
        return category.strip()

    def _validate_price(self, price: float) -> float:
        """Valide que le prix est un nombre positif ou zéro."""
        if not isinstance(price, (int, float)) or price < 0:
            raise ValidationError(f"Le prix doit être un nombre positif, reçu: {price}")
        return float(price)

    def _validate_stock(self, stock: int) -> int:
        """Valide que le stock est un entier positif ou zéro."""
        if not isinstance(stock, int) or stock < 0:
            raise ValidationError(f"Le stock doit être un entier positif, reçu: {stock}")
        return stock

    def _validate_created_at(self, created_at: str) -> str:
        """Valide le format de la date de création."""
        try:
            # Essayer de parser la date pour vérifier son format
            datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            return created_at
        except ValueError as e:
            raise ValidationError(f"Format de date invalide, utilisez le format ISO (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS): {e}")

    def _validate_rating(self, rating: Union[int, float, None]) -> Optional[float]:
        """Valide que la note est comprise entre 0 et 5."""
        if rating is None:
            return None
            
        if not isinstance(rating, (int, float)) or not (0 <= float(rating) <= 5):
            raise ValidationError(f"La note doit être un nombre entre 0 et 5, reçu: {rating}")
        return float(rating)

    def _validate_url(self, url: str) -> str:
        """Valide le format de l'URL."""
        if url is None:
            return url
            
        url_regex = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%\_\+.~#?&\/\/=]*)$'
        if not re.match(url_regex, url):
            raise ValidationError(f"URL invalide: {url}")
        return url

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet Book en dictionnaire."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "created_at": self.created_at,
            "rating": self.rating,
            "url": self.url
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """Crée une instance de Book à partir d'un dictionnaire."""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            category=data.get('category'),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            created_at=data.get('created_at'),
            rating=data.get('rating'),
            url=data.get('url')
        )
        
    def __str__(self) -> str:
        """Représentation en chaîne de caractères du livre."""
        return f"Livre(id={self.id}, title='{self.title}', price={self.price}, stock={self.stock})"

    def __repr__(self) -> str:
        """Représentation technique du livre."""
        return (f"Book(id={self.id}, title='{self.title}', category='{self.category}', "
                f"price={self.price}, stock={self.stock}, created_at='{self.created_at}', "
                f"rating={self.rating}, url='{self.url}')")
