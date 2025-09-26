# spiders/scrapybooks.py
import scrapy
from ..items import BookItem

class ScrapybooksSpider(scrapy.Spider):
    # Nom du spider (doit correspondre à celui généré par genspider)
    name = "scrapybooks"

    # Domaine autorisé — matching avec la commande genspider
    allowed_domains = ["books.toscrape.com"]

    # Point d'entrée
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        # Pour chaque bloc livre sur la page
        for bloc in response.css('article.product_pod'):
            item = BookItem()

            # titre (stocké dans l'attribut title de la balise <a>)
            item['title'] = bloc.css('h3 a::attr(title)').get()

            # prix : texte comme '£51.77' — on nettoiera dans le pipeline
            item['price'] = bloc.css('p.price_color::text').get()

            # rating : la classe p.star-rating Three|Four... (string)
            # on récupère la classe et on la transformera en int plus tard
            rating_class = bloc.css('p.star-rating').attrib.get('class', '')
            # rating_class ressemble à 'star-rating Three' -> on garde le mot final
            item['rating'] = rating_class.split()[-1] if rating_class else None

            # url de la page du livre (relative -> absolute via response.urljoin)
            relative = bloc.css('h3 a::attr(href)').get()
            item['url'] = response.urljoin(relative)

            # category : la catégorie est dans le fil d'ariane de la page liste —
            # ici on prend la catégorie de la page courante (s'il y a plusieurs niveaux,
            # on récupère le dernier lien utile)
            item['category'] = response.css('ul.breadcrumb li a::text').getall()[-1].strip()

            # stock : extrait de la page détail seulement — on peut naviguer vers la page
            # du livre si on veut obtenir des infos additionnelles. Ici on yield item tel quel.
            yield item

        # pagination : suivre le lien "next" s'il existe
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
