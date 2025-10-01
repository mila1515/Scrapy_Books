import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import scrapy
from scrapy.exceptions import DropItem
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class CleanPipeline:
    """Pipeline de nettoyage des données"""
    
    def process_item(self, item, spider):
        # Nettoyage et validation des champs
        for field in item.fields:
            if field in item and item[field] is not None:
                if isinstance(item[field], str):
                    item[field] = item[field].strip()
        return item


class DuplicatesLoggerPipeline:
    """Pipeline pour détecter et logger les doublons"""
    
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        if not item.get('url'):
            raise DropItem("URL manquante dans l'item")
            
        if item['url'] in self.seen_urls:
            spider.logger.warning(f"Doublon ignoré: {item.get('title', 'Sans titre')} - {item['url']}")
            raise DropItem(f"Doublon ignoré: {item.get('title', 'Sans titre')}")
            
        self.seen_urls.add(item['url'])
        return item


class SQLitePipeline:
    """Pipeline pour stocker les données dans SQLite"""
    
    def __init__(self):
        self.conn = None
        self.cur = None
        self.batch_size = 100  # Taille du lot pour les insertions par lots
        self.batch_count = 0

    def open_spider(self, spider):
        """Initialise la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect('books.db')
            self.conn.row_factory = sqlite3.Row
            self.cur = self.conn.cursor()
            self._create_tables()
            spider.logger.info("Connexion à la base de données SQLite établie")
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur de connexion à SQLite: {e}")
            raise

    def _create_tables(self):
        """Crée les tables si elles n'existent pas"""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                rating INTEGER,
                category TEXT,
                stock INTEGER DEFAULT -1,
                url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        """Traite et enregistre un item dans la base de données"""
        if not all(item.get(field) for field in ['title', 'url']):
            raise DropItem("Champs obligatoires manquants dans l'item")

        try:
            self.cur.execute('''
                INSERT INTO books 
                (title, price, rating, category, stock, url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    price=excluded.price,
                    rating=excluded.rating,
                    category=excluded.category,
                    stock=excluded.stock,
                    updated_at=CURRENT_TIMESTAMP
            ''', (
                item.get('title'),
                item.get('price'),
                item.get('rating'),
                item.get('category'),
                item.get('stock', -1),
                item['url']
            ))
            
            self.batch_count += 1
            
            # Validation périodique pour éviter les verrous trop longs
            if self.batch_count >= self.batch_size:
                self.conn.commit()
                self.batch_count = 0
                
            return item
            
        except sqlite3.Error as e:
            self.conn.rollback()
            spider.logger.error(f"Erreur SQLite lors de l'insertion: {e}")
            raise DropItem(f"Erreur de base de données: {e}")

    def close_spider(self, spider):
        """Ferme la connexion à la base de données"""
        try:
            if self.conn:
                self.conn.commit()  # S'assure que tout est commité
                if self.cur:
                    self.cur.close()
                self.conn.close()
                spider.logger.info("Connexion à la base de données fermée")
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur lors de la fermeture de la connexion: {e}")
