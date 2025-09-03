# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/09/01
from bald_spider.event import ignore_request
from bald_spider.utils.log import get_logger
from bald_spider.exceptions import IgnoreRequest


class RequestIgnore:
    def __init__(self, stats, log_level):
        self.logger = get_logger(self.__class__.__name__, log_level)
        self.stats = stats

    @classmethod
    def create_instance(cls, crawler):
        o = cls(
            stats=crawler.stats,
            log_level=crawler.settings.get("LOG_LEVEL")
        )
        crawler.subscriber.subscribe(o.ignore_request, event=ignore_request)
        return o

    async def ignore_request(self, exc, request, _spider):
        self.logger.info(f'Ignore request: {request}')
        self.stats.inc_value('ignore_request_count')
        reason = exc.message
        if reason:
            self.stats.inc_value('ignore_request_count/%s' % reason)

    @staticmethod
    def process_exception(_request, exception, _spider):
        if isinstance(exception, IgnoreRequest):
            return True