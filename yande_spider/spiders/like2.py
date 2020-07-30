# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import FormRequest

"""
第二种登陆方式
"""
class LikeSpider(CrawlSpider):
    name = 'like2'

    allowed_domains = ['yande.re']
    start_urls = ['https://yande.re/user/login']

    def parse(self, response):
        token = response.xpath('//*[@id="user-login"]/form/input[@name="authenticity_token"]/@value').get()
        print(token)
        form_data = {
            'authenticity_token': token,
            'user[name]': 'kamiyamashiki',
            'user[password]': '15931596981',
            'commit': 'Login'
        }
        yield scrapy.FormRequest('https://yande.re/user/authenticate', formdata=form_data, callback=self.after_login) # 会重定向到用户主页

    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_list', follow=True),
    # )




    def after_login(self, response):
        # yield scrapy.Request('https://yande.re/user/home', callback=self.parse_list)
        print(response.body)
        yield scrapy.Request('https://yande.re/post?page=1&tags=vote%3A%3E%3D1%3Akamiyamashiki+order%3Avote', callback=self.parse_list)

    def parse_list(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        print(response.body)
        return item

    def parse_pic(self, response):
        pass
