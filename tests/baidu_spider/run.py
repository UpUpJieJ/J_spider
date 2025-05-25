# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import asyncio
import time

from bald_spider.crawler import CrawlProcess
from tests.baidu_spider.spiders.baidu import BaiduSpider
from tests.baidu_spider.spiders.baidu2 import BaiduSpider2
from bald_spider.utils.project import get_settings


async def run():
    settings = get_settings()
    process = CrawlProcess(settings)
    await process.crawl(BaiduSpider)
    await process.crawl(BaiduSpider2)
    await process.start()



    # baidu_spider = BaiduSpider()
    # engine = Engine(settings)
    # await engine.start_spider(baidu_spider)
s = time.time()
asyncio.run(run())
print(time.time() - s)