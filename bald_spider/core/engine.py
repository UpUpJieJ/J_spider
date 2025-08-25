# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/06/22
import asyncio
from typing import Optional, Generator, Callable

from bald_spider import Request, Item
from bald_spider.core.downloader import DownloaderBase
from bald_spider.core.processor import Processor
from bald_spider.core.scheduler import Scheduler
from bald_spider.exceptions import TransformTypeError, OutputTypeError
from bald_spider.spider import Spider
from inspect import iscoroutine, isgenerator, isasyncgen
from bald_spider.utils.spider import transform
from bald_spider.task_manager import TaskManager
from bald_spider.utils.log import get_logger
from bald_spider.utils.project import load_class


class Engine:

    def __init__(self, crawler):
        self.settings = crawler.settings
        self.logger = get_logger(self.__class__.__name__)
        self.crawler = crawler
        self.downloader: Optional[DownloaderBase] = None
        self.scheduler: Optional[Scheduler] = None
        self.processor: Optional[Processor] = None
        self.spider: Optional[Spider] = None
        self.start_requests: Optional[Generator] = None
        self.task_manager: TaskManager = TaskManager(self.settings.getint('CONCURRENCY'))
        self.running = False

    def _get_downloader(self):
        downloader_cls = load_class(self.settings.get('DOWNLOADER'))
        if not issubclass(downloader_cls, DownloaderBase):
            raise TypeError(f"The downloader class {self.settings.get('DOWNLOADER')} "
                            f"doesn't fully implemented required interface.")
        return downloader_cls

    # 接受一个spider对象并且启动实例
    async def start_spider(self, spider):
        self.running = True
        self.logger.info(f"info Starting spider (project name: {self.settings.get('PROJECT_NAME')})")
        self.logger.debug(f"debug Starting spider (project name: {self.settings.get('PROJECT_NAME')})")
        self.spider = spider
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, "open"):
            self.scheduler.open()
        downloader_cls = self._get_downloader()
        self.downloader = downloader_cls.create_instance(self.crawler)
        if hasattr(self.downloader, "open"):
            self.downloader.open()
        self.processor = Processor(self.crawler)
        self.start_requests = iter(spider.start_requests())
        # await self.crawl()
        await self._open_spider()

    async def _open_spider(self):
        # 创建task
        crawling = asyncio.create_task(self.crawl())
        # 做额外事情
        await crawling

    async def crawl(self):
        """
        下载逻辑
        """
        while self.running:
            # 出队
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    start_request = next(self.start_requests)
                    # self.downloader.download(start_request)
                except StopIteration:
                    self.start_requests = None
                except Exception as exc:
                    # 1 发起请求的task 运行完毕
                    # 2 调度器是否空闲
                    # 3 下载器是否空闲
                    if not await self._exit():
                        continue
                    self.running = False
                    if self.start_requests is not None:
                        self.logger.warning(f"Error during start_requests: {exc}")
                else:  # 不直接下载 使用调度器 入队
                    await self.enqueue_requests(start_request)
        if not self.running:
            await self.close_spider()

    async def _crawl(self, request):
        # todo 实现并发
        async def crawl_task():
            outputs = await self._fetch(request)
            # 处理outputs
            if outputs:
                await self._handle_spider_outputs(outputs)

        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

    # 获取下载请求 就可以实现并发
    async def _fetch(self, request):
        # 把结果回调回spider看是否还是个请求
        # todo 失败的处理
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            # print(type(callback(_response))) 可能是生成器 异步生成器 也可能是普通函数NoneType
            if _outputs := callback(_response):
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    return transform(_outputs)

        _response = await self.downloader.fetch(request)
        if _response is None:
            return None
        outputs = await _success(_response)
        return outputs

    # 入队逻辑
    async def enqueue_requests(self, request):
        await self._schedule_request(request)

    async def _schedule_request(self, request):
        # todo 去重
        await self.scheduler.enqueue_requests(request)

    # 出队下载逻辑
    async def _get_next_request(self):
        return await self.scheduler.next_requests()

    async def _handle_spider_outputs(self, outputs):
        async for spider_output in outputs:
            # 处理是请求还是数据
            if isinstance(spider_output, (Request, Item)):
                await self.processor.enqueue(spider_output)
            else:
                raise OutputTypeError(
                    f"Spider {self.spider} must return `Request` or `item`, but get {type(spider_output)}")

    async def _exit(self):
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done() and self.processor.idle():
            return True
        return False

    async def close_spider(self):
        await self.downloader.close()
