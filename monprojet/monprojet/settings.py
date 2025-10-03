# Scrapy settings for monprojet project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "monprojet"

SPIDER_MODULES = ["monprojet.spiders"]
NEWSPIDER_MODULE = "monprojet.spiders"

ADDONS = {}

# Configurez les pipelines d'items

ITEM_PIPELINES = {
    'monprojet.pipelines.CleanPipeline': 300,
    'monprojet.pipelines.DuplicatesLoggerPipeline': 400,
    'monprojet.pipelines.SQLitePipeline': 800,
    
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "monprojet (+http://www.yourdomain.com)"
#USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

# Obey robots.txt rules (à laisser à True pour respecter le site)
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # ça évite de surcharger le site et évite les blocages.
DOWNLOAD_DELAY = 1 # Délai entre les requêtes (en secondes)

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "monprojet.middlewares.MonprojetSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
    "monprojet.middlewares.MonprojetDownloaderMiddleware": 543,
}  # Le numéro indique l'ordre d'exécution (plus petit = plus tôt), le 543 est un bon compromis. 

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "monprojet.pipelines.MonprojetPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 3
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True  # Utile pour le développement, à désactiver en production
#HTTPCACHE_EXPIRATION_SECS = 86400     # 1 jour (les images sont re-téléchargées au bout d'un jour)
HTTPCACHE_DIR = "httpcache"  # Dossier où sont stockées les requêtes en cache
#HTTPCACHE_IGNORE_HTTP_CODES = []  # On ne met pas 404 ici pour voir les erreurs
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"   # Stockage sur le disque

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"


LOG_LEVEL = "DEBUG"  # Pour avoir plus de détails dans les logs. En production, mettre à WARNING ou ERROR
