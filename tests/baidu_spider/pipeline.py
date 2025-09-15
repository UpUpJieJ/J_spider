import random

from motor.motor_asyncio import AsyncIOMotorClient

from bald_spider.event import spider_closed
from bald_spider.exceptions import ItemDiscard
from bald_spider.pipeline import BasePipeline
from bald_spider.utils.log import get_logger


class TestPipeline(BasePipeline):

    async def process_item(self, item, spider):
        # print(f'我是pipeline我正在处理{item}, 来自{spider}')
        if random.random() > 0.5:
            raise ItemDiscard(f'{item}被丢弃了')


class MongoPipeline:

    def __init__(self, conn, col):
        self.conn = conn
        self.col = col

        self.logger = get_logger(self.__class__.__name__)

    @classmethod
    def create_instance(cls, crawler):
        settings = crawler.settings
        mongo_params = settings.get('MONGO_PARAMS',None)
        db_name = settings.get('DB_NAME')
        project_name = settings.get('PROJECT_NAME')
        conn = AsyncIOMotorClient(**mongo_params) if mongo_params else AsyncIOMotorClient()
        col = conn[db_name][project_name]
        o = cls(conn, col)
        crawler.subscriber.subscribe(o.spider_closed, event=spider_closed)
        return o

    async def spider_closed(self):
        self.conn.close()
        self.logger.info('MongoDB closed')

    async def process_item(self, item, spider):
        await self.col.insert_one(item.to_dict())
        return item