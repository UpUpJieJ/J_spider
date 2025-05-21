# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import asyncio
import time

import requests


class Downloader:

    def __init__(self):
        self._active = set()

    async def fetch(self, request):
        self._active.add(request)
        response = await self.download(request)
        self._active.remove(request)
        return response

    async def download(self, request):
        # response = requests.get(request.url)
        # print(response)
        await asyncio.sleep(0.1)
        return 'asdasd'

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active)