import scrapy
from ..items import PracticumItem
import requests
from scrapy_splash import SplashRequest

urlslist = [
        #'https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights',
        #'https://www.healthmanagement.com/knowledge-share/blog/',
        #'https://www.brookings.edu/search/?s=healthcare',
         'https://www.kff.org/search/?s=healthcare&paged=&fs=search&s=healthcare'
    ]

select_dic = {'https://www.mckinsey.com/industries/healthcare-systems-and-services/our-insights':{'title':'//div[@class="contentwrapper"]//h1//text()',
                                                                                                  'body':'//article[@itemprop="articleBody"]//p/text()', \
                                                                                                  'author':"//div[@class='author-by-line']//a/text()", \
                                                                                                  'all_elements':"//div[@class='item']/div[@class='text-wrapper']",\
                                                                                                  'element_link': ".//a/@href", \
                                                                                                  'element_type':".//span/text()",\
                                                                                                  'element_type_constraint':'Collection',\
                                                                                                  'type':"//div/footer/span/text()", \
                                                                                                  'date':"//div/footer/time[@class='hero-article-info']/text()",\
                                                                                                  'inf_scroll':{'Type':'build_request',\
                                                                                                                'parameter_name1': 'ig_page',
                                                                                                                'Parameters':{ 'UseAjax': 'true',\
                                                                                                                               'PresentationId': '{225AFD08 - 2381 - 4FCD - B73F - F68A6859B4FC}',\
                                                                                                                               'ds': '{F8382F15-08D4-458C-96F8-26623103604B}',\
                                                                                                                               'showfulldek': 'False',\
                                                                                                                               'hideeyebrows': 'False',\

                                                                                                                             },
                                                                                                                'page_name':'ig_page',\

                                                                                                                'page_start': 1}},\

              'https://www.healthmanagement.com/knowledge-share/blog/':{'title':"//header[@class='entry-header']/h1/text()", \
                                                                        'body':"//div[@class='entry-content']//p//text()", \
                                                                        'author':"//span[@class='author-name']//text()",\
                                                                        'all_elements':"//article",\
                                                                        'element_link': ".//header/h2/a/@href", \
                                                                        'element_type':".//span/text()",\
                                                                        'element_type_constraint':'None',\
                                                                        'type':"//h1[@class='page-title']//text()",\
                                                                        'date':"//time/text()",  \
                                                                        'inf_scroll':{'Type':'pagination',\
                                                                                      'next_page':'//a[@class="nextpostslink"]/@href' }},


              'https://www.brookings.edu/search/?s=healthcare':{'title':"//div[@class='headline-wrapper']/h1/text()", \
                                                                'body':"//div[@class='content-column']//p/text()", \
                                                                'author':"//div[@class='expert-info']//span/text()",\
                                                                'all_elements':"//div[@class='article-info']",\
                                                                'element_link': "./h4/a/@href", \
                                                                'element_type':"//none",\
                                                                'element_type_constraint':'None',\
                                                                'type':"//div[@class='headline-wrapper']/a/text()",\
                                                                'date':"//div[@class='headline-wrapper']//time/text()",  \
                                                                'Atwitter':"//div[@class='expert-info']/div[@class='contact']/a/@href",\
                                                                'inf_scroll':{'Type':'pagination',\
                                                                              'next_page':"//a[@class='load-more']/@href" }},

              'https://www.kff.org/search/?s=healthcare&paged=&fs=search&s=healthcare':{'title':"//div[@class='box primary']/h2/text()", \
                                                          'body':"//div[@class='box full-post']//text()", \
                                                          'author':"//none",\
                                                          'all_elements':"//article",\
                                                          'element_link': ".//h5/a/@href", \
                                                          'element_type':"//none",\
                                                          'element_type_constraint':'None',\
                                                          'type':"//none",\
                                                          'date':"//p[@class='byline']/span/text()",  \
                                                          'Atwitter':"//none",\
                                                          'inf_scroll':{'Type':'pagination',\
                                                                        'next_page':"//ul[@class='page-numbers']//a[@class='next page-numbers']/@href" }},


              'https://eldercarematters.com/elder-care-senior-care-articles/':{'title':"", \
                                                          'body':"", \
                                                          'author':"",\
                                                          'all_elements':"",\
                                                          'element_link': "", \
                                                          'element_type':"//none",\
                                                          'element_type_constraint':'None',\
                                                          'type':"//none",\
                                                          'date':"",  \
                                                          'Atwitter':"//none",\
                                                          'inf_scroll':{'Type':'pagination',\
                                                                        'next_page':"" }},



}

