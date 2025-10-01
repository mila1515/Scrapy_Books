from pydantic import BaseModel, Field, HttpUrl, validator, constr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import re

class BookBase(BaseModel):
    """
    Schéma de base pour un livre avec des champs communs.
    """
    title: constr(min_length=1, max_length=255) = Field(
        ...,
        description="Titre du livre (1-255 caractères)",
        example="Le Petit Prince"
    )
    
    category: Optional[constr(max_length=100)] = Field(
        None,
        description="Catégorie du livre (max 100 caractères)",
        example="Littérature"
    )
    
    price: float = Field(
        ...,
        ge=0.0,
        le=10000.0,
        description="Pix du livre en euros (0-10 000€)",
        example=19.99
    )
    
    stock: int = Field(
        ...,
        ge=0,
        le=1_000_000,
        description="Quantité en stock (0-1 000 000)",
        example=10
    )
    
    rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Note moyenne du livre (0.0-5.0)",
        example=4.5
    )
    
    url: Optional[HttpUrl] = Field(
        None,
        description="URL de la page du livre",
        example="https://example.com/le-petit-prince"
    )
    
    # Validation personnalisée pour le titre
    @validator('title')
    def validate_title(cls, v):
        # Supprimer les espaces superflus
        v = ' '.join(v.strip().split())
        
        # Vérifier que le titre contient des caractères alphanumériques
        if not any(c.isalnum() for c in v):
            raise ValueError("Le titre doit contenir au moins un caractère alphanumérique")
            
        return v
    
    # Validation personnalisée pour le prix
    @validator('price')
    def validate_price(cls, v):
        # Arrondir à 2 décimales
        return round(v, 2)
    
    # Validation personnalisée pour la note
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None:
            # Arrondir à 0.5 près (4.3 -> 4.5, 4.2 -> 4.0)
            return round(v * 2) / 2
        return v
    
    # Validation personnalisée pour l'URL
    @validator('url', pre=True)
    def validate_url(cls, v):
        if v is None or v == '':
            return None
        return v


class BookCreate(BookBase):
    """
    Schéma pour la création d'un nouveau livre.
    Hérite de tous les champs de BookBase.
    """
    pass


class BookUpdate(BaseModel):
    """
    Schéma pour la mise à jour partielle d'un livre.
    Tous les champs sont optionnels.
    """
    title: Optional[constr(min_length=1, max_length=255)] = Field(
        None,
        description="Nouveau titre du livre (1-255 caractères)",
        example="Le Petit Prince - Édition Spéciale"
    )
    
    category: Optional[constr(max_length=100)] = Field(
        None,
        description="Nouvelle catégorie du livre (max 100 caractères)",
        example="Littérature classique"
    )
    
    price: Optional[float] = Field(
        None,
        ge=0.0,
        le=10000.0,
        description="Nouveau prix du livre en euros (0-10 000€)",
        example=24.99
    )
    
    stock: Optional[int] = Field(
        None,
        ge=0,
        le=1_000_000,
        description="Nouvelle quantité en stock (0-1 000 000)",
        example=15
    )
    
    rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Nouvelle note moyenne du livre (0.0-5.0)",
        example=4.8
    )
    
    url: Optional[HttpUrl] = Field(
        None,
        description="Nouvelle URL de la page du livre",
        example="https://example.com/le-petit-prince-special"
    )
    
    # Définir les validateurs directement dans la classe
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            # Supprimer les espaces superflus
            v = ' '.join(v.strip().split())
            
            # Vérifier que le titre contient des caractères alphanumériques
            if not any(c.isalnum() for c in v):
                raise ValueError("Le titre doit contenir au moins un caractère alphanumérique")
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            # Arrondir à 2 décimales
            return round(v, 2)
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None:
            # Arrondir à 0.5 près (4.3 -> 4.5, 4.2 -> 4.0)
            return round(v * 2) / 2
        return v
    
    @validator('url', pre=True)
    def validate_url(cls, v):
        if v is None or v == '':
            return None
        return v


class BookSchema(BookBase):
    """
    Schéma pour la représentation complète d'un livre.
    Inclut les champs en lecture seule (id, created_at).
    """
    id: int = Field(..., description="Identifiant unique du livre", example=1)
    
    created_at: Optional[datetime] = Field(
        None,
        description="Date et heure de création de l'entrée",
        example="2023-01-01T12:00:00"
    )

    class Config:
        """Configuration Pydantic pour le schéma."""
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Le Petit Prince",
                "category": "Littérature",
                "price": 19.99,
                "stock": 10,
                "rating": 4.5,
                "url": "https://example.com/le-petit-prince",
                "created_at": "2023-01-01T12:00:00"
            }
        }
