# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
from contextlib import asynccontextmanager
from typing import Set, Final, Optional
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse, TraceConfig

from bald_spider import Response
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


class Downloader:

    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self._use_session: Optional[bool] = None

        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))
        self.request_method = {
            'get': self._get,
            'post': self._post,
        }

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class: {type(self).__name__}>"
                         f"<concurrency: {self.crawler.settings.getint('CONCURRENCY')}>")
        request_timeout = self.crawler.settings.getint('REQUEST_TIMEOUT')
        self._verify_ssl = self.crawler.settings.getbool('VERIFY_SSL')
        self._timeout = ClientTimeout(total=request_timeout)
        self._use_session = self.crawler.settings.getbool('USE_SESSION')
        if self._use_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            trace_config = TraceConfig()
            trace_config.on_request_start.append(self.request_start)
            self.session = ClientSession(connector=self.connector, timeout=self._timeout, trace_configs=[trace_config])

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request)
            return response

    async def download(self, request) -> Response:
        try:
            if self._use_session:
                response = await self.send_request(self.session, request)
                body = await response.read()
            else:
                # 每次请求都使用新的 session
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                trace_config = TraceConfig()
                trace_config.on_request_start.append(self.request_start)
                async with ClientSession(
                        connector=connector, timeout=self._timeout, trace_configs=[trace_config]
                ) as session:
                    response = await self.send_request(session, request)
                    body = await response.read()

        except Exception as e:
            self.logger.error(f'Error while downloading {request.url}: {e}')
            raise e
        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            request=request,
            status_code=response.status,
            cookies=response.cookies,
            body=body,
        )

    async def send_request(self, session, request) -> ClientResponse:
        return await self.request_method[request.method.lower()](session, request)

    @staticmethod
    async def _get(session, request) -> ClientResponse:
        return await session.get(
            request.url,
            headers=request.headers,
            cookies=request.cookies,
            proxy=request.proxy,
        )

    @staticmethod
    async def _post(session, request) -> ClientResponse:
        return await session.get(
            request.url,
            data=request.body,
            headers=request.headers,
            cookies=request.cookies,
            proxy=request.proxy,
        )

    async def request_start(self, _session, _trace_config_ctx, params):
        self.logger.debug(f'Request Downloading: {params.method} {params.url}')

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()
