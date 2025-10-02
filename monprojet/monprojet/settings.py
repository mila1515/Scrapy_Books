"""
Configuration du projet Scrapy pour le scraping de livres.

Ce fichier contient les paramètres de configuration pour le projet Scrapy,
y compris les paramètres des pipelines, des middlewares, des extensions,
et d'autres options de configuration importantes.

Structure du fichier :
1. Configuration de base du projet
2. Paramètres de requête et de concurrence
3. Middlewares et extensions
4. Configuration du cache HTTP
5. Journalisation et débogage
6. Paramètres avancés
"""

import brotli

# ===============================================
# Configuration de base du projet
# ===============================================

# Nom du bot (utilisé pour le user-agent par défaut)
BOT_NAME = 'monprojet'

# Désactive la vérification des robots.txt
ROBOTSTXT_OBEY = False

# Configuration du délai entre les requêtes (en secondes)
DOWNLOAD_DELAY = 2

# Nombre maximum de requêtes simultanées
CONCURRENT_REQUESTS = 16

# Configuration du user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# ===============================================
# Configuration des middlewares
# ===============================================

# Configuration des middlewares de téléchargement
DOWNLOADER_MIDDLEWARES = {
    # Désactiver le middleware de compression HTTP par défaut de Scrapy
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': None,
    
    # Notre middleware Brotli personnalisé (priorité haute pour traiter la compression en premier)
    'monprojet.middlewares.BrotliMiddleware': 100,
    
    # Middleware par défaut de Scrapy (désactivés ou avec priorité plus basse)
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'monprojet.middlewares.MonprojetDownloaderMiddleware': 543,  # Notre middleware personnalisé
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
}

# Désactiver la compression HTTP côté client (nous gérons la décompression manuellement)
COMPRESSION_ENABLED = False

# Accepter l'encodage Brotli dans les en-têtes de requête
DOWNLOADER_CLIENT_TLS_METHOD = 'TLSv1.2'

# Configuration des en-têtes pour accepter la compression Brotli
REQUEST_HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Configuration des en-têtes par défaut
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',  # Do Not Track
}

# Désactiver le cache HTTP pour forcer le rechargement des pages
HTTPCACHE_ENABLED = False

# ===============================================
# Configuration des extensions
# ===============================================

EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 0,     # Statistiques de base
    'scrapy.extensions.memusage.MemoryUsage': 0,    # Surveillance de la mémoire
    'scrapy.extensions.memdebug.MemoryDebugger': 0,  # Débogage de la mémoire
    'scrapy.extensions.closespider.CloseSpider': 0,  # Fermeture automatique
    'scrapy.extensions.logstats.LogStats': 0,        # Statistiques de log
    'scrapy.extensions.spiderstate.SpiderState': 0,  # État du spider
    'scrapy.extensions.throttle.AutoThrottle': 0,    # Régulation automatique
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "monprojet.pipelines.MonprojetPipeline": 300,
#}

# Activation de l'extension AutoThrottle
# Ajuste automatiquement les délais entre les requêtes en fonction de la charge du serveur
AUTOTHROTTLE_ENABLED = True

# Délai initial entre les requêtes (en secondes)
AUTOTHROTTLE_START_DELAY = 1.0

# Délai maximum entre deux requêtes (en secondes)
# Même en cas de forte latence, ne pas dépasser cette valeur
AUTOTHROTTLE_MAX_DELAY = 3.0

# Nombre moyen de requêtes simultanées par domaine
# 1.0 signifie une requête à la fois
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Active l'affichage des statistiques de throttling pour chaque réponse
# Utile pour le débogage des problèmes de débit
AUTOTHROTTLE_DEBUG = False

# ===============================================
# 8. Configuration des middlewares
# ===============================================

# Middlewares de téléchargement
# L'ordre est important, les valeurs basses sont exécutées en premier
DOWNLOADER_MIDDLEWARES = {
    # Désactive le middleware par défaut (priorité 543)
    # 'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
    
    # Middleware personnalisé
    "monprojet.middlewares.MonprojetDownloaderMiddleware": 543,
    
    # Middlewares standards (activés par défaut, désactivez-les si nécessaire)
    # 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    # 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    # 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    # 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    # 'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    # 'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
}

# ===============================================
# 9. Configuration des extensions
# ===============================================

# Extensions à activer/désactiver
# EXTENSIONS = {
#     'scrapy.extensions.telnet.TelnetConsole': None,  # Désactive la console Telnet
#     'scrapy.extensions.corestats.CoreStats': 0,     # Active les statistiques de base
#     'scrapy.extensions.memusage.MemoryUsage': 0,    # Surveillance de l'utilisation de la mémoire
#     'scrapy.extensions.memdebug.MemoryDebugger': 0,  # Débogage de la mémoire
#     'scrapy.extensions.closespider.CloseSpider': 0,  # Fermeture automatique du spider
# }

# ===============================================
# 10. Configuration de l'export des données
# ===============================================

# Encodage des fichiers d'export
FEED_EXPORT_ENCODING = "utf-8"

# Format d'export par défaut (décommenter si nécessaire)
# FEED_FORMAT = 'jsonlines'
# FEED_URI = 'output/items_%(time)s.json'

# Champs à exporter (dans l'ordre spécifié)
# FEED_EXPORT_FIELDS = ['title', 'price', 'category', 'url']

# ===============================================
# 11. Configuration avancée
# ===============================================

# Désactive les cookies (activés par défaut)
# COOKIES_ENABLED = False

