import redis.asyncio as redis
from redis.asyncio import Redis

from bald_spider import Request
from bald_spider.duplicate_filter import BaseFilter
from bald_spider.stats_collect import StatsCollector
from bald_spider.utils.log import get_logger
from bald_spider.utils.request import request_fingerprint


class AioRedisFilter(BaseFilter):

    def __init__(
        self,
        redis_key: str,
        client: Redis,
        debug: bool,
        save_fp: str,
        stats: StatsCollector,
        log_level: str
    ):
        super().__init__(
            logger=get_logger(f"{self}", log_level=log_level),
            stats=stats,
            debug=debug,
        )
        self.save_fp = save_fp
        self.redis_key = redis_key
        self.redis = client

    @classmethod
    def create_instance(cls, crawler):
        redis_url = crawler.settings.get('REDIS_URL')
        decode_responses = crawler.settings.get('DECODE_RESPONSES')
        o = cls(
            redis_key=f"{crawler.settings.get('PROJECT_NAME')}:{crawler.settings.get('REDIS_KEY')}",
            client=redis.from_url(redis_url, decode_responses=decode_responses),
            debug=crawler.settings.getbool('FILTER_DEBUG'),
            save_fp=crawler.settings.getbool('SAVE_FINGERPRINT'),
            stats=crawler.stats,
            log_level=crawler.settings.get('LOG_LEVEL'),
        )
        return o

    async def add(self, fp):
        await self.redis.sadd(self.redis_key, fp)

    async def requested(self, request: Request) -> bool:
        fp = request_fingerprint(request)
        if await self.redis.sismember(self.redis_key, fp):
            return True
        await self.add(fp)
        return False

    async def closed(self):
        if not self.save_fp:
            await self.redis.delete(self.redis_key)