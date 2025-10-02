"""
Pipelines de traitement des données du projet de scraping de livres.

Ce module contient les pipelines qui traitent les données après leur extraction par les spiders.
Les pipelines sont exécutés dans l'ordre défini dans settings.py et effectuent des opérations telles que :
- Nettoyage et validation des données
- Détection et gestion des doublons
- Stockage structuré dans une base de données SQLite
- Journalisation des opérations

L'ordre d'exécution des pipelines est important et est défini dans la variable ITEM_PIPELINES du fichier settings.py.
"""

# Bibliothèques standards
import sqlite3
from datetime import datetime
import logging
import os

# Bibliothèques tierces
from dotenv import load_dotenv
import scrapy
from scrapy.exceptions import DropItem

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Chemin par défaut de la base de données SQLite
DEFAULT_DB_PATH = 'books.db'

class CleanPipeline:
    """
    Pipeline de nettoyage et de validation des données extraites.
    
    Ce pipeline effectue les opérations suivantes :
    - Suppression des espaces superflus dans les chaînes de caractères
    - Conversion des types de données
    - Validation des champs obligatoires
    - Formatage cohérent des données
    """
    
    def process_item(self, item, spider):
        """
        Traite un item en appliquant les opérations de nettoyage.
        
        Args:
            item (dict): L'item à nettoyer
            spider (scrapy.Spider): L'instance du spider qui a généré l'item
            
        Returns:
            dict: L'item nettoyé et validé
            
        Raises:
            DropItem: Si l'item ne passe pas la validation
        """
        # Journalisation du traitement de l'item
        logger.debug(f"Nettoyage de l'item: {item.get('title', 'Sans titre')}")
        
        # Nettoyage et validation des champs
        for field in item.fields:
            if field in item and item[field] is not None:
                # Nettoyage des chaînes de caractères
                if isinstance(item[field], str):
                    item[field] = item[field].strip()
                    
                    # Conversion des chaînes vides en None
                    if item[field] == '':
                        item[field] = None
                
                # Conversion des nombres
                elif field in ['price', 'rating'] and item[field]:
                    try:
                        item[field] = float(item[field])
                    except (ValueError, TypeError):
                        item[field] = None
                        logger.warning(f"Impossible de convertir {field}: {item[field]}")
        
        # Validation des champs obligatoires
        required_fields = ['title', 'url']
        for field in required_fields:
            if not item.get(field):
                logger.warning(f"Champ obligatoire manquant: {field} dans {item}")
                raise DropItem(f"Champ obligatoire manquant: {field}")
        return item


