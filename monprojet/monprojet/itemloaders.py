from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
import re

def clean_price(value: str):
    try:
        return float(value.replace("£", "").strip())
    except ValueError:
        return None

def clean_stock(value):
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

def absolute_url(value: str, loader_context):
    response = loader_context.get("response")
    if response:
        return response.urljoin(value)
    return urljoin("http://books.toscrape.com/", value)

def clean_rating(value: str):
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    parts = value.split()
    if parts:
        return rating_map.get(parts[-1], None)
    return None

class BookLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    price_in = MapCompose(clean_price)
    stock_in = MapCompose(clean_stock)
    url_in = MapCompose(absolute_url)
    rating_in = MapCompose(clean_rating)
