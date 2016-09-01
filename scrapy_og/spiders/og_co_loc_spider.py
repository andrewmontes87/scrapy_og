import scrapy
import re

BASE_URL = "http://en.wikipedia.org"
DATA_URL = "https://www.wikidata.org"

class OGCoLocItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    inception = scrapy.Field()
    instance_of = scrapy.Field()
    isin = scrapy.Field()
    headquarters_location = scrapy.Field()
    headquarters_location_link = scrapy.Field()
    country = scrapy.Field()
    coordinate_location = scrapy.Field()
    # text = scrapy.Field()

class OGCoLocSpider(scrapy.Spider):
    """ 
    Locations of largest oil/gas companies
    """
    name = 'og_co_loc'
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
                data['link'] = BASE_URL + link[0]
                request = scrapy.Request(data['link'], callback=self.parse_bio, dont_filter=True)
                request.meta['item'] = OGCoLocItem(**data)
                yield request


    def parse_bio(self, response):
        item = response.meta['item']
        href = response.xpath("//li[@id='t-wikibase']/a/@href").extract()
        if href:
            request = scrapy.Request(href[0], callback=self.parse_wikidata, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_wikidata(self, response):
        item = response.meta['item']
        property_codes = [
            {'name':'instance_of', 'code':'P31'},
            {'name':'inception', 'code':'P571'},
            {'name':'isin', 'code':'P946'},
        ]
        link_codes = [
            {'name':'headquarters_location', 'code':'P159'},
        ]
        template = '//*[@id="{code}"]/div[2]/div/div/div[2]/div[1]/div/div[2]/div[2]{link_html}'

        for prop in property_codes:
            link_html = ''
            sel = response.xpath(template.format(code=prop['code'], link_html=link_html))
            sel_a = sel.xpath('./a')
            if sel_a:
                link_html = '/a'
            sel_text = response.xpath(template.format(code=prop['code'], link_html=link_html))
            if sel_text:
                item[prop['name']] = sel_text.xpath('text()').extract()[0]
 
        for prop in link_codes:
            link_html = '/a'
            sel_link = response.xpath(template.format(code=prop['code'], link_html=link_html))
            dest_html = DATA_URL + sel_link.xpath('./@href').extract()[0]
            request = scrapy.Request(dest_html, callback=self.parse_location, dont_filter=link_html)
            request.meta['item'] = item
            yield request


    def parse_location(self, response):
        item = response.meta['item']
        property_codes = [
            {'name':'country', 'code':'P17'},
            {'name':'coordinate_location', 'code':'P625'},
        ]
        template = '//*[@id="{code}"]/div[2]/div/div/div[2]/div[1]/div/div[2]/div[2]{link_html}'

        for prop in property_codes:
            link_html = ''
            sel = response.xpath(template.format(code=prop['code'], link_html=link_html))
            sel_a = sel.xpath('./a')
            if sel_a:
                link_html = '/a'
            sel_text = response.xpath(template.format(code=prop['code'], link_html=link_html))
            if sel_text:
                item[prop['name']] = sel_text.xpath('text()').extract()[0]

        yield item



