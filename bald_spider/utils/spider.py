# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/07/14
from inspect import isgenerator, isasyncgen

from bald_spider.exceptions import TransformTypeError


async def transform(func_result):
    if isgenerator(func_result):
        for result in func_result:
            yield result
    elif isasyncgen(func_result):
        async for result in func_result:
            yield result
    else:
        raise TransformTypeError('callback must return a `generator` or `async generator`')