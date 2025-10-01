from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from spiders.scrapybooks_spider import ScrapybooksSpider
from crochet import setup, wait_for

setup()

@wait_for(timeout=120.0)
def run_spider():
    books = []

    class SpiderWrapper(ScrapybooksSpider):
        def parse(self, response, **kwargs):
            for item in super().parse(response, **kwargs):
                books.append({
                    "title": item.get("title"),
                    "author": item.get("author", "Unknown"),
                    "category": item.get("category"),
                    "price": item.get("price"),
                    "stock": item.get("stock", 0),
                    "created_at": item.get("created_at")
                })
            yield from []

    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(SpiderWrapper)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    return books
