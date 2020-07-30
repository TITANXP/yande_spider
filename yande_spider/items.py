# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 类似于实体类
class PicPage(scrapy.Item):
    url = scrapy.Field()

class Pic(scrapy.Item):
    unchanged_pic_url = scrapy.Field()
    changed_pic_url = scrapy.Field()
    pic_id = scrapy.Field()
    parent_pic_id = scrapy.Field()
    pool_id = scrapy.Field()
    pool = scrapy.Field()
    pool_seq = scrapy.Field()
    rating = scrapy.Field()
    source = scrapy.Field()
    size = scrapy.Field()
    tags = scrapy.Field()
    date = scrapy.Field()

class Pool(scrapy.Item):
    pool_id = scrapy.Field()
    pool_name = scrapy.Field()
    pool_url = scrapy.Field()
    pic_num = scrapy.Field()
    date = scrapy.Field()

class ImageItem(scrapy.Item):
    pool_name = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
