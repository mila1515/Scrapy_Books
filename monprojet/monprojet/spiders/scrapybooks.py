"""
Spider Scrapy pour l'extraction de données de livres depuis books.toscrape.com

Ce module contient la définition du spider principal qui parcourt le site books.toscrape.com,
extrait les informations des livres et les structure selon le modèle défini dans items.py.

Le spider implémente un processus en deux étapes :
1. Parcours large (broad crawl) : exploration des pages de catalogue pour collecter les URLs des livres
2. Parcours profond (deep crawl) : extraction détaillée des informations de chaque livre

Fonctionnalités clés :
- Gestion automatique de la pagination
- Extraction robuste des données avec gestion des erreurs
- Respect des règles de politesse (délais entre requêtes)
- Nettoyage et validation des données extraites
- Journalisation détaillée pour le débogage

Exemple d'utilisation :
    scrapy crawl scrapybooks -a category=fiction -o livres.json
"""

# Bibliothèques standards
import re

# Bibliothèques Scrapy
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin

# Import des composants du projet
from monprojet.items import BookItem
from monprojet.itemloaders import BookLoader

class ScrapybooksSpider(scrapy.Spider):
    """
    Spider principal pour l'extraction de livres depuis books.toscrape.com.
    
    Ce spider implémente un processus de scraping en deux phases :
    1. Parcours des pages de catalogue pour collecter les URLs des livres
    2. Extraction détaillée des informations de chaque livre
    
    Configuration :
    - Gestion automatique de la pagination
    - Extraction robuste avec gestion des erreurs
    - Respect des règles de politesse (délais entre requêtes)
    - Nettoyage et validation des données
    
    Attributs de classe :
        name (str): Identifiant unique du spider (utilisé avec 'scrapy crawl')
        allowed_domains (list): Domaines autorisés pour le scraping
        start_urls (list): URL(s) de départ pour le scraping
        custom_settings (dict): Configuration spécifique au spider
    
    Méthodes publiques :
        parse: Traite une page de catalogue et extrait les liens vers les pages de détail
        parse_book_details: Extrait les informations détaillées d'un livre
        parse_next_page: Gère la pagination en suivant le lien vers la page suivante
    """
    
    # Identifiant unique du spider (utilisé avec la commande scrapy crawl)
    name = "scrapybooks"
    
    # Domaines autorisés pour le scraping
    allowed_domains = ["books.toscrape.com"]
    
    # URL de départ pour le scraping (première page du catalogue)
    start_urls = ["http://books.toscrape.com/catalogue/page-1.html"]
    
    def __init__(self, *args, **kwargs):
        super(ScrapybooksSpider, self).__init__(*args, **kwargs)
        self.logger.info("Spider initialisé: %s", self.name)
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ScrapybooksSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        self.logger.info('Spider opened: %s', spider.name)
    
    def spider_closed(self, spider):
        self.logger.info('Spider closed: %s', spider.name)
    
    def start_requests(self):
        """
        Cette méthode est appelée par Scrapy pour créer les requêtes initiales.
        """
        self.logger.info('Starting spider with start_urls: %s', self.start_urls)
        for url in self.start_urls:
            self.logger.info('Yielding request for URL: %s', url)
            yield scrapy.Request(
                url=url, 
                callback=self.parse, 
                dont_filter=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                }
            )
    
    # Configuration spécifique du spider
    custom_settings = {
        'CONCURRENT_REQUISITIONS': 4,  # Nombre de requêtes simultanées
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,  # Limite par domaine
        'DOWNLOAD_DELAY': 1.5,  # Délai entre les requêtes (en secondes)
        'AUTOTHROTTLE_ENABLED': True,  # Active le réglage automatique du débit
        'AUTOTHROTTLE_START_DELAY': 1.0,  # Délai initial entre les requêtes
        'AUTOTHROTTLE_MAX_DELAY': 5.0,  # Délai maximum entre les requêtes
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Nombre moyen de requêtes simultanées
        'HTTPCACHE_ENABLED': True,  # Activation du cache HTTP
        'HTTPCACHE_EXPIRATION_SECS': 86400,  # Durée de vie du cache (1 jour)
        'ITEM_PIPELINES': {
            'monprojet.pipelines.CleanPipeline': 100,
            'monprojet.pipelines.SQLitePipeline': 300,
        },
        'LOG_LEVEL': 'INFO',  # Niveau de journalisation par défaut
        'FEED_EXPORT_ENCODING': 'utf-8',  # Encodage pour l'export des données
    }
    
    def __init__(self, category=None, *args, **kwargs):
        """
        Initialise le spider avec des paramètres optionnels.
        
        Args:
            category (str, optional): Catégorie spécifique à scraper. Si None, toutes les catégories sont traitées.
            *args: Arguments positionnels supplémentaires
            **kwargs: Arguments nommés supplémentaires
        """
        super(ScrapybooksSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.logger.info(f"Initialisation du spider pour la catégorie: {category or 'toutes'}")

    def parse(self, response):
        """
        Traite une page de catalogue et extrait les liens vers les pages de détail des livres.
        
        Cette méthode est le point d'entrée principal du spider. Elle est appelée pour chaque
        réponse reçue pour les URLs de départ. Elle extrait les informations de base des livres
        depuis la vue en liste et génère des requêtes pour les pages de détail de chaque livre.
        
        Args:
            response (scrapy.http.Response): Objet Response contenant le contenu HTML de la page
            
        Yields:
            scrapy.Request: Requêtes pour les pages de détail des livres
            
        Notes:
            - Utilise BookLoader pour une extraction et un nettoyage cohérents des données
            - Transmet le loader via le meta pour conserver les données entre les requêtes
            - Gère automatiquement les erreurs de requête via le système de middleware de Scrapy
        """
        self.logger.info(f"Traitement de la page de catalogue: {response.url}")
        
        # Extraction de la catégorie depuis l'URL ou le breadcrumb
        category = self._extract_category(response)
        
        # Si une catégorie spécifique est demandée et ne correspond pas, on ignore la page
        if self.category and self.category.lower() != category.lower():
            self.logger.debug(f"Page ignorée (catégorie: {category} ne correspond pas à {self.category}")
            return
            
        # Affichage des 1000 premiers caractères de la réponse pour le débogage
        self.logger.debug(f"Contenu de la réponse (1000 premiers caractères): {response.text[:1000]}")
        
        # Compteur pour le suivi des performances
        book_count = 0
        
        # Extraction de tous les blocs de livres sur la page
        for bloc in response.css('article.product_pod'):
            book_count += 1
            
            try:
                # Création d'un BookLoader pour traiter les données du livre
                loader = BookLoader(item=BookItem(), selector=bloc, response=response)
                
                # Ajout de la catégorie extraite
                loader.add_value('category', category)
                
                # Extraction des champs de base depuis la vue en liste
                loader.add_css('title', 'h3 a::attr(title)')
                loader.add_css('price', 'p.price_color::text')
                loader.add_css('rating', 'p.star-rating::attr(class)')
                
                # Construction de l'URL absolue vers la page de détail du livre
                book_url = response.urljoin(bloc.css('h3 a::attr(href)').get())
                loader.add_value('url', book_url)
                
                # Génération d'une requête pour la page de détail du livre
                request = scrapy.Request(
                    url=book_url,
                    callback=self.parse_book_details,
                    meta={'loader': loader, 'category': category},
                    errback=self.handle_error
                )
                
                # Ajout d'un délai de politesse entre les requêtes
                yield request
                
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du livre {book_count}: {str(e)}")
                continue
        
        # Gestion de la pagination pour la page suivante
        yield from self.parse_next_page(response)
        
        # Journalisation des statistiques
        self.logger.info(f"Traitement terminé pour la page: {response.url} - {book_count} livres traités")
        
    def _extract_category(self, response):
        """
        Extrait la catégorie de la page à partir de l'URL ou du breadcrumb.
        
        Args:
            response (scrapy.http.Response): La réponse HTTP de la page
            
        Returns:
            str: Le nom de la catégorie ou 'uncategorized' si non trouvé
        """
        # Essayer d'extraire de l'URL d'abord
        url_parts = response.url.split('/')
        if 'category' in url_parts:
            cat_index = url_parts.index('category') + 1
            if cat_index < len(url_parts):
                category = url_parts[cat_index].split('_')[0]  # Enlève le numéro de page
                self.logger.debug(f"Catégorie extraite de l'URL: {category}")
                return category
        
        # Essayer d'extraire du breadcrumb
        breadcrumb = response.css('.breadcrumb li a::text').getall()
        self.logger.debug(f"Breadcrumb trouvé: {breadcrumb}")
        
        if len(breadcrumb) > 1:  # Home > Catégorie
            category = breadcrumb[1].strip()
            self.logger.debug(f"Catégorie extraite du breadcrumb: {category}")
            return category
            
        # Essayer avec un autre sélecteur si le premier ne fonctionne pas
        alt_category = response.css('.page-header.action h1::text').get()
        if alt_category:
            alt_category = alt_category.strip()
            self.logger.debug(f"Catégorie alternative trouvée: {alt_category}")
            return alt_category
            
        self.logger.warning("Aucune catégorie trouvée, utilisation de 'uncategorized'")
        return 'uncategorized'
            
            # On suit le lien vers la page détaillée pour récupérer le stock et la catégorie
    def parse_book_details(self, response):
        """
        Extrait les informations détaillées d'un livre à partir de sa page de détail.
        
        Cette méthode est appelée en callback après avoir extrait les informations
        de base depuis la vue en liste. Elle complète l'item avec des informations
        supplémentaires disponibles uniquement sur la page de détail du livre.
        
        Args:
            response (scrapy.http.Response): La réponse HTTP de la page de détail du livre
            
        Yields:
            BookItem: Un dictionnaire contenant toutes les informations du livre
            
        Notes:
            - Utilise le loader passé dans le meta de la requête
            - Gère les champs optionnels avec des valeurs par défaut appropriées
            - Nettoie et formate les données avant de les ajouter à l'item
        """
        # Journalisation pour le suivi
        self.logger.debug(f"Traitement de la page de détail: {response.url}")
        
        # Récupération du loader initialisé dans la méthode parse()
        loader = response.meta['loader']
        
        try:
            # Extraction de la description du livre
            description = response.css('#product_description + p::text').get()
            if description:
                loader.add_value('description', description.strip())
            
            # Extraction des informations techniques (tableau des détails du produit)
            product_details = {}
            rows = response.css('table.table.table-striped tr')
            for row in rows:
                key = row.css('th::text').get()
                value = row.css('td::text').get()
                if key and value:
                    product_details[key.strip().lower()] = value.strip()
            
            # Ajout des détails techniques à l'item
            field_mapping = {
                'upc': 'upc',
                'product type': 'product_type',
                'price (excl. tax)': 'price_excl_tax',
                'price (incl. tax)': 'price_incl_tax',
                'tax': 'tax',
                'number of reviews': 'number_of_reviews'
            }
            
            for field, target_field in field_mapping.items():
                if field in product_details:
                    loader.add_value(target_field, product_details[field])
            
            # Traitement spécial pour la disponibilité et le stock
            if 'availability' in product_details:
                stock_match = re.search(r'(\d+)', product_details['availability'])
                if stock_match:
                    loader.add_value('stock', int(stock_match.group(1)))
            
            # Extraction de la catégorie depuis le breadcrumb si non déjà défini
            if not loader.get_collected_values('category'):
                category = response.meta.get('category') or 'uncategorized'
                loader.add_value('category', category)
            
            # Extraction de l'URL de l'image de couverture
            image_url = response.css('#product_gallery img::attr(src)').get()
            if image_url:
                loader.add_value('image_urls', [response.urljoin(image_url)])
            
            # Extraction des étoiles de notation (si disponible)
            rating_class = response.css('p.star-rating::attr(class)').get()
            if rating_class:
                rating_map = {
                    'One': 1, 'Two': 2, 'Three': 3, 
                    'Four': 4, 'Five': 5
                }
                for key, value in rating_map.items():
                    if key.lower() in rating_class.lower():
                        loader.add_value('rating', value)
                        break
            
            # Journalisation du succès
            title = loader.get_output_value('title') or 'Titre inconnu'
            self.logger.debug(f"Livre traité avec succès: {title}")
            
            # Renvoi de l'item complet pour traitement par les pipelines
            yield loader.load_item()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la page {response.url}: {str(e)}")
            raise
    
    def parse_next_page(self, response):
        """
        Gère la pagination en suivant le lien vers la page suivante si elle existe.
        
        Cette méthode est appelée après avoir traité tous les livres d'une page de catalogue.
        Elle extrait le lien vers la page suivante et génère une nouvelle requête
        pour continuer le scraping de manière récursive.
        
        Args:
            response (scrapy.http.Response): La réponse HTTP de la page actuelle
            
        Yields:
            scrapy.Request: Une requête pour la page suivante du catalogue
            
        Notes:
            - Utilise response.follow() pour gérer automatiquement les URLs relatives
            - Respecte le paramètre de catégorie si spécifié
            - Inclut un délai de politesse entre les requêtes
        """
        # Recherche du lien vers la page suivante
        next_page = response.css('li.next a::attr(href)').get()
        
        if next_page:
            # Construction de l'URL absolue pour la page suivante
            next_page_url = response.urljoin(next_page)
            
            # Vérification de la catégorie si spécifiée
            if self.category:
                category = self._extract_category(response)
                if category.lower() != self.category.lower():
                    self.logger.info(f"Fin de la catégorie: {category}")
                    return
            
            # Journalisation pour le suivi
            self.logger.info(f"Passage à la page suivante: {next_page_url}")
            
            # Génération de la requête pour la page suivante
            yield response.follow(
                next_page_url, 
                callback=self.parse,
                meta={'category': self.category},
                dont_filter=True  # Important pour éviter le filtrage des doublons
            )
    
    def handle_error(self, failure):
        """
        Gère les erreurs survenues lors des requêtes HTTP.
        
        Args:
            failure (twisted.python.failure.Failure): L'échec à traiter
            
        Notes:
            - Journalise les erreurs pour le débogage
            - Peut implémenter des stratégies de nouvelle tentative
        """
        self.logger.error(f"Erreur lors de la requête: {failure.value}")
        
        # Exemple de log plus détaillé
        if failure.check(HttpError):
            # Gestion spécifique des erreurs HTTP
            response = failure.value.response
            self.logger.error(f'Erreur HTTP {response.status} sur {response.url}')
        
        # Exemple de nouvelle tentative (simplifié)
        # if failure.check(TimeoutError, TCPTimedOutError):
        #     return failure.request  # Renvoyer la requête pour une nouvelle tentative