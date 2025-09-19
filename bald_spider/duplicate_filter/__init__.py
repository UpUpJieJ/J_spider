from abc import ABC, abstractmethod

from bald_spider import Request
from bald_spider.utils.request import request_fingerprint


class BaseFilter(ABC):
    def __init__(self, logger, stats, debug: bool):
        """
        :param logger: Logger instance for logging msg.
        :param stats: StatsCollector instance for recording statistics.
        :param debug: A boolean indicating if debug mode is on.
        """
        self.logger = logger
        self.stats = stats
        self.debug = debug

    @classmethod
    def create_instance(cls, *args, **kwargs) -> "BaseFilter":
        return cls(*args, **kwargs)

    def requested(self, request: Request) -> bool:
        fp = request_fingerprint(request)
        if fp in self:
            return True
        self.add(fp)
        return False

    @abstractmethod
    def add(self, fp: str) -> None:
        raise NotImplementedError

    def log_stats(self, request: Request) -> None:
        if self.debug:
            self.logger.debug(f"Filtered duplicate request: {request}")
        self.stats.inc_value(f"{self}/filtered")

    def __str__(self):
        return self.__class__.__name__