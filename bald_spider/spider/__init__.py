# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
from bald_spider import Request


class Spider:
    def __init__(self):
        if not hasattr(self, 'start_urls'):
            self.start_urls = []
        self.crawler = None

    @classmethod
    def create_instance(cls, crawler):
        """
        创建spider实例
        """
        o = cls()
        o.crawler = crawler
        return o

    def start_requests(self):
        """
        engine获取的是request/data 而不是url
        所以这里需要将url转换为request,封装一个request
        :return: 新的request
        """
        if self.start_urls:
            for url in self.start_urls:
                # 初始请求不能被过滤
                yield Request(url=url, dont_filter=True)
        else:
            if hasattr(self, 'start_url') and isinstance(getattr(self, 'start_url'), str):
                yield Request(getattr(self, 'start_url'))

    def parse(self, response):
        raise NotImplementedError

    def __str__(self):
        return f'<Spider {self.__class__.__name__}>'

    async def spider_opened(self):
        pass

    async def spider_closed(self):
        pass
