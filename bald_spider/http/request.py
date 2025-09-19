# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/07/13
from typing import Dict, Optional, Callable


class Request:
    def __init__(self,
                 url: str,*,
                 headers: Optional[Dict] = None,
                 callback: Optional[Callable] = None,
                 priority: int = 0,
                 method: str = 'GET',
                 cookies: Optional[Dict] = None,
                 params: Optional[Dict] = None,
                 proxy: Optional[Dict] = None,
                 body: Optional[Dict] = None,
                 encoding='utf-8',
                 meta: Optional[Dict] = None,
                 dont_filter: bool = False,
                 ):
        self.url = url
        self.method = method.lower()
        self.headers = headers if headers else {}
        self.callback = callback
        self.params = params
        self.cookies = cookies
        self.priority = priority
        self.proxy = proxy
        self.body = body
        self.encoding = encoding
        self.dont_filter = dont_filter
        self._meta = meta if meta else {}

    def __str__(self):
        return f'{self.url} {self.method}'

    def __lt__(self, other):
        return self.priority < other.priority

    @property
    def meta(self):
        return self._meta