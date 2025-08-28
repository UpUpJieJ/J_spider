# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/26
from bald_spider import Response, Request


class BaseMiddleware:
    def process_request(self, request, spider) -> None | Request | Response:
        pass

    def process_response(self, request, response, spider) -> Request | Response:
        pass

    def process_exception(self, request, exception, spider) -> None | Request | Response:
        pass

    @classmethod
    def create_instance(cls, crawler):
        return cls()