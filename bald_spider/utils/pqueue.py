# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/26
import asyncio
from asyncio import PriorityQueue,TimeoutError

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super(SpiderPriorityQueue, self).__init__(maxsize=maxsize)

    async def get(self):
        f = super().get()
        try:
            # 取出来的是协程对象
            return await asyncio.wait_for(f, timeout=0.05)
        except TimeoutError:
            return None
