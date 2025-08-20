# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/18
import re
from typing import Dict
import ujson
from bald_spider import Request
from bald_spider.exceptions import DecodeError
from urllib.parse import urljoin as _urljoin
from parsel import Selector


class Response:
    def __init__(
            self,
            url: str,
            *,
            headers: Dict,
            request: Request,
            status_code: int = 200,
            cookies: Dict,
            encoding: str = "utf-8",
            body: bytes = b"",
    ):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.cookies = cookies
        self.encoding = encoding
        self.request = request
        self.body = body
        self._text_cache = None
        self._selector = None

    @property
    def text(self):
        # 检查是否已有缓存
        if self._text_cache is not None:
            return self._text_cache

        try:
            text = self.body.decode(self.encoding)
        except UnicodeDecodeError:
            try:
                _encoding_re = re.compile(r'charset=([\w-]+)', flags=re.I)
                _encoding_string = self.headers.get('content-type', '') or self.headers.get('Content-Type', '')
                _encoding = _encoding_re.search(_encoding_string)
                if _encoding:
                    text = self.body.decode(_encoding.group(1))
                else:
                    raise DecodeError(f'{self.request} {self.request.encoding} error.')
            except UnicodeDecodeError as exc:
                raise UnicodeDecodeError(
                    exc.encoding, exc.object, exc.end, exc.start, f"{self.request}"
                )

        # 缓存结果
        self._text_cache = text
        return text

    def xpath(self, xpath_string):
        if self._selector is None:
            self._selector = Selector(self.text)
        return self._selector.xpath(xpath_string)

    def json(self):
        return ujson.loads(self.text)

    def urljoin(self, url):
        return _urljoin(self.url, url)

    def __str__(self):
        return f'<{self.status_code}> {self.url}>'

    @property
    def meta(self):
        return self.request.meta
