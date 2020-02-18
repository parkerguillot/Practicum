# -*- coding: utf-8 -*-
import scrapy
from ..items import PracticumItem

urls = 'https://www.nrdc.org/blogs/'


class Blog3SpiderSpider(scrapy.Spider):
    name = 'blog3_spider'

    def start_requests(self):
        yield scrapy.Request(url=urls,
                             callback=self.parse_front)

    # First parsing method
    def parse_front(self, response):
        next_page = response.css('li.pager-next a::attr(href)').get()
        article_links = response.xpath('//header[contains(@class, "tab-teaser__header mb-16")]/a/@href')
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
        all_blogs = response.css('div.content')

        # this will loop through multiple instances of specified tags in the url
        # this will allow multiple quotes to be extracted from the website
        # extracts the region, article_date, and article_title of each blog
        for blogs in all_blogs:
            article_title = blogs.xpath('//h1//text()').extract()
            author = blogs.xpath('//span[contains(@class, "byline-text author-name")]//text()').extract()
            article_date = blogs.xpath('//span[contains(@class, "byline-text author-date")]//text()').extract()
            article_text = blogs.xpath('//span[@class = "body-content"]//p//text()').extract()
            twitter = 'no twitter'
            blogger = ''
            for blog in author:
                blogger = blogger + blog
            body = ''
            for text in article_text:
                body = body + text
            # # blog_title = ''
            # # for title in article_title:
            # #     blog_title = blog_title + title
            # blog_region = ''
            # for area in region:
            #     blog_region = blog_region + area
            # # blog_title = blog_title.replace('\r', '')
            # # blog_title = blog_title.replace('\n', '')
            # # blog_title = blog_title.replace('\t', '')
            blogger = blogger.replace('\r', '')
            blogger = blogger.replace('\n', '')
            blogger = blogger.replace('\t', '')
            body = body.replace('\r', '')
            body = body.replace('\n', '')
            body = body.replace('\t', '')
            # blog_region = blog_region.replace('\r', '')
            # blog_region = blog_region.replace('\n', '')
            # blog_region = blog_region.replace('\t', '')

            # declares items extracted for each of the following
            items['article_url'] = response.request.url
            items['article_date'] = article_date
            items['article_title'] = article_title
            items['author'] = blogger
            items['article_text'] = body
            items['twitter'] = twitter

            yield items

        # this assigns a value for looking at pagination in a url
        # next_page = response.css('li.next a::attr(href)') .get()
        # next_page = response.css('li.next.next_last a::attr(href)').get()

        # if condition to check if next_page value is empty or there are no more pages to comb through
        # if next_page is not None:
        # if next_page is not None:
        #    yield response.follow(next_page, callback=self.parse_front)
