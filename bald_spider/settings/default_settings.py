# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/21
"""
default config
"""

CONCURRENCY = 16

LOG_LEVEL = 'INFO'

LOG_INTERVAL = 60

VERIFY_SSL = True

REQUEST_TIMEOUT = 60

USE_SESSION = True

DOWNLOADER = 'bald_spider.core.downloader.aiohttp_downloader.AioDownloader'

STATS_DUMP = True
# download_delay
DOWNLOAD_DELAY = 0
RANDOMNESS = True
RANDOM_RANGE = (0.75, 1.25)

# retry
RETRY_HTTP_CODES = [408, 429, 500, 502, 503, 504, 522, 524]
IGNORE_HTTP_CODES = [403, 404]
MAX_RETRY_TIMES = 2
ALLOWED_CODES = []