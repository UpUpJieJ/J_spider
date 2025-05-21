# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/26
#使用优先级队列
import asyncio
from bald_spider.utils.pqueue import SpiderPriorityQueue
from typing import Optional
class Scheduler:

    def __init__(self):
        self.request_queue: Optional[SpiderPriorityQueue] = None


    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_requests(self):
        # 使用了封装的自定义队列的get函数
        request = await self.request_queue.get()
        return request

    async def enqueue_requests(self,requests):
        if isinstance(requests, list):
            for request in requests:
                await self.request_queue.put(request)
        else:
            await self.request_queue.put(requests)

    def idle(self) -> bool:
        return len(self)==0

    def __len__(self):
        return self.request_queue.qsize()