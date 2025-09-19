import os
from typing import Set, Optional, TextIO

from bald_spider.duplicate_filter import BaseFilter
from bald_spider.utils.log import get_logger


class MemoryFilter(BaseFilter):

    def __init__(self, crawler):
        self.fingerprints: Set[str] = set()
        debug: bool = crawler.settings.getbool('FILTER_DEBUG')
        logger = get_logger(f"{self}", crawler.settings.get('LOG_LEVEL'))
        super().__init__(logger, crawler.stats, debug)
        self._file: Optional[TextIO] = None
        self.set_file(crawler.settings.get('REQUEST_DIR'))

    def add(self, fp: str) -> None:
        self.fingerprints.add(fp)
        if self._file:
            self._file.write(fp + '\n')

    def __contains__(self, item):
        return item in self.fingerprints

    def set_file(self, request_dir):
        if request_dir:
            self._file = open(os.path.join(request_dir, 'request_fingerprints.txt'), 'a+')
            self._file.seek(0)
            self.fingerprints.update(line.strip() for line in self._file)

    async def closed(self):
        if self._file:
            self._file.close()