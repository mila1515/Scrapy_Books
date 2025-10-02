"""
ItemLoaders pour le traitement des données extraites par les spiders.

Ce module contient les classes et fonctions pour nettoyer et transformer
les données brutes extraites des pages web en données structurées.
"""

from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
import re

def clean_price(value: str) -> float:
    """
    Nettoie et convertit une chaîne de prix en nombre flottant.
    
    Args:
        value: Chaîne de prix à nettoyer (ex: "£20.00")
        
    Returns:
        float: Le prix sous forme de nombre flottant, ou None si la conversion échoue
    """
    try:
        return float(value.replace("£", "").strip())
    except (ValueError, AttributeError):
        return None

def clean_stock(value) -> int:
    """
    Nettoie et normalise la valeur de stock.
    
    Args:
        value: Valeur de stock à nettoyer (peut être une chaîne, une liste ou un entier)
        
    Returns:
        int: La quantité en stock sous forme d'entier
    """
    if isinstance(value, int):
        return value
    if not value:
        return 0
    if isinstance(value, list):
        value = " ".join(str(v).strip() for v in value if v)

    value = " ".join(str(value).split())
    m = re.search(r"\((\d+)\s+available\)", value)
    if m:
        return int(m.group(1))
    if "in stock" in value.lower():
        return None
    return 0

def absolute_url(value: str, loader_context) -> str:
    """
    Convertit une URL relative en URL absolue.
    
    Args:
        value: URL relative à convertir
        loader_context: Contexte du loader contenant l'URL de base
        
    Returns:
        str: URL absolue
    """
    base_url = loader_context.get('base_url', '')
    return urljoin(base_url, value)

def clean_rating(value) -> int:
    """
    Convertit une évaluation textuelle ou numérique en note numérique.
    
    Args:
        value: Valeur d'évaluation (chaîne ou nombre)
        
    Returns:
        int: Note numérique entre 1 et 5, 0 si non trouvée
    """
    # Si la valeur est déjà un nombre, on s'assure qu'elle est entre 1 et 5
    if isinstance(value, (int, float)):
        return max(1, min(5, int(value)))
    
    # Si la valeur est une chaîne, on essaie de la convertir
    if isinstance(value, str):
        # Vérifie si c'est une note numérique
        try:
            rating = float(value)
            return max(1, min(5, int(rating)))
        except (ValueError, TypeError):
            # Si ce n'est pas un nombre, on essaie de le convertir à partir du texte
            rating_map = {
                'one': 1, 'two': 2, 'three': 3,
                'four': 4, 'five': 5,
                '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
            }
            # Nettoie la chaîne et cherche une correspondance
            value = value.lower().strip()
            for key, val in rating_map.items():
                if key in value:
                    return val
    
    # Si on n'a pas pu convertir, on retourne 0 (pas de note)
    return 0

class BookLoader(ItemLoader):
    """
    Loader pour traiter et structurer les données des livres.
    
    Ce loader applique différents processeurs pour nettoyer et formater
    les champs des livres extraits par les spiders.
    """
    
    # Processeur par défaut pour tous les champs
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    
    # Processeurs spécifiques pour chaque champ
    price_in = MapCompose(clean_price)      # Nettoie le prix
    stock_in = MapCompose(clean_stock)      # Nettoie la quantité en stock
    url_in = MapCompose(absolute_url)       # Convertit les URLs relatives en absolues
    rating_in = MapCompose(clean_rating)    # Convertit l'évaluation textuelle en note numérique
