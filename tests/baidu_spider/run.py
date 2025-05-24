# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import asyncio
from bald_spider.core.engine import Engine
from baidu import BaiduSpider
from bald_spider.utils.project import get_settings


async def run():
    settings = get_settings()
    baidu_spider = BaiduSpider()
    engine = Engine(settings)
    await engine.start_spider(baidu_spider)

asyncio.run(run())