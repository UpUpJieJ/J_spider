# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/20
from typing import Optional

from httpx import AsyncClient, Timeout

from bald_spider import Response
from bald_spider.core.downloader import DownloaderBase


class HTTPXDownloader(DownloaderBase):

    def __init__(self, crawler):
        super().__init__(crawler)
        self._client: Optional[AsyncClient] = None
        self._timeout: Optional[Timeout] = None

    def open(self):
        super().open()
        request_timeout = self.crawler.settings.getint('REQUEST_TIMEOUT')
        self._timeout = Timeout(timeout=request_timeout)

    async def download(self, request) -> Optional[Response]:
        try:
            proxies = request.proxy
            async with AsyncClient(timeout=self._timeout, proxy=proxies) as client:
                self.logger.debug(f'Request Downloading: {request.method} {request.url}')
                response = await client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    cookies=request.cookies,
                    data=request.body,
                )
                body = await response.aread()
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
            status_code=response.status_code,
            cookies=response.cookies,
            body=body,
        )