# Désactive la console Telnet (activée par défaut)
# TELNETCONSOLE_ENABLED = False

# En-têtes par défaut des requêtes HTTP
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',  # Do Not Track
}

# Profondeur maximale de crawling (0 pour illimité)
# DEPTH_LIMIT = 0

# Délai d'attente pour les requêtes AJAX (en secondes)
# AJAXCRAWL_ENABLED = True

# Configuration des proxies (exemple)
# HTTP_PROXY = 'http://proxy.example.com:8080'
# HTTPS_PROXY = 'http://proxy.example.com:8080'

# Activation du cache HTTP
# Utile pendant le développement pour éviter de surcharger le site cible
# À désactiver en production ou pour des données toujours fraîches
HTTPCACHE_ENABLED = False

# Durée de vie des entrées du cache (en secondes)
# 86400 secondes = 1 jour
HTTPCACHE_EXPIRATION_SECS = 86400

# Dossier de stockage du cache
HTTPCACHE_DIR = "httpcache"

# Codes HTTP à ignorer pour le cache (par défaut, on ne met pas 404 pour voir les erreurs)
HTTPCACHE_IGNORE_HTTP_CODES = []

# Classe de stockage du cache
# Par défaut, utilise le système de fichiers
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# ===============================================
# 6. Configuration de la journalisation
# ===============================================

# Niveau de journalisation (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# En développement, utiliser DEBUG pour plus d'informations
# En production, utiliser WARNING ou ERROR pour réduire les logs
LOG_LEVEL = "DEBUG"

# Fichier de log (optionnel)
# LOG_FILE = "scrapy.log"

# Format des messages de log
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# ===============================================
# 7. Configuration d'AutoThrottle
# ===============================================

# ===============================================
# 16. Configuration de l'export des données
# ===============================================

# Encodage des fichiers d'export
FEED_EXPORT_ENCODING = "utf-8"

# Format d'export par défaut (décommenter si nécessaire)
# FEED_FORMAT = 'jsonlines'
# FEED_URI = 'output/items_%(time)s.json'

# Champs à exporter (dans l'ordre spécifié)
# FEED_EXPORT_FIELDS = ['title', 'price', 'category', 'url']

# ===============================================
# 17. Configuration de la journalisation
# ===============================================

# Niveau de journalisation (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# En développement, utiliser DEBUG pour plus d'informations
# En production, utiliser WARNING ou ERROR pour réduire les logs
LOG_LEVEL = "DEBUG"

# Fichier de log (optionnel)
# LOG_FILE = "scrapy.log"

# Format des messages de log
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# ===============================================
# 18. Configuration avancée
# ===============================================

# Profondeur maximale de crawling (0 pour illimité)
# DEPTH_LIMIT = 0

# Délai d'attente pour les requêtes AJAX (en secondes)
# AJAXCRAWL_ENABLED = True

# Configuration des proxies (exemple)
# HTTP_PROXY = 'http://proxy.example.com:8080'
# HTTPS_PROXY = 'http://proxy.example.com:8080'

# Configuration de la limite de profondeur
# DEPTH_STATS_VERBOSE = True
# DEPTH_PRIORITY = 1

# Configuration de la taille maximale des réponses (en octets)
# DOWNLOAD_MAXSIZE = 1024*1024*10  # 10MB

# Configuration du timeout des requêtes (en secondes)
# DOWNLOAD_TIMEOUT = 180  # 3 minutes

# Configuration de la taille maximale des fichiers téléchargés
# DOWNLOAD_MAXSIZE = 1073741824  # 1GB
# DOWNLOAD_WARNSIZE = 33554432  # 32MB

# Configuration de la compression
# COMPRESSION_ENABLED = True

# Configuration de la redirection
# REDIRECT_ENABLED = True
# REDIRECT_MAX_TIMES = 20  # Nombre maximum de redirections à suivre

# Configuration des cookies
# COOKIES_DEBUG = False

# Configuration des retry
# RETRY_ENABLED = True
# RETRY_TIMES = 3  # Nombre de tentatives de reconnexion
# RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Configuration du user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configuration de la politique de robots.txt
# ROBOTSTXT_OBEY = True

# Configuration de la profondeur maximale
# DEPTH_LIMIT = 0  # 0 pour illimité

# Configuration de l'ordre de tri des URLs
# DEPTH_PRIORITY = 0

# Configuration de la politique de priorité des requêtes
# SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'

# Configuration de la taille de la file d'attente
# SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# Configuration de la taille maximale de la file d'attente
# SCHEDULER_MEMORY_QUEUE_SIZE = 100

# Configuration de la persistance de la file d'attente
# SCHEDULER_PERSIST = False

# Configuration du réessai des requêtes échouées
# RETRY_ENABLED = True
# RETRY_TIMES = 3
# RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Configuration du timeout des requêtes
# DOWNLOAD_TIMEOUT = 180  # 3 minutes

# Configuration de la taille maximale des réponses
# DOWNLOAD_MAXSIZE = 1073741824  # 1GB

# Configuration de la taille d'avertissement des réponses
# DOWNLOAD_WARNSIZE = 33554432  # 32MB

# Configuration de la compression
# COMPRESSION_ENABLED = True

# Configuration de la redirection
# REDIRECT_ENABLED = True
# REDIRECT_MAX_TIMES = 20  # Nombre maximum de redirections à suivre

# Configuration des cookies
# COOKIES_DEBUG = False
