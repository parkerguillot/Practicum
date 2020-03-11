# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PracticumItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # link = scrapy.Field()
    article_url = scrapy.Field()
    twitter = scrapy.Field()
    author = scrapy.Field()
    article_title = scrapy.Field()
    article_date = scrapy.Field()
    article_text = scrapy.Field()
    # name = scrapy.Field()
    pass
