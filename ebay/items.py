# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CarAd(scrapy.Item):
    name = scrapy.Field()
    maker = scrapy.Field()
    model = scrapy.Field()
    year = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
    info = scrapy.Field()
    condition = scrapy.Field()
    remoteid = scrapy.Field()
    image_path = scrapy.Field()
