# pipelines.py
import re
import sqlite3
import scrapy

class CleanPipeline:
    """Nettoie price -> float, rating -> int, stock -> int"""
    def process_item(self, item, spider):
        # price "£51.77" -> 51.77
        price = item.get('price')
        if price:
            cleaned = re.sub(r'[^\d.]', '', price)
            try:
                item['price'] = float(cleaned)
            except ValueError:
                item['price'] = None

        # rating (ex: 'Three') -> 3
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        rating = item.get('rating')
        if rating:
            item['rating'] = rating_map.get(rating, None)

        # stock : si disponible
        stock = item.get('stock')
        if stock:
            m = re.search(r'(\d+)', stock)
            item['stock'] = int(m.group(1)) if m else 0

        return item


class DuplicatesLoggerPipeline:
    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.seen:
            spider.logger.info(f"Doublon ignoré: {item['title']}")
            raise scrapy.exceptions.DropItem(f"Doublon ignoré: {item['title']}")
        else:
            self.seen.add(item['url'])
            return item


class SQLitePipeline:
    """Insère les items nettoyés dans SQLite et ignore les doublons sur l'URL"""
    def open_spider(self, spider):
        self.conn = sqlite3.connect('books.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                price REAL,
                rating INTEGER,
                category TEXT,
                stock INTEGER,
                url TEXT UNIQUE
            )
        ''')  # Ajout de UNIQUE sur URL
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            self.cur.execute(
                'INSERT OR IGNORE INTO books (title, price, rating, category, stock, url) VALUES (?,?,?,?,?,?)',
                (
                    item.get('title'),
                    item.get('price'),
                    item.get('rating'),
                    item.get('category'),
                    item.get('stock', 0),
                    item.get('url')
                )
            )
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur SQLite: {e}")
        return item

    def close_spider(self, spider):
        self.conn.close()
