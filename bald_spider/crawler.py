# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/24
import asyncio
from typing import Type, Final, Set, Optional

from bald_spider.core.engine import Engine
from bald_spider.exceptions import SpiderTypeError
from bald_spider.settings.setting_manager import SettingsManager
from bald_spider.spider import Spider
from bald_spider.utils.project import merge_settings


class Crawler:
    """
    组织spider和engine
    """

    def __init__(self, spider_cls, settings=None):
        self.spider_cls = spider_cls
        self.spider: Optional[Spider] = None
        self.engine: Optional[Engine] = None
        self.settings: SettingsManager = settings.copy()
    async def crawl(self) -> None:
        """
        启动爬虫
        """
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        await self.engine.start_spider(self.spider)

    def _create_spider(self):
        spider = self.spider_cls.create_instance(self)
        self._set_spider(spider)
        return spider

    def _create_engine(self):
        engine = Engine(self)
        return engine

    def _set_spider(self, spider):
        merge_settings(spider, self.settings)



class CrawlProcess:

    def __init__(self, settings=None):
        self.crawlers: Final[Set] = set()
        self._active: Final[Set] = set()
        self.settings: SettingsManager = settings

    async def crawl(self, spider: Type[Spider]):
        # 通过这个spider创建crawler
        crawler: Crawler = self._create_crawler(spider)
        self.crawlers.add(crawler)
        task = await self._crawl(crawler)
        self._active.add(task)

    @staticmethod
    async def _crawl(crawler: Crawler):
        return asyncio.create_task(crawler.crawl())

    async def start(self):
        await asyncio.gather(*self._active)
    def _create_crawler(self, spider_cls) -> Crawler:
        if isinstance(spider_cls, str):
            raise SpiderTypeError(f'{type(self)}.crwal args: must be a Spider class')
        crawler = Crawler(spider_cls, self.settings)
        return crawler
