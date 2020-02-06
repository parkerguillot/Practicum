# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import PracticumItem

urls = 'https://www.energyindepth.org/category/blog/'


class BlogSpiderSpider(scrapy.Spider):
    name = 'blog_spider'

    def start_requests(self):
        yield scrapy.Request(url=urls,
                             callback=self.parse)

    def parse(self, response):

        items = PracticumItem()

        all_blogs = response.css('div.post_title.tt')

        for blogs in all_blogs:
            region = blogs.css('.post_lable a::text').extract()
            article_date = blogs.css('span.date::text').extract()
            article_title = blogs.css('.entry_title a::text').extract()

            items['region'] = region
            items['article_date'] = article_date
            items['article_title'] = article_title

            yield items

        next_page = response.css('li.next.next_last a::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    # def parse_front(self, response):
    #
    #     title = response.css('h2.entry_title').extract()
    #     yield title
    #
    #     # items = PracticumItem()
    #
    #     for href in response.xpath('//h2[@class = "entry_title"]/a/@href'):
    #         url = response.urljoin(href.extract())
    #         yield scrapy.Request(url, callback=self.parse_pages)
    #
    #
    #     # next_page = response.css('li.next.next_last a::attr(href)').get()
    #
    #     # if next_page is not None:
    #     #     yield response.follow(next_page, callback=self.parse_front)
    #
    # def parse_pages(self, response):
    #
    #     items = PracticumItem()
    #     for blogs in response.xpath('//content_inner'):
    #
    #         region = blogs.css('span.post_lable.ty::text').extract()
    #         article_title = blogs.css('h2.entry_title::text').extract()
    #         author = blogs.css('span.post_author::text').extract()
    #         article_date = blogs.css('span.time::text').extract()
    #         article_text = blogs.css('div.post_content.a::attr(p)').extract()
    #         link = blogs.css('head.link::attr(href)').extract()
    #
    #         items['region'] = region
    #         items['author'] = author
    #         items['article_title'] = article_title
    #         items['article_date'] = article_date
    #         items['article_text'] = article_text
    #         items['link'] = link
    #
    #         yield items


        # next_page = response.css('li.next.next_last a::attr(href)').get()
        #
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)