for urls in urlslist:

    class p_spider1(scrapy.Spider):
        name = 'ps1'
        c=1
        current_all_element = []
        def start_requests(self):

            yield scrapy.Request(url=urls, callback=self.parse_cover)

        def parse_cover(self, response):
            all_element = response.xpath(select_dic[urls]['all_elements'])
            if all_element != [] and all_element != p_spider1.current_all_element:
                p_spider1.current_all_element = all_element
                for el in all_element:
                    link = el.xpath(select_dic[urls]['element_link']).extract()
                    print(link)
                    Article_type = []
                    if select_dic[urls]['element_type']:
                        Article_type = el.xpath(select_dic[urls]['element_type']).extract()
                        print(Article_type)
                    if select_dic[urls]['element_type_constraint'] not in Article_type:
                        print(len(all_element))
                        yield response.follow(link[0], callback=self.parse)

                if select_dic[urls]['inf_scroll']['Type'] == 'build_request':
                    p_spider1.c += 1
                    params = { 'UseAjax': 'true',
                               'PresentationId': '{225AFD08 - 2381 - 4FCD - B73F - F68A6859B4FC}',
                               'ds': '{F8382F15-08D4-458C-96F8-26623103604B}',
                               'showfulldek': 'False',
                               'hideeyebrows': 'False',
                               'ig_page': p_spider1.c

                             }
                    # params =select_dic[urls]['inf_scroll']['Parameters']
                    # params[select_dic[urls]['inf_scroll']['parameter_name1']]=p_spider1.c
                    print('PAGE NUMBER >>>>>>',p_spider1.c,'!!!!!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                    print(params)
                    yield scrapy.FormRequest(url=urls, method='GET', formdata=params, callback=self.parse_cover)

                if select_dic[urls]['inf_scroll']['Type'] == 'pagination':

                    flink = response.xpath(select_dic[urls]['inf_scroll']['next_page']).extract()[0]
                    print('LETS GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'+str(flink))
                    if flink !=[]:
                        yield response.follow(flink, callback=self.parse_cover)

        def parse(self, response):
            sel_title = select_dic[urls]['title']
            sel_body = select_dic[urls]['body']
            sel_author = select_dic[urls]['author']
            sel_type = select_dic[urls]['type']
            items = PracticumItem()
            title = response.xpath(sel_title).extract()
            body = response.xpath(sel_body).extract()
            author = response.xpath(sel_author).extract()
            Article_type = response.xpath(sel_type).extract()
            date = response.xpath(select_dic[urls]['date']).extract()
            Atwitter = response.xpath(select_dic[urls]['Atwitter']).extract()
            titlemerge=''
            bodymerge = ''
            for t in title:
                titlemerge = titlemerge + t
            for b in body:
                bodymerge = bodymerge + b
            if len(date) >0:
                items['Article_Date'] = date[0]
            else:
                items['Article_Date']=''
            items['Article_url'] = response.request.url

            if len(Article_type)>0:
                Article_type2 = Article_type[0].replace(' ', '')
                Article_type2 = Article_type2.replace('|', '')
                items['Article_Type'] = Article_type2
            else:
                items['Article_Type'] = ''

            items['Article_Title'] = titlemerge
            items['Article_Text'] = bodymerge
            if len(author)>0:
                items['Article_Author'] = author[0]
            else:
                items['Article_Author'] = ''
            if len(Atwitter)>0:
                items['ATwitter'] = Atwitter[0]
            else:
                items['ATwitter'] = ''

            yield items


