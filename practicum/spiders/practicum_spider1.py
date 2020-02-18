import scrapy
from ..items import PracticumItem
import requests
from scrapy_splash import SplashRequest

urlslist = [
        'https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights'
    ]
select_dic = {'https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights':{'title':'div.content-wrapper > h1::text', 'body':'//article[@itemprop="articleBody"]//p/text()', \
                                                                                                  'author':"//div[@class='author-by-line']//a/text()", 'all_elements':"//div[@class='item']/div[@class='text-wrapper']",\
                                                                                                  'element_link': ".//a/@href", 'element_type':".//span/text()",\
                                                                                                  'type':"//div/footer/span/text()", 'date':"//div/footer/time[@class='hero-article-info']/text()",\
                                                                                                  'next_page':"//div[@class='view-more']/a/@href"}}
for urls in urlslist:

    class p_spider1(scrapy.Spider):
        name = 'ps1'

        def start_requests(self):

            yield scrapy.Request(url=urls, callback=self.parse_cover)

        def parse_cover(self, response):
            assert isinstance(response.xpath(select_dic[urls]['all_elements']).extract, object)
            all_element = response.xpath(select_dic[urls]['all_elements'])
            all_element = list(dict.fromkeys(all_element))
            print(len(all_element))
            for el in all_element:
                link = el.xpath(select_dic[urls]['element_link']).extract()
                print(link)
                Article_type = el.xpath(select_dic[urls]['element_type']).extract()
                print(Article_type)
                if Article_type != ['Collection']:
                    print(len(all_element))
                    yield response.follow(link[0], callback=self.parse)

            for c in range(20):
                page = c+2
                params ={ 'UseAjax': 'true',
                          'PresentationId': '{225AFD08 - 2381 - 4FCD - B73F - F68A6859B4FC}',
                          'ds': '{F8382F15-08D4-458C-96F8-26623103604B}',
                          'showfulldek': 'False',
                          'hideeyebrows': 'False',
                          'ig_page': str(page)
                        }
                print('PAGE NUMBER >>>>>>',page,'!!!!!')
                conturl = 'https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights'
                yield scrapy.FormRequest(url=conturl, method='GET', formdata=params, callback=self.parse_cover)

        def parse(self, response):
            sel_title = select_dic[urls]['title']
            sel_body = select_dic[urls]['body']
            sel_author = select_dic[urls]['author']
            sel_type = select_dic[urls]['type']
            items = PracticumItem()
            title = response.css(sel_title).extract()
            body = response.xpath(sel_body).extract()
            author = response.xpath(sel_author).extract()
            #Article_type = 'null'
            Article_type = response.xpath(sel_type).extract()
            date = response.xpath(select_dic[urls]['date']).extract()
            print('article type is:', Article_type, date)

            print(type(author), author)
            titlemerge=''
            bodymerge = ''
            for t in title:
                titlemerge = titlemerge + t
            for b in body:
                bodymerge = bodymerge + b
            # titlemerge = titlemerge.replace('\r', '')
            # titlemerge = titlemerge.replace('\n', '')
            # titlemerge = titlemerge.replace('\t', '')
            # bodymerge = bodymerge.replace('\r','')
            # bodymerge = bodymerge.replace('\n', '')
            # bodymerge = bodymerge.replace('\t', '')
            if len(date) >0:
                items['Article_date'] = date[0]
            else:
                items['Article_date']=''
            items['Article_url'] = response.request.url

            if len(Article_type)>0:
                Article_type2 = Article_type[0].replace(' ', '')
                Article_type2 = Article_type2.replace('|', '')
                items['Article_type'] = Article_type2
            else:
                items['Article_type'] = ''

            items['titletext'] = titlemerge
            items['body'] = bodymerge
            if len(author)>0:
                items['author'] = author[0]
            else:
                items['author'] = ''

            yield items

