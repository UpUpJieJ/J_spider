from bald_spider import event
from bald_spider.utils.date import now, date_delta


class LogStats:
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def create_instance(cls, crawler):
        o = cls(crawler.stats)
        crawler.subscriber.subscribe(o.spider_opened, event=event.spider_opened)
        crawler.subscriber.subscribe(o.spider_closed, event=event.spider_closed)
        crawler.subscriber.subscribe(o.item_successful, event=event.item_successful)
        crawler.subscriber.subscribe(o.item_discard, event=event.item_discard)
        crawler.subscriber.subscribe(o.request_scheduled, event=event.request_scheduled)
        crawler.subscriber.subscribe(o.response_received, event=event.response_received)
        return o

    async def request_scheduled(self, request, spider):
        self.stats.inc_value('request_scheduled_count', start=0)

    async def response_received(self, response, spider):
        self.stats.inc_value('response_received_count')

    async def item_successful(self, item, spider):
        self.stats.inc_value('item_successful_count')

    async def item_discard(self, item, exc, spider):
        self.stats.inc_value('item_discard_count')
        reason = exc.message
        if reason:
            self.stats.inc_value(f'item_discard_count/{reason}')

    async def spider_opened(self):
        self.stats['start_time'] = now()

    async def spider_closed(self):
        self.stats['end_time'] = now()
        self.stats['cost_time(s)'] = date_delta(self.stats['start_time'], self.stats['end_time'])


