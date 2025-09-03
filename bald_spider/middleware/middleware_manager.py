# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/26
import asyncio
from collections import defaultdict
from pprint import pformat
from types import MethodType
from typing import List, Dict, Callable, Optional

from bald_spider import Request, Response
from bald_spider.event import ignore_request, response_received
from bald_spider.exceptions import MiddlewareInitError, InvalidOutputError, RequestMethodError, IgnoreRequest, \
    NotConfigured
from bald_spider.middleware import BaseMiddleware
from bald_spider.utils.log import get_logger
from bald_spider.utils.project import load_class, common_call


class MiddlewareManager:
    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))
        self.middlewares: List = []
        self.method: Dict[str, List[MethodType]] = defaultdict(list)
        middlewares = self.crawler.settings.getlist('MIDDLEWARES')
        self._add_middleware(middlewares)
        self._add_method()

        self.download_method: Callable = crawler.engine.downloader.download
        self._stats = crawler.stats

    async def _process_request(self, request: Request):
        for method in self.method['process_request']:
            result = await common_call(method, request, self.crawler.spider)
            if result is None:
                continue
            if isinstance(result, (Request, Response)):
                return result
            raise InvalidOutputError(
                f'{result.__qualname__} must return None, Request or Response, but got {type(result).__name__}.')
        return await self.download_method(request)

    async def _process_response(self, request: Request, response: Response):
        for method in reversed(self.method['process_response']):
            try:
                response = await common_call(method, request, response, self.crawler.spider)
            except IgnoreRequest as exc:
                _ = asyncio.create_task(
                    self.crawler.subscriber.notify(ignore_request, exc, request, self.crawler.spider))
                return None
            else:
                if isinstance(response, Request):
                    return response
                if isinstance(response, Response):
                    continue
                raise InvalidOutputError(
                    f'{response.__qualname__} must return Request or Response, but got {type(response).__name__}.')
        return response

    async def _process_exception(self, request: Request, exception: Exception):
        for method in reversed(self.method['process_exception']):
            response = await common_call(method, request, exception, self.crawler.spider)
            if response is None:
                continue
            if isinstance(response, (Request, Response)):
                return response
            if response:
                break
            raise InvalidOutputError(
                f'{response.__qualname__} must return None, Request or Response, but got {type(response).__name__}.')
        else:
            raise exception

    async def download(self, request: Request) -> Optional[Response]:
        """ 下载器中调用此方法 """
        try:
            response = await self._process_request(request)
        except KeyError:
            raise RequestMethodError(f'{request.method.lower()} is not supported.')
        except IgnoreRequest as exc:
            _ = asyncio.create_task(self.crawler.subscriber.notify(ignore_request, exc, request, self.crawler.spider))
            response = await self._process_exception(request, exc)
        except Exception as exc:
            self._stats.inc_value(f'download_error/{exc.__class__.__name__}')
            response = await self._process_exception(request, exc)
        else:
            _ = asyncio.create_task(self.crawler.subscriber.notify(response_received, response, self.crawler.spider))
            self.crawler.stats.inc_value('response_received_count')
        if isinstance(response, Response):
            response = await self._process_response(request, response)
        if isinstance(response, Request):
            await self.crawler.engine.enqueue_requests(response)
            return None
        return response

    def _add_method(self):
        for middleware in self.middlewares:
            if hasattr(middleware, 'process_request'):
                if self._validate_method('process_request', middleware):
                    self.method.setdefault('process_request', []).append(middleware.process_request)
            if hasattr(middleware, 'process_response'):
                if self._validate_method('process_response', middleware):
                    self.method.setdefault('process_response', []).append(middleware.process_response)
            if hasattr(middleware, 'process_exception'):
                if self._validate_method('process_exception', middleware):
                    self.method.setdefault('process_exception', []).append(middleware.process_exception)

    def _add_middleware(self, middlewares):
        enabled_middlewares = [m for m in middlewares if self._validate_middleware(m)]
        if enabled_middlewares:
            self.logger.info(f"Enabled middlewares: \n {pformat(enabled_middlewares)}")
        else:
            self.logger.info("No middlewares enabled")

    def _validate_middleware(self, middleware):
        middleware_cls = load_class(middleware)
        if not hasattr(middleware_cls, 'create_instance'):
            raise MiddlewareInitError(f"Middleware init failed, "
                                      f"{middleware} must inherit from BaseMiddleware"
                                      f" or have a create_instance method")
        try:
            instance = middleware_cls.create_instance(self.crawler)
            self.middlewares.append(instance)
            return True
        except NotConfigured:
            return False


    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @staticmethod
    def _validate_method(method_name, middleware) -> bool:
        method = getattr(type(middleware), method_name)
        base_method = getattr(BaseMiddleware, method_name)
        return False if method == base_method else True
