# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/09/02
from bald_spider.exceptions import NotConfigured
from bald_spider.utils.log import get_logger
from asyncio import sleep
from random import uniform


class DownloadDelay:

    def __init__(self, settings, log_level):
        self.delay = settings.getfloat('DOWNLOAD_DELAY')
        if not self.delay:
            raise NotConfigured
        self.randomness = settings.getbool('DOWNLOAD_DELAY')
        self.floor, self.upper = settings.getlist('RANDOM_RANGE')
        self.logger = get_logger(self.__class__.__name__, log_level)

    @classmethod
    def create_instance(cls, crawler):
        o = cls(
            log_level=crawler.settings.get("LOG_LEVEL"),
            settings=crawler.settings
        )
        return o

    async def process_request(self, _request, _spider):
        if self.delay:
            delay = uniform(self.floor*self.delay, self.upper*self.delay)
            self.logger.debug(f"Sleeping for random time {round(delay, 3)} seconds")
            await sleep(delay)
        else:
            self.logger.debug(f"Sleeping for {self.delay} seconds")
            await sleep(self.delay)