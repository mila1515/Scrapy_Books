"""
Middlewares personnalisés pour le projet de scraping de livres.

Ce module implémente des middlewares personnalisés pour le spider Scrapy qui permettent de :
- Gérer et faire tourner les en-têtes HTTP (User-Agent)
- Gérer les erreurs de requête et de réponse
- Implémenter une logique personnalisée avant/après le traitement des requêtes
- Journaliser les événements importants

Les middlewares sont des composants clés de l'architecture de Scrapy qui permettent
d'intervenir à différents stades du cycle de vie d'une requête/réponse.

Pour plus d'informations sur les middlewares Scrapy, consultez la documentation :
https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

import random
from typing import Any, AsyncIterable, Iterable, Optional, Union

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.crawler import Crawler
from scrapy.spiders import Spider

# =============================================================================
# CONFIGURATION
# =============================================================================

# Liste des user-agents pour la rotation
# Ces user-agents sont utilisés pour éviter d'être bloqué par le serveur cible
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class MonprojetSpiderMiddleware:
    """
    Middleware de niveau spider pour le projet de scraping de livres.
    
    Ce middleware intervient dans le traitement des réponses et des items
    après qu'ils aient été traités par le spider. Il permet de :
    - Intercepter et modifier les réponses avant qu'elles n'atteignent le spider
    - Traiter les exceptions levées par le spider
    - Modifier les items générés par le spider avant qu'ils ne soient traités
    - Exécuter du code au démarrage du spider
    
    Le cycle de vie d'une requête à travers ce middleware est le suivant :
    1. spider_opened() - Appelé lors du démarrage du spider
    2. process_spider_input() - Pour chaque réponse reçue
    3. Le spider traite la réponse
    4. process_spider_output() - Pour chaque item/requête généré par le spider
    5. En cas d'erreur : process_spider_exception() est appelé
    
    Attributs:
        logger: Un logger pour enregistrer les événements importants
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'MonprojetSpiderMiddleware':
        """
        Méthode de fabrique utilisée par Scrapy pour créer une instance du middleware.
        
        Args:
            crawler: L'instance du crawler Scrapy
            
        Returns:
            Une instance du middleware configurée
        """
        instance = cls()
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        return instance

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        """
        Appelé pour chaque réponse traitée par le spider.
        
        Args:
            response: La réponse HTTP reçue
            spider: L'instance du spider qui traite la réponse
            
        Returns:
            None si le traitement doit continuer, ou lève une exception en cas d'erreur
        """
        # Ici, on pourrait ajouter une logique pour pré-traiter les réponses
        # avant qu'elles n'atteignent le spider
        return None

    def process_spider_output(self, response: Response, result: Iterable[Any], 
                            spider: Spider) -> Iterable[Any]:
        """
        Traite les résultats (items ou requêtes) générés par le spider.
        
        Args:
            response: La réponse qui a généré ces résultats
            result: Itérable d'items ou de requêtes
            spider: L'instance du spider qui a généré ces résultats
            
        Yields:
            Les items ou requêtes à traiter par les étapes suivantes
        """
        for item in result:
            # Ici, on pourrait modifier les items avant qu'ils ne soient traités
            # par les pipelines
            yield item

    def process_spider_exception(self, response: Response, exception: Exception, 
                               spider: Spider) -> Optional[Iterable[Any]]:
        """
        Gère les exceptions levées par le spider ou d'autres middlewares.
        
        Args:
            response: La réponse en cours de traitement lors de l'erreur
            exception: L'exception qui a été levée
            spider: L'instance du spider qui a généré l'erreur
            
        Returns:
            None pour continuer le traitement normal des erreurs, ou un itérable
            d'items/requêtes pour reprendre le traitement
        """
        spider.logger.error(f"Erreur lors du traitement de {response.url}: {exception}", 
                          exc_info=True)
        return None

    async def process_start(self, start: AsyncIterable[Any]) -> AsyncIterable[Any]:
        """
        Traite les requêtes initiales du spider de manière asynchrone.
        
        Args:
            start: Itérable asynchrone des requêtes initiales
            
        Yields:
            Les requêtes initiales potentiellement modifiées
        """
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider: Spider) -> None:
        """
        Appelé lors de l'ouverture du spider.
        
        Args:
            spider: L'instance du spider qui démarre
        """
        spider.logger.info(f"Spider démarré: {spider.name}")


