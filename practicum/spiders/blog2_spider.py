# -*- coding: utf-8 -*-
import scrapy
from ..items import PracticumItem
urls = 'https://www.npr.org/sections/health-shots/'


class Blog2SpiderSpider(scrapy.Spider):
    name = 'blog2_spider'

    def start_requests(self):
        yield scrapy.Request(url=urls,
                             callback=self.parse_front)

    # First parsing method
    def parse_front(self, response):
        next_page = response.css('.pager__item--next a::attr(href)').get()
        article_links = response.xpath('//h2[@class = "title"]/a/@href')
        links_to_follow = article_links.extract()
        for link in links_to_follow:
            yield response.follow(url=link,
                                  callback=self.parse_pages)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_front)

    def parse_pages(self, response):

        # calls the items.py file
        items = PracticumItem()

        # looks at source code but only at a certain html tag in the document
        # html tag for quotes is the div (tag) which is why it is specified first
        all_blogs = response.css('.story-blogpost')

        # this will loop through multiple instances of specified tags in the url
        # this will allow multiple quotes to be extracted from the website
        # extracts the region, article_date, and article_title of each blog
        for blogs in all_blogs:
            twitter = blogs.css('.byline__social-handle--5::attr(href)').extract()
            article_date = blogs.css('.date::text').extract()
            article_title = blogs.css('h1::text').extract()
            author = blogs.css('.byline__name--block a::text').extract()
            article_text = blogs.xpath('//p/text()').extract()
            body = ''
            for text in article_text:
                body = body + text
            # article_title = article_title.replace('\r', '')
            # article_title = article_title.replace('\n', '')
            # article_title = article_title.replace('\t', '')
            body = body.replace('\r', '')
            body = body.replace('\n', '')
            body = body.replace('\t', '')
            # region = region.replace('\r', '')
            # region = region.replace('\n', '')
            # region = region.replace('\t', '')
            # author = author.replace('\r', '')
            # author = author.replace('\n', '')
            # author = author.replace('\t', '')

            # declares items extracted for each of the following
            items['article_url'] = response.request.url
            items['article_date'] = article_date
            items['twitter'] = twitter
            items['article_title'] = article_title
            items['author'] = author
            items['article_text'] = body

            yield items
