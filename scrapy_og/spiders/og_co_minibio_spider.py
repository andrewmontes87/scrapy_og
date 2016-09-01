import scrapy
import re

BASE_URL = 'http://en.wikipedia.org'

class OGCoMinibioItem(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    revenue = scrapy.Field()
    mini_bio = scrapy.Field()
    image_urls = scrapy.Field()
    bio_img = scrapy.Field()
    images = scrapy.Field()

class OGCoMinibioSpider(scrapy.Spider):
    """ 
    Scrapes mini bio + images of oil/gas companies
    """

    name = 'og_co_minibio'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        "https://en.wikipedia.org/wiki/List_of_largest_oil_and_gas_companies_by_revenue"
    ]

    def parse(self, response):

        filename = response.url.split('/')[-1]
        trs = response.xpath('//tr')
        for tr in trs:
            link = tr.xpath('td[2]/a/@href').extract()
            if link:
                data = {}
                data['name'] = tr.xpath('td[2]/a/text()').extract()[0]
                revenue_td = tr.xpath('td[3]')
                revenue_td_i = revenue_td.xpath('i')
                if len(revenue_td_i):
                    data['revenue'] = revenue_td_i.xpath('text()').extract()[0]
                else: 
                    data['revenue'] = revenue_td.xpath('text()').extract()[0]

                data['link'] = BASE_URL + link[0]
                request = scrapy.Request(data['link'], callback=self.get_img)
                request.meta['item'] = OGCoMinibioItem(**data)
                yield request

    def get_img(self, response):
        """ Get photo """

        BASE_URL_ESCAPED = 'http:\/\/en.wikipedia.org'
        item = response.meta['item']
        
        item['image_urls'] = []
        
        img_src = response.xpath('//table[contains(@class, "infobox")]//img/@src')
        if img_src:
            item['image_urls'] = ['https:'+img_src[0].extract()]

        yield item






