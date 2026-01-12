# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/09/05

"""
重试中间件
1. 状态码不对
408 429 500 502 503 504 522 524
2. 无需重试
200-300 403 404
3. 报错的 收集错误 捕获到异常的 重新请求
"""
from asyncio.exceptions import TimeoutError
from typing import List

from aiohttp import ClientConnectorError, ClientTimeout, ClientConnectorSSLError, ClientResponseError, \
    ClientPayloadError, ClientConnectionError, ClientConnectorDNSError
from anyio import EndOfStream
from httpcore import ReadTimeout
from httpx import RemoteProtocolError, ReadError, ConnectError

from bald_spider.stats_collect import StatsCollector
from bald_spider.utils.log import get_logger

_retry_exceptions = [
    ClientConnectionError,
    ClientTimeout,
    ClientConnectorSSLError,
    ClientResponseError,
    RemoteProtocolError,
    ReadError,
    EndOfStream,
    ConnectError,
    TimeoutError,
    ClientPayloadError,
    ReadTimeout,
    ClientConnectorError,
    ClientConnectorDNSError
]


class Retry:

    def __init__(
            self,
            *,
            retry_http_codes: List,
            ignore_http_codes: List,
            max_retry_times: int,
            retry_exceptions: List,
            stats: StatsCollector,
            retry_priority: int
    ):
        self.retry_http_codes = retry_http_codes
        self.ignore_http_codes = ignore_http_codes
        self.max_retry_times = max_retry_times
        self.retry_exceptions = tuple(retry_exceptions+_retry_exceptions)
        self.stats = stats
        self.retry_priority = retry_priority
        self.logger = get_logger(self.__class__.__name__)

    @classmethod
    def create_instance(cls, crawler):
        o = cls(
            retry_http_codes=crawler.settings.getlist('RETRY_HTTP_CODES'),
            ignore_http_codes=crawler.settings.getlist('IGNORE_HTTP_CODES'),
            max_retry_times=crawler.settings.getint('MAX_RETRY_TIMES'),
            retry_exceptions=crawler.settings.getlist('RETRY_EXCEPTIONS'),
            stats=crawler.stats,
            retry_priority=crawler.settings.getint('RETRY_PRIORITY')
        )
        return o

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status_code in self.ignore_http_codes:
            return response
        if response.status_code in self.retry_http_codes:
            # 重试
            reason = f"response code: {response.status_code}"
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.retry_exceptions) and not request.meta.get('dont_retry', False):
            return self._retry(request, type(exception).__name__, spider)

    def _retry(self, request, reason, spider):
        retry_times = request.meta.get('retry_times', 0)
        if retry_times < self.max_retry_times:
            retry_times += 1
            self.logger.info(
                f'Retrying {spider} {request} {reason}(failed {retry_times} times)')
            request.meta['retry_times'] = retry_times
            request.dont_filter = True
            request.priority = request.priority+self.retry_priority
            self.stats.inc_value('retry/count')
            return request
        else:
            self.logger.warning(f'{spider} {request} {reason} retry max {self.max_retry_times} times,'
                                f'gave up.')
            return None
