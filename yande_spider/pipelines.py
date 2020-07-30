# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from yande_spider.items import *
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
import os
from mytools.idm import add_to_idm_queue
from functools import reduce

class YandeSpiderPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
        self.setting = get_project_settings()


    @classmethod
    def from_crawler(cls, crawler):
        '''
            scrapy为我们访问settings提供了这样的一个方法，这里，
            我们需要从settings.py文件中，取得数据库的URI和数据库名称
        '''
        return cls(crawler.settings.get('MONGO_URL'), crawler.settings.get('MONGO_DB')) # 返回一个YandeSpiderPipeline类，不需要实例化类就可以调用此方法

    def open_spider(self, spider):
        print('爬虫开始运行')
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]
        if self.setting['RUN_SPIDER'] == 'like': # 爬收藏
            self.table = self.db[self.setting['MONGO_YANDE_POST_DB']]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            self.post_url_file = open('download-URLs/' + self.setting['RUN_SPIDER'] + '/' + timestamp + self.setting['RUN_SPIDER'] + '.txt','w')
        elif self.setting['RUN_SPIDER'] == 'pool': # 爬pool
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            self.post_url_file = open('download-URLs/' + self.setting['RUN_SPIDER'] + '/' + timestamp + self.setting['RUN_SPIDER'] + '.txt','w')
            self.table = self.db[self.setting['MONGO_YANDE_POOL_POST_DB']]
            self.pool_table = self.db[self.setting['MONGO_YANDE_POOL_DB']]

    def process_item(self, item, spider):
        if isinstance(item, Pic):
            self.table.insert(dict(item))
            download_url = (item['unchanged_pic_url'] if item['unchanged_pic_url'] else item['changed_pic_url']) + '\n'
            self.post_url_file.write(download_url)
            if self.setting['RUN_SPIDER'] == 'pool':
                # 去掉windows文件名中不合法的字符
                #   reduce(表达式，可迭代对象，初始值)
                # pool_name = eval(reduce(lambda pool, ruler: pool.replace(ruler, ' '), '!#\\/*"?<>|:', repr(item['pool'])))
                pool_name = reduce(lambda pool, ruler: pool.replace(ruler, ' '), '!#\\/*"?<>|:', repr(item['pool']))

                add_to_idm_queue(download_url, os.path.join(self.setting['POOL_PATH'], pool_name))
                # return ImageItem(pool_name=item['pool'], image_urls=[(item['unchanged_pic_url'] if item['unchanged_pic_url'] else item['changed_pic_url'])])
        elif isinstance(item, Pool):
            print('pool')
            self.pool_table.insert(dict(item))
        return item

    def close_spider(self, spider):
        print('爬虫结束运行')
        self.post_url_file.close()
        self.client.close()


class PoolImagePipeline(ImagesPipeline):
    setting = get_project_settings()
    def get_media_requests(self, item, info):
        # 该方法在发送下载请求前调用，其实这个方法本身就是去发送下载请求的
        request_objs = super(PoolImagePipeline, self).get_media_requests(item, info)
        print(item)
        for request_obj in request_objs:
            request_obj.item = item
        return request_objs

    def file_path(self, request, response=None, info=None):
        print('file_path file_path file_path')
        # 该方法是在图片将要被存储的时候调用，来获取这个图片存储路径
        # path = super(PoolImagePipeline, self).file_path(request, response, info)
        image_name = request.url.split('/')[-1]
        images_store = self.setting['IMAGES_STORE']
        pool_name = request.item.get('pool_name')
        save_path = os.path.join(images_store, pool_name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        # image_name = path.replace('full/', '')
        save_path = os.path.join(save_path, image_name)
        print(save_path)
        return save_path
