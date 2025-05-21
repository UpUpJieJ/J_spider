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
                 body=''
                 ):
        self.url = url
        self.method = method
        self.headers = headers
        self.callback = callback
        self.params = params
        self.cookies = cookies
        self.priority = priority
        self.proxy = proxy
        self.body = body

    def __lt__(self, other):
        return self.priority < other.priority

