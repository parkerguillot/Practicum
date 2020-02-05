import scrapy
from scrapy.crawler import CrawlerProcess

# Create the Spider class
class blogspider(scrapy.Spider):
  name = "blog_spider"
  urls = ['https://www.energyindepth.org/category/blog/']

  custom_settings={ 'FEED_URI': "eid_%(time)s.csv",
                       'FEED_FORMAT': 'csv'}
  # start_requests method
  def start_requests(self):
    urls = 'https://www.energyindepth.org/category/blog/'
    yield scrapy.Request(url = urls,
                         callback = self.parse_front)
  # First parsing method
  def parse_front(self, response):
    article_links = response.xpath('//h2[@class = "entry_title"]/a/@href')
    links_to_follow = article_links.extract()
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_pages)

  # Second parsing method
  def parse_pages(self, response):
    region = response.xpath('//a[contains(@class,"one")]/text()').extract()
    author = response.xpath('//a[contains(@class, "post_author_link")]/text()').extract()
    article_date = response.xpath('//span[@class = "time"]/text()').extract()
    article_text = response.xpath('//p/text()').extract()

    row_data=zip(region,author,article_date,article_text)

    for item in row_data:

        scraped_info = {
                #key:value
                'page':response.url,
                'audience_region' : item[0], #item[0] means product in the list and so on, index tells what value to assign
                'article_author' : item[1],
                'date_written' : item[2],
                'text' : item[3],
            }

        yield scraped_info










# Initialize the dictionary **outside** of the Spider class
# dc_dict = dict()
#
# # Run the Spider
process = CrawlerProcess()
process.crawl(blogspider)
process.start()
#
# # Print a preview of courses
# previewCourses(dc_dict)
