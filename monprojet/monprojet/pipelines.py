import re
import sqlite3
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
import scrapy

# Load environment variables from .env file
load_dotenv()

# Configuration de la base de données PostgreSQL
SQLITE_PATH = os.getenv("SQLITE_PATH")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = int(os.getenv("PG_PORT", 5432))

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

# Pipeline pour SQLite
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
                ON CONFLICT(url) DO UPDATE SET
                    price=excluded.price,
                    rating=excluded.rating,
                    category=excluded.category,
                    stock=excluded.stock,
                    created_at=excluded.created_at
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



class PostgresPipeline:
    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD,
                host=PG_HOST,
                port=PG_PORT
            )
            self.cur = self.conn.cursor()
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    price NUMERIC,
                    rating INTEGER,
                    category TEXT,
                    stock INTEGER,
                    url TEXT UNIQUE,
                    created_at TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"Erreur PostgreSQL: {e}")
            raise scrapy.exceptions.CloseSpider("DB connection failed")

# Pipeline pour PostgreSQL
    def process_item(self, item, spider):
        # ⚡ Gestion du stock
        stock = item.get('stock')
        if stock is None:
            stock = -1
            spider.logger.warning(f"Stock introuvable pour {item.get('title')}")

        created_at = datetime.now()

        try:
            self.cur.execute(
                '''
                INSERT INTO books (title, price, rating, category, stock, url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                ON CONFLICT(url) DO UPDATE SET
                    price=excluded.price,
                    rating=excluded.rating,
                    category=excluded.category,
                    stock=excluded.stock,
                    created_at=excluded.created_at
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
        except psycopg2.Error as e:
            spider.logger.error(f"Erreur PostgreSQL: {e}")
        return item

    def close_spider(self, spider):
        self.conn.close()
        self.cur.close() 