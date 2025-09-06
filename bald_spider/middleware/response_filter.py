# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/09/06
from bald_spider.utils.log import get_logger
from bald_spider.exceptions import IgnoreRequest


class ResponseFilter:
    # 过滤器 将状态码是错误的Response过滤掉，不要返回引擎.
    def __init__(self, log_level, allowed_codes):
        self.logger = get_logger(self.__class__.__name__, log_level)
        self.allowed_codes = allowed_codes

    @classmethod
    def create_instance(cls, crawler):
        o = cls(
            log_level=crawler.settings.get('LOG_LEVEL'),
            allowed_codes=crawler.settings.getlist('ALLOWED_CODES')
        )
        return o

    def process_response(self, request, response, spider):
        if 200 <= response.status_code < 300:
            return response
        if response.status_code in self.allowed_codes:
            return response
        raise IgnoreRequest(f"response_status/non-200")