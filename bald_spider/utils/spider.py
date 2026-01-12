# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/07/14
from inspect import isgenerator, isasyncgen
from typing import Union, AsyncGenerator, Generator, Coroutine

from bald_spider import Response, Request, Item
from bald_spider.exceptions import TransformTypeError

T = Union[Request, Item, Coroutine]
SpiderOutPutType = Union[AsyncGenerator[T, None], Generator[T, None, None]]


async def transform(func_result: SpiderOutPutType, response: Response):
    def set_request(t: T) -> T:
        if isinstance(t, Request):
            t.meta['depth'] = response.meta['depth']
        return t

    try:
        if isgenerator(func_result):
            for result in func_result:
                yield set_request(result)
        elif isasyncgen(func_result):
            async for result in func_result:
                yield set_request(result)
        else:
            raise TransformTypeError('callback must return a `generator` or `async generator`')
    except Exception as e:
        yield e
