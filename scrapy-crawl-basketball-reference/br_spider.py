import scrapy

class BlogSpider(scrapy.Spider):
    name = 'brspider'
    start_urls = ['https://www.basketball-reference.com/playoffs/']

    def parse(self, response):
        for title in response.css('h2.entry-title'):
            yield {'title': title.css('a ::text').extract_first()}
