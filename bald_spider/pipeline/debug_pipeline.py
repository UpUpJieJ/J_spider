from pprint import pformat

from bald_spider.items.items import Item
from bald_spider.spider import Spider
from bald_spider.utils.log import get_logger


class DebugPipeline:

    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def create_instance(cls, crawler):
        logger = get_logger(cls.__name__, crawler.settings.get('LOG_LEVEL'))
        return cls(logger)

    async def process_item(self, item: Item, spider: Spider) -> None:
        self.logger.debug(pformat(item.to_dict()))