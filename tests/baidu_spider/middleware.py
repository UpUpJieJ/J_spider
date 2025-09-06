# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/26
import random

from bald_spider.exceptions import IgnoreRequest
from bald_spider.middleware import BaseMiddleware


class TestMiddleware(BaseMiddleware):
    def process_request(self, request, spider):
        retry_times = request.meta.get("retry_times", 0)
        if request.url == "https://www.baidu.com111" and retry_times > 0:
            request.url = "https://www.baidu.com"

    # def process_response(self, request, response, spider):
    #     pass

    # def process_exception(self, request, exception, spider):
    #     print("test middleware: process_exception", request, exception, spider)


class TestMiddleware2(BaseMiddleware):
    def process_request(self, request, spider):
        if request.headers is None:
            request.headers = {}
        request.headers["User-Agent"] = \
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        return request

# class TestMiddleware3(BaseMiddleware):
#     def process_response(self):
#         pass
