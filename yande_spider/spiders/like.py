# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import FormRequest
from scrapy.utils.project import get_project_settings
from yande_spider.items import *
import datetime
import pymongo


class LikeSpider(scrapy.Spider):
    name = 'like'

    allowed_domains = ['yande.re']
    setting = get_project_settings() # 配置文件，用来取值
    table = pymongo.MongoClient(setting['MONGO_URL'])[setting['MONGO_DB']][setting['MONGO_YANDE_POST_DB']]
    # rules = (
    #     Rule(LinkExtractor(allow=r'/post\?page=\d+&tags=vote%3A%3E%3D1%3Akamiyamashiki\+order%3Avote'), callback='parse_list', follow=True),
    # )
    # https://yande.re/post?page=1&tags=vote%3A%3E%3D1%3Akamiyamashiki+order%3Avote
    # /post?page=2&tags=vote%3A%3E%3D1%3Akamiyamashiki+order%3Avote

    def start_requests(self):
        yield scrapy.Request('https://yande.re/user/login', callback=self.login)

    def login(self, response):
        form_data = {
            'user[name]': self.setting['YANDE_USERNAME'],
            'user[password]': self.setting['YANDE_PASSWORD']
        }
        yield FormRequest.from_response(response, formdata=form_data, callback=self.after_login)

    def after_login(self, response):
        yield scrapy.Request('https://yande.re/post?tags=vote:'+ self.setting['YANDE_VOTE'] + ':' + self.setting['YANDE_USERNAME'] + ' order:vote', callback=self.parse_list)


    def parse_list(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        print(response.url)
        print(response.body)
        for url_selector in response.xpath('//li//div[@class="inner"]/a[@class="thumb"]/@href'):
            url = url_selector.get()
            pic_id = int(url.replace('/post/show/', ''))
            if not self.table.find_one({'pic_id': pic_id}):
                yield scrapy.Request('https://' + self.allowed_domains[0] + url, callback=self.parse_pic)
            else:
                print('#####图片 ' + str(pic_id) + ' 已存在#####')
            # pass
        if response.xpath('//a[@class="next_page"]/@href').get():
            next_page = 'https://' + self.allowed_domains[0] + response.xpath('//a[@class="next_page"]/@href').get()
            yield scrapy.Request(next_page, callback=self.parse_list)



    def parse_pic(self, response):
        print('开始处理' + response.url)
        pic = Pic()
        pic['unchanged_pic_url'] = response.xpath('//a[@class="original-file-unchanged"]/@href').extract_first()
        pic['changed_pic_url'] = response.xpath('//a[@class="original-file-changed"]/@href').extract_first()
        pic['pic_id'] = int(response.xpath('//*[@id="stats"]/ul/li[1]/text()').extract_first().replace('Id: ', ''))
        pic['rating'] = response.xpath('//li[contains(./text(), "Rating")]/text()').get().replace('Rating: ', '')
        pic['size'] = response.xpath('//*[@id="stats"]/ul/li[contains(./text(), "Size")]/text()').get().replace('Size: ', '')
        pic['source'] = response.xpath('//*[@id="stats"]/ul/li[contains(./text(), "Source")]/a/@href').get()
        pic['date'] = datetime.datetime.now()
        # pic['tags'] = '■'.join(response.xpath('//ul[@id="tag-sidebar"]/li/a[contains(./@href, "/post?tags=") and not(@class)]/text()').extract())
        pic['tags'] = response.xpath('//ul[@id="tag-sidebar"]/li/a[contains(./@href, "/post?tags=") and not(@class)]/text()').extract()
        parent = response.xpath('//div/a[contains(text(), "parent post")]/@href').get()
        if parent:
            pic['parent_pic_id'] = int(parent.replace('/post/show/', ''))
        if response.xpath('//p/span').get():
            pic['pool'] = response.xpath('//p/span/following-sibling::*/text()').get()
            pic['pool_id'] = int(response.xpath('//p/span/following-sibling::*/@href').get().replace('/pool/show/', ''))
            pic['pool_seq'] = response.xpath('//p/span/text()').get().replace('#', '')
        yield pic