class SQLitePipeline:
    """
    Pipeline pour le stockage des données dans une base de données SQLite.
    
    Ce pipeline gère :
    - La connexion à la base de données SQLite
    - La création des tables si elles n'existent pas
    - L'insertion par lots pour optimiser les performances
    - La gestion des transactions pour assurer l'intégrité des données
    
    La configuration de la base de données peut être personnalisée via les variables d'environnement.
    """
    
    def __init__(self):
        """Initialise le pipeline avec les paramètres par défaut."""
        # Connexion à la base de données (sera initialisée dans open_spider)
        self.conn = None
        self.cur = None
        
        # Configuration du traitement par lots
        self.batch_size = 100  # Nombre d'items à insérer en une seule transaction
        self.batch_count = 0   # Compteur d'items dans le lot actuel
        
        # Chemin de la base de données (peut être remplacé par une variable d'environnement)
        self.db_path = os.getenv('SQLITE_DB_PATH', DEFAULT_DB_PATH)
        
        logger.info(f"Initialisation du pipeline SQLite (base de données: {self.db_path})")

    def open_spider(self, spider):
        """
        Méthode appelée lors de l'ouverture du spider.
        
        Établit la connexion à la base de données SQLite et initialise les tables.
        
        Args:
            spider (scrapy.Spider): L'instance du spider en cours d'exécution
            
        Raises:
            sqlite3.Error: En cas d'échec de la connexion à la base de données
        """
        try:
            # Établissement de la connexion à la base de données
            self.conn = sqlite3.connect(self.db_path)
            # Configuration pour récupérer les résultats sous forme de dictionnaire
            self.conn.row_factory = sqlite3.Row
            self.cur = self.conn.cursor()
            
            # Création des tables si elles n'existent pas
            self._create_tables()
            
            # Journalisation du succès de la connexion
            spider.logger.info(f"Connexion à la base de données SQLite établie: {self.db_path}")
            
            # Initialisation des statistiques
            spider.crawler.stats.set_value('items_processed', 0)
            spider.crawler.stats.set_value('database_errors', 0)
            
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur de connexion à SQLite: {e}")
            spider.crawler.stats.inc_value('database_errors')
            raise

    def _create_tables(self):
        """
        Crée les tables de la base de données si elles n'existent pas.
        
        Cette méthode est appelée automatiquement lors de l'initialisation du pipeline.
        Elle crée la structure de la base de données avec les contraintes nécessaires.
        """
        try:
            # Création de la table des livres
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    -- Identifiant unique auto-incrémenté
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- Informations de base du livre
                    title TEXT NOT NULL,
                    price REAL,
                    rating INTEGER,
                    category TEXT,
                    
                    -- Gestion du stock (-1 = inconnu)
                    stock INTEGER DEFAULT -1,
                    
                    -- URL unique du livre (clé naturelle)
                    url TEXT UNIQUE NOT NULL,
                    
                    -- Métadonnées de suivi
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Création des index pour accélérer les recherches courantes
            self.cur.execute('CREATE INDEX IF NOT EXISTS idx_books_category ON books(category)')
            self.cur.execute('CREATE INDEX IF NOT EXISTS idx_books_price ON books(price)')
            self.cur.execute('CREATE INDEX IF NOT EXISTS idx_books_rating ON books(rating)')
            
            # Création d'une table pour le suivi des exécutions
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS scrapes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    items_processed INTEGER DEFAULT 0,
                    status TEXT
                )
            ''')
            
            # Validation des modifications
            self.conn.commit()
            logger.info("Structure de la base de données vérifiée/créée avec succès")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            self.conn.rollback()
            raise

    def process_item(self, item, spider):
        """
        Traite et enregistre un item dans la base de données.
        
        Cette méthode est appelée pour chaque item extrait par le spider.
        Elle gère l'insertion ou la mise à jour des données dans la base SQLite.
        
        Args:
            item (dict): L'item à enregistrer
            spider (scrapy.Spider): L'instance du spider
            
        Returns:
            dict: L'item traité
            
        Raises:
            DropItem: Si l'item est invalide ou en cas d'erreur de base de données
        """
        # Vérification des champs obligatoires
        required_fields = ['title', 'url']
        if not all(item.get(field) for field in required_fields):
            spider.logger.warning(f"Champs obligatoires manquants dans l'item: {item}")
            spider.crawler.stats.inc_value('validation_errors')
            raise DropItem("Champs obligatoires manquants dans l'item")

        try:
            # Préparation des données pour l'insertion
            data = {
                'title': item.get('title'),
                'price': float(item.get('price', 0)) if item.get('price') is not None else None,
                'rating': int(item['rating']) if item.get('rating') is not None else None,
                'category': item.get('category'),
                'stock': int(item.get('stock', -1)),
                'url': item['url']
            }
            
            # Requête d'insertion ou de mise à jour (UPSERT)
            self.cur.execute('''
                INSERT INTO books 
                (title, price, rating, category, stock, url)
                VALUES (:title, :price, :rating, :category, :stock, :url)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    price = excluded.price,
                    rating = excluded.rating,
                    category = excluded.category,
                    stock = excluded.stock,
                    updated_at = CURRENT_TIMESTAMP
                WHERE excluded.updated_at > books.updated_at
                   OR books.updated_at IS NULL
            ''', data)
            
            # Mise à jour du compteur de lot
            self.batch_count += 1
            spider.crawler.stats.inc_value('items_processed')
            
            # Validation périodique pour optimiser les performances
            if self.batch_count >= self.batch_size:
                self.conn.commit()
                spider.logger.debug(f"Lot de {self.batch_count} items enregistrés")
                self.batch_count = 0
                
            # Journalisation de débogage
            if spider.settings.getbool('LOG_ITEM_PROCESSED'):
                spider.logger.debug(f"Item traité: {item['title']}")
                
            return item
            
        except (sqlite3.Error, ValueError, TypeError) as e:
            self.conn.rollback()
            error_msg = f"Erreur lors de l'enregistrement de l'item {item.get('url')}: {str(e)}"
            spider.logger.error(error_msg, exc_info=True)
            spider.crawler.stats.inc_value('database_errors')
            raise DropItem(f"Erreur de base de données: {str(e)}")

    def close_spider(self, spider):
        """
        Méthode appelée à la fermeture du spider.
        
        Effectue les opérations de nettoyage et ferme proprement la connexion à la base de données.
        
        Args:
            spider (scrapy.Spider): L'instance du spider qui se termine
        """
        try:
            if self.conn:
                # Dernier commit pour les données restantes
                if self.batch_count > 0:
                    self.conn.commit()
                    spider.logger.info(f"Dernier lot de {self.batch_count} items enregistré")
                
                # Enregistrement des statistiques de l'exécution
                stats = spider.crawler.stats.get_stats()
                has_errors = spider.crawler.stats.get_value('log_count/ERROR', 0) > 0 if spider.crawler and spider.crawler.stats else False
                self.cur.execute('''
                    INSERT INTO scrapes 
                    (end_time, items_processed, status)
                    VALUES (CURRENT_TIMESTAMP, ?, ?)
                ''', (
                    stats.get('item_scraped_count', 0),
                    'completed' if not has_errors else 'completed_with_errors'
                ))
                
                # Fermeture des ressources
                self.conn.commit()
                if self.cur:
                    self.cur.close()
                self.conn.close()
                
                # Journalisation des statistiques finales
                duration = stats.get('elapsed_time_seconds', 0)
                items_processed = stats.get('item_scraped_count', 0)
                items_per_second = items_processed / duration if duration > 0 else 0
                
                spider.logger.info(
                    f"Scraping terminé. "
                    f"Items traités: {items_processed} "
                    f"en {duration:.2f} secondes "
                    f"({items_per_second:.2f} items/sec)"
                )
                
        except sqlite3.Error as e:
            spider.logger.error(f"Erreur lors de la fermeture de la connexion: {e}", exc_info=True)
            spider.crawler.stats.inc_value('database_errors')
            
        except Exception as e:
            spider.logger.error(f"Erreur inattendue lors de la fermeture du spider: {e}", exc_info=True)
