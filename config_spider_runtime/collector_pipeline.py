# encoding: utf-8
"""
将配置爬虫抓到的 item 写入 CONFIG_SPIDER_ITEM_COLLECTOR（供 Web 导出 CSV 等）。
"""
from __future__ import annotations

from bald_spider.utils.log import get_logger


class ConfigSpiderCollectorPipeline:
    """把 item 写入 settings 中的 CONFIG_SPIDER_ITEM_COLLECTOR（若有）。"""

    @classmethod
    def create_instance(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler
        self.collector = crawler.settings.get("CONFIG_SPIDER_ITEM_COLLECTOR")
        self.logger = get_logger(
            self.__class__.__name__, crawler.settings.get("LOG_LEVEL")
        )

    async def process_item(self, item, spider):
        if self.collector is not None and hasattr(self.collector, "add_item"):
            item_dict = item.to_dict() if hasattr(item, "to_dict") else dict(item)
            self.collector.add_item(item_dict)
        return item
