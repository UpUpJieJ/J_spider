# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import time

from bald_spider import Request
from bald_spider.event import spider_error
from bald_spider.spider import Spider
from tests.baidu_spider.items import BaiduItem


# 这个类需要继承于基类
class BaiduSpider(Spider):
    start_urls = ["https://www.baidu.com", "https://www.douban.com"]

    # custom_settings = {'CONCURRENCY': 10}

    @classmethod
    def create_instance(cls, crawler):
        o = cls()
        crawler.subscriber.subscribe(o.spider_error, event=spider_error)
        o.crawler = crawler
        return o

    # 重写基类的回调函数 使之可以处理多次请求
    async def parse(self, response):
        # print('>>>>>', response)
        for i in range(4):
            url = "https://www.baidu.com"
            request = Request(url=url, callback=self.page_parse)
            yield request

    def page_parse(self, response):
        # print('page_parse', response)
        for i in range(2):
            url = "https://www.baidu.com"
            request = Request(url=url, callback=self.parse_detail)
            yield request

    def parse_detail(self, response):
        # 接收download的结果
        # response 从download传来的
        # print('parse_detail', response)
        item = BaiduItem()
        item['title'] = response.xpath('//title/text()').get()
        item['url'] = response.url
        yield item

    async def spider_closed(self):
        print('爬虫结束,hhhhhhhhhhhhhhhhhhhhhhhhhh')

    async def spider_opened(self):
        print('爬虫开始,hhhhhhhhhhhhhhhhhhhhhhhhhh')

    async def spider_error(self, exc, spider):
        print(f'爬虫错误{exc}, 位于{spider}')