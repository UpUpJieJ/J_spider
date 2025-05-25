# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import time

from bald_spider import Request
from bald_spider.spider import Spider
# 这个类需要继承于基类
class BaiduSpider(Spider):

    start_urls = ["https://www.baidu.com", "https://www.douban.com"]

    custom_settings = {'CONCURRENCY': 10}

    # 重写基类的回调函数 使之可以处理多次请求
    async def parse(self, response):
        print('>>>>>', response)
        for i in range(10):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.page_parse)
            yield request

    def page_parse(self, response):
        print('page_parse', response)
        for i in range(10):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.parse_detail)
            yield request

    def parse_detail(self, response):
        print('parse_detail', response)
    # 接收download的结果


