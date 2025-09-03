PROJECT_NAME = 'BAIDU_SPIDER'
CONCURRENCY = 1
FLAG = '1'
LOG_LEVEL = 'DEBUG'
# USE_SESSION = False
# DOWNLOADER = 'bald_spider.core.downloader.httpx_downloader.HTTPXDownloader'
# STATS_DUMP = False

HEADERS = {}

MIDDLEWARES = [
    'bald_spider.middleware.request_ignore.RequestIgnore',
    'bald_spider.middleware.response_code.ResponseCodeStats',
    'bald_spider.middleware.download_delay.DownloadDelay',
    'bald_spider.middleware.default_header.DefaultHeader',
    # 'baidu_spider.middleware.TestMiddleware',
    # 'baidu_spider.middleware.TestMiddleware2',
    # 'baidu_spider.middleware.TestMiddleware3'
]

DOWNLOAD_DELAY = 0

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}