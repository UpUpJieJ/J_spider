# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/06/01
from asyncio import Queue
from typing import Union

from bald_spider import Item, Request


class Processor:

    def __init__(self, crawler):
        self.queue: Queue = Queue()
        self.crawler = crawler
    async def process(self):
        while not self.idle():
            output = await self.queue.get()
            if isinstance(output, Request):
                await self.crawler.engine.enqueue_requests(output)
            else:
                assert isinstance(output, Item), 'output must be Request or Item'
                await self._process_item(output)

    async def _process_item(self, item):
        print(item)

    async def enqueue(self, output: Union[Request, Item]):
        await self.queue.put(output)
        await self.process()

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()

