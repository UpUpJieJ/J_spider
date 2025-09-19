# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/26
# 使用优先级队列

from bald_spider.utils.pqueue import SpiderPriorityQueue
from bald_spider.utils.log import get_logger
from typing import Optional, Callable

from bald_spider.utils.project import load_class, common_call


class Scheduler:

    def __init__(self, crawler, dupe_filter, stats, log_level):
        self.crawler = crawler
        self.request_queue: Optional[SpiderPriorityQueue] = None
        self.logger = get_logger(self.__class__.__name__, log_level=log_level)
        self.dupe_filter = dupe_filter
        self._stats = stats

    @classmethod
    def create_instance(cls, crawler):
        filter_cls = load_class(crawler.settings.get('FILTER_CLS'))
        o = cls(
            crawler=crawler,
            dupe_filter=filter_cls.create_instance(crawler),
            stats=crawler.stats,
            log_level=crawler.settings.get('LOG_LEVEL'),
        )
        return o

    def open(self):
        self.request_queue = SpiderPriorityQueue()
        self.logger.info(f"request filter: {self.dupe_filter}")

    async def next_requests(self):
        # 使用了封装的自定义队列的get函数
        request = await self.request_queue.get()
        return request

    async def enqueue_requests(self, request):
        # request中 dont_filter 无需过滤 为False则需要参加过滤
        if (
            not request.dont_filter
            and await common_call(self.dupe_filter.requested, request)
        ):
            self.dupe_filter.log_stats(request)
            return False
        await self.request_queue.put(request)
        return True

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()

    async def close(self):
        if isinstance(closed := getattr(self.dupe_filter, 'closed', None), Callable):
            await closed()
