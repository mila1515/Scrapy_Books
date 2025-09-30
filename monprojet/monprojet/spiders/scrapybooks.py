import scrapy
from ..items import BookItem
from ..itemloaders import BookLoader
import re

class ScrapybooksSpider(scrapy.Spider):
    name = "scrapybooks"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        for bloc in response.css('article.product_pod'):
            # On crée un loader en liant l'item, le bloc et la réponse
            loader = BookLoader(item=BookItem(), selector=bloc, response=response)

            # Extraction des champs de base
            loader.add_css('title', 'h3 a::attr(title)')
            loader.add_css('price', 'p.price_color::text')
            loader.add_css('rating', 'p.star-rating::attr(class)')
            
            # On récupère l'URL du livre
            book_url = response.urljoin(bloc.css('h3 a::attr(href)').get())
            loader.add_value('url', book_url)
            
            # On suit le lien vers la page détaillée pour récupérer le stock et la catégorie
            yield scrapy.Request(
                book_url,
                callback=self.parse_book_detail,
                meta={'loader': loader}
            )

        # Pagination
        next_page = response.css('li.next a::attr(href)').get()   # Récupère le lien de la page suivante
        if next_page:
            yield response.follow(next_page, callback=self.parse)   


        

    def parse_book_detail(self, response):
        loader = response.meta['loader']

        # Extraction du stock depuis la page détaillée (nettoyé)
        stock_text = response.css('p.instock.availability::text').getall()   # Récupère tout le texte dans le paragraphe
        stock_text = " ".join(s.strip() for s in stock_text if s.strip())    # Nettoie et joint les parties
        self.logger.debug(f"Texte du stock nettoyé: {stock_text}")           # Log pour vérifier

        # Extraction du nombre avec regex
        stock_match = re.search(r'\((\d+)\s+available\)', stock_text) # Cherche un nombre suivi de " available"
        stock_qty = int(stock_match.group(1)) if stock_match else 0   # Si pas trouvé, on met 0
        self.logger.debug(f"Quantité extraite: {stock_qty}")          

        # Ajout du stock à l'item
        loader.add_value('stock', stock_qty)

        # Extraction de la catégorie depuis le breadcrumb
        category = response.css('ul.breadcrumb li a::text').getall()
        if len(category) > 2:  # Home > Books > Catégorie
            loader.add_value('category', category[2]) # La catégorie est le 3ème élément

        yield loader.load_item() # On retourne l'item finalisé