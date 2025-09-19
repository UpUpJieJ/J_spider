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
    # user_agent = '123Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
    # headers = {
    #     'Accept': '123text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'Accept-Language': 'zh-CN,zh;q=0.9',
    #  }
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
            # url = "https://www.httpbin.org/404"
            url = "https://www.baidu.com"
            request = Request(url=url, callback=self.page_parse,dont_filter=True)
            yield request

    def page_parse(self, response):
        # print('page_parse', response)
        for i in range(2):
            url = "https://www.baidu.com"
            request = Request(url=url, callback=self.parse_detail, dont_filter=False)
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