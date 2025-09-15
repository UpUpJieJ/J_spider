from bald_spider.items.items import Item
from bald_spider.utils.log import get_logger


class BasePipeline:

    def __init__(self, crawler):
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))
        self.crawler = crawler

    def process_item(self, item: Item, spider) -> None:
        raise NotImplementedError

    @classmethod
    def create_instance(cls, crawler):
        return cls(crawler)