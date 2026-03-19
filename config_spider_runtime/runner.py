from __future__ import annotations

import asyncio
from typing import Type

from bald_spider.crawler import CrawlProcess
from bald_spider.settings.setting_manager import SettingsManager
from bald_spider.spider import Spider
from bald_spider.utils.project import merge_settings

from .factory import ConfigSpiderFactory
from .models import SpiderConfig

CONFIG_SPIDER_COLLECTOR_PIPELINE = (
    "config_spider_runtime.collector_pipeline.ConfigSpiderCollectorPipeline"
)
NOOP_FILTER_CLS = "bald_spider.duplicate_filter.noop_filter.NoopFilter"


async def _run_process(
    spider_cls: Type[Spider],
    config: SpiderConfig,
    item_collector=None,
):
    # 使用框架默认配置，不依赖项目下的 settings 模块（GUI 独立运行时无该模块）
    base_settings = SettingsManager()

    # 覆盖并发和下载延时到框架实际使用的配置项
    override = {
        "CONCURRENCY": max(1, int(config.concurrency or 1)),
        "DOWNLOAD_DELAY": max(0.0, float(config.download_delay or 0.0)),
    }
    if not config.enable_dedup:
        override["FILTER_CLS"] = NOOP_FILTER_CLS

    # 若配置了结果收集器，则启用收集管道
    if item_collector is not None:
        override["CONFIG_SPIDER_ITEM_COLLECTOR"] = item_collector
        override["PIPELINES"] = [CONFIG_SPIDER_COLLECTOR_PIPELINE]

    # 若设置了下载延时，则自动启用 DownloadDelay 中间件
    if override["DOWNLOAD_DELAY"] > 0:
        middlewares = base_settings.getlist("MIDDLEWARES", [])
        download_delay_mw = "bald_spider.middleware.download_delay.DownloadDelay"
        if download_delay_mw not in middlewares:
            middlewares.append(download_delay_mw)
        override["MIDDLEWARES"] = middlewares

    base_settings.update_values(override)
    merge_settings(spider_cls, base_settings)
    settings = base_settings

    # 从 Web/GUI 调用时不接管 SIGINT，避免 Ctrl+C 无法退出 uvicorn
    process = CrawlProcess(settings, handle_sigint=False)
    await process.crawl(spider_cls)
    await process.start()


def run_config_spider(config: SpiderConfig):
    """
    同步入口：从外部（GUI / Web）调用
    """
    spider_cls = ConfigSpiderFactory.create_spider_class(config)
    asyncio.run(_run_process(spider_cls, config))


async def run_config_spider_once(
    config: SpiderConfig, item_collector=None
):
    """
    跑配置爬虫。若传入 item_collector（如 Web 的 result_store），
    抓到的 item 会写入其中，便于导出 CSV。
    """
    spider_cls = ConfigSpiderFactory.create_spider_class(config)
    await _run_process(spider_cls, config, item_collector=item_collector)
