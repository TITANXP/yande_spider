# -*- coding: utf-8 -*-
import scrapy
from yande_spider.items import Pic, PicPage, Pool
from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import SelectorList
from scrapy.utils.project import get_project_settings
import datetime
import pymongo

class PoolSpider(scrapy.Spider):
    name = 'pool'
    allowed_domains = ['yande.re']
    setting = get_project_settings() # 配置文件，用来取值
    # start_urls = ['https://yande.re/pool/show/96975']  # 可以是一个url列表
    table = pymongo.MongoClient(setting['MONGO_URL'])[setting['MONGO_DB']][setting['MONGO_YANDE_POOL_POST_DB']]
    pool_table = pymongo.MongoClient(setting['MONGO_URL'])[setting['MONGO_DB']][setting['MONGO_YANDE_POOL_DB']]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        file_path = r'D:\IDEA\yande_spider\yande_spider\in\pool\pools.txt'
        start_urls = []
        with open(file_path, 'r') as f:
            for line in f.readlines():
                start_urls.append(line)
                print(line)
        return super().from_crawler(crawler, start_urls=start_urls)

    def parse(self, response):
        pool = Pool()
        pool['pool_id'] = int(response.url.split('/')[-1])
        pool['pool_name'] = response.xpath('//div/div/h4[contains(text(), "P")]/text()').get().replace('Pool: ', '')
        pool['pool_url'] = response.url
        post_url_list = response.xpath('//li//div[@class="inner"]/a[@class="thumb"]/@href')
        pool['pic_num'] = len(post_url_list)
        pool['date'] = datetime.datetime.now()
        print(pool)
        if not self.pool_table.find_one({'pool_id': pool['pool_id']}):
            yield pool
        else:
            print(pool['pool_name'] + '已经下载过')

        for url in post_url_list:
            pic_id = int(url.get().replace('/post/show/', ''))
            href = 'https://' + self.allowed_domains[0] + url.get()
            if not self.table.find_one({'pic_id': pic_id}):
                yield scrapy.Request(href, callback=self.parse_pic)
            else:
                print('#####图片 ' + str(pic_id) + ' 已存在#####')
        # 也可以用return将所有数据都返回

    # 处理图片详情页
    def parse_pic(self, response):
        print('开始处理' + response.url)
        pic = Pic()
        pic['unchanged_pic_url'] = response.xpath('//a[@class="original-file-unchanged"]/@href').extract_first()
        pic['changed_pic_url'] = response.xpath('//a[@class="original-file-changed"]/@href').extract_first()
        pic['pic_id'] = int(response.xpath('//*[@id="stats"]/ul/li[1]/text()').extract_first().replace('Id: ', ''))
        pic['rating'] = response.xpath('//li[contains(./text(), "Rating")]/text()').get().replace('Rating: ', '')
        pic['size'] = response.xpath('//*[@id="stats"]/ul/li[contains(./text(), "Size")]/text()').get().replace(
            'Size: ', '')
        pic['source'] = response.xpath('//*[@id="stats"]/ul/li[contains(./text(), "Source")]/a/@href').get()
        pic['date'] = datetime.datetime.now()
        pic['tags'] = response.xpath(
            '//ul[@id="tag-sidebar"]/li/a[contains(./@href, "/post?tags=") and not(@class)]/text()').extract()
        parent = response.xpath('//div/a[contains(text(), "parent post")]/@href').get()
        if parent:
            pic['parent_pic_id'] = int(parent.replace('/post/show/', ''))
        if response.xpath('//p/span').get():
            pic['pool'] = response.xpath('//p/span/following-sibling::*/text()').get()
            pic['pool_id'] = int(response.xpath('//p/span/following-sibling::*/@href').get().replace('/pool/show/', ''))
            pic['pool_seq'] = response.xpath('//p/span/text()').get().replace('#', '')
        yield pic
