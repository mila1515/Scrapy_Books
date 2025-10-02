"""
Définition des items pour le projet de scraping de livres.

Ce module contient les classes d'items qui définissent la structure des données
récupérées lors du scraping. Chaque champ représente une propriété d'un livre.

Le module utilise la classe `scrapy.Item` pour définir un schéma de données
qui sera utilisé pour collecter, valider et traiter les informations extraites
des pages web. Chaque champ est défini comme une instance de `scrapy.Field()`.

Exemple d'utilisation :
    >>> book = BookItem(
    ...     title="Example Book",
    ...     price="19.99",
    ...     rating="4.5",
    ...     category="Fiction",
    ...     stock="5",
    ...     url="http://example.com/books/1"
    ... )
    >>> print(book['title'])
    Example Book

Pour plus d'informations sur les items dans Scrapy, consultez la documentation :
https://docs.scrapy.org/en/latest/topics/items.html
"""

# Bibliothèques standards
import re
from datetime import datetime

# Bibliothèques tierces
import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags, strip_html5_whitespace

def clean_price(value):
    """
    Nettoie et formate le prix du livre.
    
    Args:
        value (str): Prix brut extrait de la page web
        
    Returns:
        float: Prix numérique nettoyé ou None si invalide
    """
    if not value:
        return None
        
    # Supprime les caractères non numériques sauf le point décimal
    try:
        price_str = re.sub(r'[^\d.,]', '', str(value))
        # Remplace la virgule par un point si nécessaire
        price_str = price_str.replace(',', '.')
        return float(price_str)
    except (ValueError, TypeError):
        return None

def clean_rating(value):
    """
    Convertit la notation textuelle en valeur numérique.
    
    Args:
        value (str): Classe CSS de la notation (ex: 'star-rating Three')
        
    Returns:
        int: Note sur 5 ou None si invalide
    """
    if not value:
        return None
        
    rating_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5
    }
    
    for key, val in rating_map.items():
        if key in value.lower():
            return val
    return None

def clean_stock(value):
    """
    Extrait le nombre d'articles en stock à partir du texte.
    
    Args:
        value (str): Texte de disponibilité (ex: 'In stock (5 available)')
        
    Returns:
        int: Nombre d'articles en stock ou -1 si illimité/inconnu
    """
    if not value:
        return -1
        
    match = re.search(r'(\d+)', str(value))
    return int(match.group(1)) if match else -1

def clean_text(text):
    """
    Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux.
    
    Args:
        text (str): Texte à nettoyer
        
    Returns:
        str: Texte nettoyé ou None si vide
    """
    if not text:
        return None
    
    # Supprime les balises HTML et les espaces superflus
    text = str(text).strip()
    text = ' '.join(text.split())  # Supprime les espaces multiples
    return text if text else None

class BookItem(scrapy.Item):
    """
    Classe représentant un livre extrait lors du scraping.
    
    Cette classe définit la structure des données pour chaque livre extrait.
    Chaque champ est associé à des processeurs d'entrée/sortie pour nettoyer
    et valider les données lors de leur extraction.
    
    Attributes:
        title (str): Titre du livre (obligatoire)
        price (float): Prix du livre en nombre décimal
        rating (int): Note sur 5 étoiles (1-5)
        category (str): Catégorie du livre
        stock (int): Nombre d'articles disponibles (-1 si inconnu)
        url (str): URL absolue de la page du livre (obligatoire)
        description (str): Description détaillée du livre
        upc (str): Code produit universel
        product_type (str): Type de produit (ex: 'Books')
        price_excl_tax (float): Prix hors taxes
        price_incl_tax (float): Prix TTC
        tax (float): Montant de la TVA
        number_of_reviews (int): Nombre d'avis clients
        image_urls (list): Liste des URLs des images du livre
        images (list): Métadonnées des images téléchargées
        created_at (str): Date de création de l'entrée
        updated_at (str): Date de mise à jour de l'entrée
    """
    # Champs de base
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst()
    )
    
    rating = scrapy.Field(
        input_processor=MapCompose(clean_rating),
        output_processor=TakeFirst()
    )
    
    category = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    stock = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_stock),
        output_processor=TakeFirst(),
        default=-1
    )
    
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    # Champs détaillés (optionnels)
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text, str.strip),
        output_processor=Join(' ')
    )
    
    upc = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    product_type = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    price_excl_tax = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst()
    )
    
    price_incl_tax = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst()
    )
    
    tax = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst()
    )
    
    number_of_reviews = scrapy.Field(
        input_processor=MapCompose(int),
        output_processor=TakeFirst()
    )
    
    # Champs pour les images
    image_urls = scrapy.Field(
        default=[]
    )
    
    images = scrapy.Field(
        default=[]
    )
    
    # Métadonnées
    created_at = scrapy.Field(
        default=datetime.utcnow().isoformat()
    )
    
    updated_at = scrapy.Field(
        default=datetime.utcnow().isoformat()
    )
    
    def __repr__(self):
        """Représentation lisible de l'item pour le débogage."""
        return f"<BookItem: {self.get('title', 'Untitled')}>"
    
    def to_dict(self):
        """Convertit l'item en dictionnaire Python."""
        return dict(self)
    
    def validate(self):
        """Valide que les champs obligatoires sont présents."""
        required_fields = ['title', 'url']
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            raise ValueError(f"Champs obligatoires manquants: {', '.join(missing)}")
        return True
