# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# this package can be downloaded by using pip install mysql-connector-python
import mysql.connector


class PracticumPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(host="ba-isdsclass-dev2.lsu.edu",
                                            user="aguil66",
                                            passwd="msadatabase",
                                            database="msa_schema")
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS blogs")
        self.cursor.execute("create table blogs(article_url text,article_date text,article_title text,"
                            "article_text text,author text, twitter text)")
        # self.cursor.execute("create table blogs("
        #                     "link text,"
        #                     "region text,"
        #                     "author text, "
        #                     "article_date text,"
        #                     "article_title text, "
        #                     "article_text text)"
        #                     )

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.cursor.execute("insert into blogs values (%s,%s,%s,%s,%s,%s)", (
            item['article_url'],
            item['article_date'],
            item['article_title'],
            item['article_text'],
            item['author'],
            item['twitter']
        ))

        self.conn.commit()

        # self.cursor.execute("insert into blogs values (%s,%s,%s)", (
        #     item['link'][0],
        #     item['region'][0],
        #     item['author'][0],
        #     item['article_date'][0],
        #     item['article_title'][0],
        #     item['article_text'][0]
        # ))


