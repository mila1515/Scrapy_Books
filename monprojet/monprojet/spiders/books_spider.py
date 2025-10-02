import scrapy
from scrapy.http import Request
from monprojet.items import BookItem

class BooksSpider(scrapy.Spider):
    """
    Spider pour extraire les livres depuis books.toscrape.com
    """
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        """
        Traite la page d'accueil et extrait les liens vers les livres
        """
        self.logger.info('Visited %s', response.url)
        
        # Extraire les liens vers les pages de détail des livres
        book_links = response.css('article.product_pod h3 a::attr(href)').getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)
        
        # Suivre le lien vers la page suivante
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_book(self, response):
        """
        Extrait les détails d'un livre à partir de sa page de détail
        """
        self.logger.info('Processing book: %s', response.url)
        
        book = BookItem()
        book['url'] = response.url
        book['title'] = response.css('h1::text').get()
        book['price'] = response.css('p.price_color::text').get()
        book['stock'] = response.css('p.instock.availability::text').getall()[-1].strip()
        book['rating'] = response.css('p.star-rating::attr(class)').get().split()[-1]
        book['description'] = response.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
        
        # Informations du tableau
        for row in response.css('table.table.table-striped tr'):
            key = row.css('th::text').get()
            value = row.css('td::text').get()
            if key and value:
                book[key.lower().replace(' ', '_')] = value.strip()
        
        return book