class BrotliMiddleware:
    """
    Middleware pour gérer la décompression Brotli des réponses HTTP.
    
    Ce middleware décompresse les réponses qui utilisent l'encodage 'br' (Brotli)
    avant qu'elles ne soient traitées par les autres middlewares ou par le spider.
    """
    
    def __init__(self):
        # Import brotli une seule fois lors de l'initialisation
        import brotli
        self.brotli = brotli
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def process_response(self, request, response, spider):
        """
        Traite la réponse HTTP pour décompresser le contenu si nécessaire.
        
        Args:
            request: La requête qui a généré cette réponse
            response: La réponse HTTP à traiter
            spider: L'instance du spider
            
        Returns:
            La réponse traitée (avec décompression si nécessaire)
        """
        # Vérifie si la réponse est compressée avec Brotli
        content_encoding = response.headers.get('Content-Encoding', b'').decode('utf-8').lower()
        
        if 'br' in content_encoding:
            try:
                # Décompresse le contenu
                decompressed_body = self.brotli.decompress(response.body)
                
                # Crée un nouveau dictionnaire d'en-têtes sans l'encodage Brotli
                headers = dict(response.headers)
                if 'content-encoding' in headers:
                    del headers['content-encoding']
                if 'Content-Encoding' in headers:
                    del headers['Content-Encoding']
                
                # Met à jour la réponse avec le contenu décompressé
                response = response.replace(
                    body=decompressed_body,
                    headers=headers
                )
                
                spider.logger.debug("Réponse décompressée avec succès (Brotli)")
                
            except Exception as e:
                spider.logger.error(f"Erreur lors de la décompression Brotli: {e}")
                spider.logger.debug(f"Headers de la réponse: {dict(response.headers)}")
                spider.logger.debug(f"Taille du corps: {len(response.body) if response.body else 0} octets")
        
        return response


class MonprojetDownloaderMiddleware:
    """
    Middleware pour le téléchargement des pages.
    
    Ce middleware intervient dans le processus de téléchargement des pages et permet de :
    - Modifier les requêtes avant leur envoi (ex: rotation des User-Agents)
    - Intercepter et modifier les réponses reçues
    - Gérer les erreurs de téléchargement
    - Implémenter une politique de retry personnalisée
    
    Le cycle de vie d'une requête à travers ce middleware est le suivant :
    1. process_request() - Pour chaque requête avant son envoi
    2. Si une exception se produit : process_exception() est appelé
    3. Sinon, process_response() est appelé avec la réponse reçue
    
    Attributs:
        logger: Un logger pour enregistrer les événements importants
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'MonprojetDownloaderMiddleware':
        """
        Méthode de fabrique utilisée par Scrapy pour créer une instance du middleware.
        
        Args:
            crawler: L'instance du crawler Scrapy
            
        Returns:
            Une instance du middleware configurée
        """
        instance = cls()
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        return instance

    def process_request(self, request: Request, spider: Spider) -> Optional[Any]:
        """
        Traite chaque requête avant son envoi au serveur.
        
        Cette méthode est idéale pour :
        - Modifier les en-têtes HTTP
        - Modifier les paramètres de la requête
        - Ajouter des métadonnées personnalisées
        
        Args:
            request: La requête à traiter
            spider: L'instance du spider qui a émis la requête
            
        Returns:
            - None pour continuer le traitement normal
            - Un objet Response pour court-circuiter le téléchargement
            - Un objet Request pour remplacer la requête actuelle
            - IgnoreRequest pour ignorer cette requête
        """
        # Rotation des User-Agents pour éviter le blocage
        request.headers['User-Agent'] = random.choice(USER_AGENTS)
        
        # Exemple d'ajout d'un en-tête personnalisé
        request.headers['X-Requested-With'] = 'Scrapy Book Scraper'
        
        # Journalisation du debug
        spider.logger.debug(f"Traitement de la requête: {request.url}")
        
        return None

    def process_response(self, request: Request, response: Response, 
                        spider: Spider) -> Union[Response, Request]:
        """
        Traite chaque réponse reçue du serveur.
        
        Cette méthode est idéale pour :
        - Vérifier les codes de statut HTTP
        - Détecter les pages de blocage (CAPTCHA, etc.)
        - Modifier le contenu de la réponse
        
        Args:
            request: La requête qui a généré cette réponse
            response: La réponse à traiter
            spider: L'instance du spider qui a émis la requête
            
        Returns:
            - La réponse (éventuellement modifiée) pour continuer le traitement
            - Une nouvelle requête pour rejouer la requête
            - Lève IgnoreRequest pour ignorer cette réponse
        """
        # Vérification du code de statut HTTP
        if response.status >= 400:
            spider.logger.warning(
                f"Erreur HTTP {response.status} pour {response.url}"
            )
            
        # Détection de pages de blocage (exemple simple avec contenu de la page)
        if b"blocked" in response.body.lower() or b"captcha" in response.body.lower():
            spider.logger.warning(
                f"Page de blocage détectée pour {response.url}"
            )
            # Ici, on pourrait implémenter une logique pour contourner le blocage
            
        return response

    def process_exception(self, request: Request, exception: Exception, 
                         spider: Spider) -> Optional[Union[Response, Request]]:
        """
        Gère les exceptions survenues pendant le téléchargement.
        
        Args:
            request: La requête qui a généré l'exception
            exception: L'exception qui a été levée
            spider: L'instance du spider qui a émis la requête
            
        Returns:
            - None pour continuer le traitement normal des erreurs
            - Un objet Response pour traiter l'exception comme une réponse
            - Un objet Request pour réessayer la requête
        """
        spider.logger.error(
            f"Erreur lors du téléchargement de {request.url}: {exception}",
            exc_info=True
        )
        
        # Ici, on pourrait implémenter une logique de retry personnalisée
        # ou une autre stratégie de gestion d'erreur
        
        return None

    def spider_opened(self, spider: Spider) -> None:
        """
        Appelé lors de l'ouverture du spider.
        
        Args:
            spider: L'instance du spider qui démarre
        """
        spider.logger.info(f"Téléchargeur middleware prêt pour le spider: {spider.name}")
