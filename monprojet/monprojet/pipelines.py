import re
import sqlite3
import scrapy
from datetime import datetime


class CleanPipeline:
    """Pipeline de nettoyage (laissé pour compatibilité)"""
    def process_item(self, item, spider):
        # Le nettoyage est maintenant géré par l'ItemLoader
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
                url TEXT UNIQUE,
                created_at TEXT
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        # Si le stock est None, on met -1 pour signaler qu'il y a un problème
        stock = item.get('stock')
        if stock is None:
            stock = -1
            spider.logger.warning(f"Stock introuvable pour {item.get('title')}")

        created_at = datetime.now().isoformat(timespec="seconds")

        try:
            self.cur.execute(
                '''
                INSERT OR IGNORE INTO books 
                (title, price, rating, category, stock, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    item.get('title'),
                    item.get('price'),
                    item.get('rating'),
                    item.get('category'),
                    stock,
                    item.get('url'),
                    created_at
                )
            )
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur SQLite: {e}")
        return item

    def close_spider(self, spider):
        self.conn.close()
