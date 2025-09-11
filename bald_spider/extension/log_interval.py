# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/09/09
import asyncio

from bald_spider.event import spider_opened, spider_closed
from bald_spider.utils.log import get_logger


class LogInterval:

    def __init__(self, crawler):
        self.stats = crawler.stats
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))
        self.item_count = 0
        self.response_count = 0
        self.seconds = crawler.settings.getint('LOG_INTERVAL')
        self.interval = int(self.seconds/60) if self.seconds % 60 == 0 else self.seconds
        self.interval = "" if self.interval == 1 else self.interval
        self.unit = "min" if self.seconds % 60 == 0 else "s"
        self.task = None

    @classmethod
    def create_instance(cls, crawler):
        o = cls(crawler)
        crawler.subscriber.subscribe(o.spider_opened, event=spider_opened)
        crawler.subscriber.subscribe(o.spider_closed, event=spider_closed)
        return o

    async def spider_opened(self):
        self.task = asyncio.create_task(self.interval_log())
        await self.task

    async def spider_closed(self):
        if self.task:
            self.task.cancel()

    async def interval_log(self):
        while True:
            last_item_count = self.stats.get_value('item_successful_count', 0)
            last_response_count = self.stats.get_value('response_received_count', 0)
            item_rate = last_item_count - self.item_count
            response_rate = last_response_count - self.response_count
            self.item_count = last_item_count
            self.response_count = last_response_count
            self.logger.info(f"Crawled {last_response_count} pages (at {response_rate} pages/{self.interval}{self.unit}),"
                             f"Got {last_item_count} items (at {item_rate} items/{self.interval}{self.unit})")
            await asyncio.sleep(self.seconds)
