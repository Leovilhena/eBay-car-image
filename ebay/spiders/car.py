# -*- coding: utf-8 -*-
import os
import scrapy
import json
from fake_useragent import UserAgent
from ..items import CarAd
from zlib import crc32

ua = UserAgent()


class CarSpider(scrapy.Spider):
    name = 'car'
    allowed_domains = ['ebay.com', 'i.ebayimg.com']
    start_urls = ['https://www.ebay.com/sch/Cars-Trucks/6001/i.html?LH_BIN=1&_ul=US&_fosrp=1']

    def get_int(self, string):
        return ''.join(letter for letter in string if letter.isdigit())

    def parse(self, response):
        links = response.xpath('//div[@class="cat-link"]/a')

        for link in links:
            maker = link.xpath('text()').extract_first()

            yield scrapy.Request(
                url=link.attrib['href'],
                callback=self.parse_pages,
                meta={'maker': maker},
                headers={'user-agent': ua.random}
            )

    def parse_pages(self, response):
        listing_count = self.get_int(response.xpath('//span[@class="listingscnt"]/text()').extract_first())

        if listing_count:
            listing_count = int(listing_count)
        else:
            return

        if listing_count % 2:
            listing_count += 1

        for page in range(1, listing_count + 1):
            yield scrapy.Request(
                url=''.join([response.url, '&_pgn=', str(page), '&_sop=3', '&_skc=', str(50 * (page - 1))]),
                callback=self.parse_list,
                meta={'maker': response.meta['maker']},
                headers={'user-agent': ua.random}
            )

    def parse_list(self, response):
        links = response.xpath('//h3/a/@href')

        if not links:
            return

        for link in links:
            yield scrapy.Request(
                url=link.extract(),
                callback=self.parse_ad,
                meta={'maker': response.meta['maker']},
                headers={'user-agent': ua.random}
            )

    def parse_ad(self, response):
        def id_hash(url):
            return str(crc32(bytes(url, encoding='utf8')))

        ad = CarAd()

        ad['price'] = ''.join([number for number in response.xpath(
            '//span[@id="mm-saleDscPrc"]/text() '
            '| //span[@id="prcIsum"]/text() '
            '| //span[@id="convbidPrice"]/text()'
        ).extract_first().replace(',', '') if number.isdigit() or number == '.'])  # u'US $19,780.00'

        images = set(response.xpath('//td/div/img[contains(@src,"i.ebayimg.com")]/@src').extract())
        ad['image_urls'] = [img.replace('l64', 'l1200') for img in images]
        ad['name'] = response.xpath('//h1[@id="itemTitle"]/text()').extract_first()

        keys = response.xpath('//div[@class="section"]/table/tr/td/text()')
        values = response.xpath(
            '//div[@class="section"]/table/tr/td/span/text() | '
            '//div[@class="section"]/table/tr/td/h2/text() | '
            '//div[@class="section"]/table/tr/td/div/text() | '
            '//div[@class="section"]/table/tr/td/h2/span/text()')

        keys = [
            k.extract().lower()[:-1].replace(':', '').strip()
            for k in keys if k.extract().replace('\n', '').replace('\t', '').strip()
        ]
        values = [
            v.extract().strip()
            for v in values if v.extract().replace('\n', '').replace('\t', '').strip()
        ]

        if len(keys) == len(values):
            ad['info'] = dict(zip(keys, values))
        else:
            ad['info'] = {}

        ad['condition'] = response.xpath('.//div[contains(@class,"condText")]/text()').extract_first()
        ad['url'] = response.url
        ad['maker'] = response.meta['maker']
        ad['remoteid'] = id_hash(response.url)

        if 'year' in ad['info']:
            ad['year'] = ad['info']['year']
        else:
            ad['year'] = response.xpath('//h1[@id="itemTitle"]/text()').re_first('^((19|20)\d{2})')

        if 'model' in ad['info']:
            ad['model'] = ad['info']['model']
        else:
            try:
                ad['model'] = '-'.join(response.xpath('//h1[@id="itemTitle"]/text()').extract_first().split()[2:4])
            except:
                ad['model'] = 'unknown'

        # Where it will be saved
        ad['image_path'] = '/'.join([
            '/ebay',
            ad['maker'],
            ad['model'],
            ad['year'],
            ad['remoteid'],
        ]).replace('-', 'm')

        full_path = '/Users/leovilhena/ebay_imgs' + ad['image_path']  # FIXME change to owners path
        if not os.path.exists(full_path):
            # Creates the directory if doesn't exist
            os.makedirs(full_path)
            os.makedirs(full_path + '/json')

        # Saves json info
        json_path = ''.join([full_path, '/json/', ad['remoteid'], '.json'])
        with open(json_path, 'w+') as fl:
            fl.write(json.dumps(dict(ad)))

        yield ad
