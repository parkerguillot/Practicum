# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import PracticumItem
# urls = list of urls that will be used in the model

selectdic = {'https://eidhealth.org/category/blog/':{'article_date':'span.time::text', \
                                                             'article_title':'.entry_title::text',\
                                                             'author':'.post_author_link::text',\
                                                             'article_text':'//p/text()'\
                                                             }}
urls = 'https://eidhealth.org/category/blog/'

# Each Spider will perform a different function when extracting information


class BlogSpiderSpider(scrapy.Spider):
    # name = declaring the name of spider for later use in program
    name = 'blog_spider'

    def start_requests(self):
        yield scrapy.Request(url=urls,
                             callback=self.parse_front)

    # First parsing method
    def parse_front(self, response):
        next_page = response.css('//*[contains(concat( " ", @class, " " ), concat( " ", "next", " " ))]/a/@href').get()
        article_links = response.xpath('//h2[@class = "cat-headline"]/a/@href')
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
        # this will loop through multiple instances of specified tags in the url
        # this will allow multiple quotes to be extracted from the website
        # extracts the region, article_date, and article_title of each blog

        article_date = response.css(selectdic[urls]['article_date']).extract()
        article_title = response.css(selectdic[urls]['article_title']).extract()
        author = response.css(selectdic[urls]['author']).extract()
        article_text = response.xpath(selectdic[urls]['article_text']).extract()
            # if article_text = None:
            #     article_title='Null'
            # if article_date = None:
            #     article_date = 'Null'

        twitter = 'no twitter'
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
            # body = body.replace('\r', '')
            # body = body.replace('\n', '')
            # body = body.replace('\t', '')
            # blog_region = blog_region.replace('\r', '')
            # blog_region = blog_region.replace('\n', '')
            # blog_region = blog_region.replace('\t', '')


            # declares items extracted for each of the following
        items['article_url'] = response.request.url
        items['article_date'] = article_date
        items['article_title'] = article_title
        items['author'] = author
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




