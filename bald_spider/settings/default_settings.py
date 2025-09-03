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

DOWNLOAD_DELAY = 0
RANDOMNESS = True
RANDOM_RANGE = (0.75, 1.25)