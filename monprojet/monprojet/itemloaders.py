from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
import re

# --- Fonctions de nettoyage et conversion ---

def clean_price(value: str):
    """Supprime le symbole £ et convertit en float"""
    try:
        return float(value.replace("£", "").strip())
    except ValueError:
        return None



def clean_stock(value):
    """
    Extrait le nombre exact entre parenthèses.
    Exemple : "In stock (19 available)" -> 19
    """
    # Si c'est déjà un entier, on le retourne directement
    if isinstance(value, int):
        return value
        
    if not value:
        return 0
    
    # Si c'est une liste, on la convertit en chaîne
    if isinstance(value, list):
        value = ' '.join(str(v).strip() for v in value if v)
    
    # Si c'est déjà un nombre, on le retourne
    if isinstance(value, (int, float)):
        return int(value)
        
    # On nettoie les espaces et retours à la ligne
    value = ' '.join(str(value).split())
    
    # Recherche du motif (X available)
    m = re.search(r'\((\d+)\s+available\)', value)
    if m:
        return int(m.group(1))
    
    # Si on ne trouve pas de nombre, on vérifie si c'est "In stock"
    if 'in stock' in value.lower():
        return 1  # On retourne 1 par défaut si c'est juste "In stock"
    
    return 0  # Par défaut, on retourne 0


def absolute_url(value: str, loader_context):
    """Transforme une URL relative en URL absolue"""
    response = loader_context.get('response')
    if response:
        return response.urljoin(value)
    return urljoin("http://books.toscrape.com/", value)

def clean_rating(value: str):
    """Transforme 'star-rating Three' en int (3)"""
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    parts = value.split()
    if parts:
        return rating_map.get(parts[-1], None)
    return None

# # --- Item Loader ---
# class BookLoader(ItemLoader):
#     default_output_processor = TakeFirst()
    
#     # nettoyage spécifique par champ
#     price_in = MapCompose(clean_price)
#     stock_in = MapCompose(clean_stock)
#     url_in = MapCompose(absolute_url)
#     rating_in = MapCompose(clean_rating)




class BookLoader(ItemLoader):
    default_output_processor = TakeFirst()

    # Nettoyage
    price_in = MapCompose(lambda x: float(x.replace("£", "").strip()))

    # ⚡ Mise à jour pour stock : on strip et on applique clean_stock
    stock_in = MapCompose(clean_stock)
    url_in = MapCompose(lambda x, loader_context: loader_context['response'].urljoin(x))
    rating_in = MapCompose(lambda x: {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}.get(x.split()[-1], None))


