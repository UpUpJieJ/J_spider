# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/20
from abc import abstractmethod, ABCMeta
from contextlib import asynccontextmanager
from typing import Set, Final, Optional

from typing_extensions import Self

from bald_spider import Response, Request
from bald_spider.utils.log import get_logger


class ActiveRequestManager:
    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        self._active.add(request)

    def remove(self, request):
        self._active.remove(request)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request)
        finally:
            self.remove(request)

    def __len__(self):
        return len(self._active)


class DownloaderMeta(ABCMeta):
    def __subclasscheck__(self, subclass):
        required_method = ('fetch', 'download', 'create_instance', 'close', 'idle')
        is_subclass = all(
            hasattr(subclass, method) and callable(getattr(subclass, method, None)) for method in required_method)
        return is_subclass


class DownloaderBase(metaclass=DownloaderMeta):
    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))

    @classmethod
    def create_instance(cls, *args, **kwargs) -> Self:
        return cls(*args, **kwargs)

    def open(self) -> None:
        self.logger.info(f"{self.crawler.spider} <downloader class: {type(self).__name__}> "
                         f"<concurrency: {self.crawler.settings.getint('CONCURRENCY')}>")

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request)
            return response

    @abstractmethod
    async def download(self, request: Request) -> Optional[Response]:
        pass

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len(self._active)

    async def close(self) -> None:
        pass
