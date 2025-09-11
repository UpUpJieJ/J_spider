# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/26
# 使用优先级队列
import asyncio

from bald_spider.event import request_scheduled
from bald_spider.utils.pqueue import SpiderPriorityQueue
from bald_spider.utils.log import get_logger
from typing import Optional


class Scheduler:

    def __init__(self, crawler):
        self.crawler = crawler
        self.request_queue: Optional[SpiderPriorityQueue] = None
        self.logger = get_logger(self.__class__.__name__, log_level=crawler.settings.get('LOG_LEVEL'))

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_requests(self):
        # 使用了封装的自定义队列的get函数
        request = await self.request_queue.get()
        return request

    async def enqueue_requests(self, request):
        await self.request_queue.put(request)
        _ = asyncio.create_task(self.crawler.subscriber.notify(request_scheduled, request, self.crawler.spider))

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()

