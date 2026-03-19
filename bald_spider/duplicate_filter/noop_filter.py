from bald_spider.duplicate_filter import BaseFilter
from bald_spider.utils.log import get_logger


class NoopFilter(BaseFilter):
    """
    No-op duplicate filter.
    Always treats requests as unseen.
    """

    def __init__(self, crawler):
        debug: bool = crawler.settings.getbool("FILTER_DEBUG")
        logger = get_logger(f"{self}", crawler.settings.get("LOG_LEVEL"))
        super().__init__(logger, crawler.stats, debug)

    def add(self, fp: str) -> None:
        # Disabled deduplication: do not store fingerprints.
        return None

    def __contains__(self, item):
        return False
