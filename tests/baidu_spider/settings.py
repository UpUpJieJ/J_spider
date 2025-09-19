PROJECT_NAME = 'BAIDU_SPIDER'
CONCURRENCY = 1
FLAG = '1'
LOG_LEVEL = 'DEBUG'
# USE_SESSION = False
# DOWNLOADER = 'bald_spider.core.downloader.httpx_downloader.HTTPXDownloader'
# STATS_DUMP = False

HEADERS = {}

MIDDLEWARES = [
    # 'baidu_spider.middleware.TestMiddleware',
    'bald_spider.middleware.default_header.DefaultHeader',
    'bald_spider.middleware.download_delay.DownloadDelay',
    'bald_spider.middleware.response_filter.ResponseFilter',
    'bald_spider.middleware.retry.Retry',
    'bald_spider.middleware.response_code.ResponseCodeStats',
    'bald_spider.middleware.request_ignore.RequestIgnore',
    # 'baidu_spider.middleware.TestMiddleware2',
    # 'baidu_spider.middleware.TestMiddleware3'
]

EXTENSIONS = [
    'bald_spider.extension.log_interval.LogInterval',
    'bald_spider.extension.log_stats.LogStats',
]

PIPELINES = [
    # 'bald_spider.pipeline.debug_pipeline.DebugPipeline',
    # 'baidu_spider.pipeline.TestPipeline',
    # 'baidu_spider.pipeline.MongoPipeline',
]


LOG_INTERVAL = 10

DOWNLOAD_DELAY = 0
RANDOMNESS = True

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}

DB_NAME = 'bald_spider'
# ALLOWED_CODES = [404]
# RETRY_EXCEPTIONS = []

# filter
FILTER_DEBUG = True
FILTER_CLS = 'bald_spider.duplicate_filter.memory_filter.MemoryFilter'

# redis_filter
REDIS_URL = "redis://localhost/0"
DECODE_RESPONSES = True
REDIS_KEY = "request_fingerprint"
SAVE_FINGERPRINT = True

REQUEST_DIR = "."