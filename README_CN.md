# bald_spider

一个基于 asyncio 构建的异步、可扩展的网络爬虫框架。灵感来自 Scrapy，但采用了现代化的 Python 架构设计。

## 特性

- **异步高性能**：完全基于 asyncio 构建，支持高并发爬取
- **事件驱动架构**：采用发布-订阅模式，实现清晰的职责分离
- **可扩展设计**：易于添加自定义组件、中间件和管道
- **去重过滤**：内置支持，可选择 Redis 后端
- **自动重试**：可配置的失败请求重试机制
- **中间件系统**：请求/响应处理钩子
- **管道系统**：灵活的项目处理和存储
- **统计收集**：内置统计跟踪和报告
- **配置管理**：灵活的设置系统，支持项目级和爬虫级配置

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd bald_spider

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 创建第一个爬虫

```python
from bald_spider import Spider, Request
from bald_spider.items import Item, Field

class ProductItem(Item):
    name = Field()
    price = Field()
    url = Field()

class MySpider(Spider):
    name = "product_spider"
    start_urls = ["https://example.com/products"]

    async def parse(self, response):
        for product in response.css('.product'):
            yield ProductItem(
                name=product.css('.name::text').get(),
                price=product.css('.price::text').get(),
                url=product.css('a::attr(href)').get()
            )
```

### 2. 运行爬虫

```python
from bald_spider.crawler import CrawlProcess

# 创建并运行爬虫
process = CrawlProcess()
process.crawl(MySpider)
process.start()
```

### 3. 使用管道

```python
# 定义处理项目的管道
class MyPipeline:
    async def process_item(self, item, spider):
        # 保存到数据库
        await save_to_database(item)
        return item

    async def open_spider(self, spider):
        # 初始化数据库连接
        await db.connect()

    async def close_spider(self, spider):
        # 清理资源
        await db.close()
```

## 架构概述

### 核心组件

- **Engine（引擎）**：爬虫系统的核心，协调所有组件
- **Scheduler（调度器）**：管理请求队列和优先级
- **Downloader（下载器）**：处理 HTTP 请求（支持 aiohttp 和 httpx）
- **Processor（处理器）**：处理响应并生成新请求/项目
- **Spider（爬虫）**：定义爬取逻辑的基类
- **Pipeline（管道）**：处理和存储爬取的数据
- **Middleware（中间件）**：请求/响应处理钩子

### 数据结构

- **Request**：表示带有元数据的 HTTP 请求
- **Response**：处理具有解析功能的 HTTP 响应
- **Item**：用于爬取数据的字典式容器，支持字段验证

### 事件系统

框架使用发布-订阅模式进行组件间的通信：

```python
# 订阅事件
spider.subscribe('item_scraped', item_handler)
spider.subscribe('request_failed', error_handler)
```

## 配置

设置通过分层系统进行管理：

```python
# 默认设置
CONCURRENT_REQUESTS = 16  # 并发请求数
DOWNLOAD_TIMEOUT = 60      # 下载超时时间（秒）
RETRY_HTTP_CODES = [500, 502, 503, 504]  # 重试的 HTTP 状态码
RANDOMIZE_DOWNLOAD_DELAY = True  # 随机延迟下载
DUPEFILTER_CLASS = 'bald_spider.duplicate_filter.RFPDupeFilter'  # 去重过滤器
```

## 高级功能

### 中间件

```python
class CustomDownloaderMiddleware:
    async def process_request(self, request, spider):
        # 下载前修改请求
        request.headers['User-Agent'] = '我的爬虫'
        return request

    async def process_response(self, response, request, spider):
        # 下载后处理响应
        return response
```

### 自定义去重过滤器

```python
from bald_spider.duplicate_filter import BaseDupeFilter

class MyDupeFilter(BaseDupeFilter):
    async def request_seen(self, request):
        # 实现你的去重逻辑
        return False
```

### 统计收集

```python
# 访问统计信息
stats = spider.stats
print(stats.get_value('item_scraped_count'))  # 爬取的项目数
print(stats.get_value('requests_count'))      # 请求数
```

## 完整爬虫示例

```python
import asyncio
from bald_spider import Spider, Request
from bald_spider.items import Item, Field

class NewsItem(Item):
    title = Field()
    content = Field()
    author = Field()
    publish_date = Field()

class NewsSpider(Spider):
    name = "news_spider"
    start_urls = ["https://news.example.com"]

    async def parse(self, response):
        # 提取文章链接
        for article_link in response.css('article h2 a::attr(href)').getall():
            yield Request(
                url=response.urljoin(article_link),
                callback=self.parse_article,
                meta={'source': response.url}
            )

    async def parse_article(self, response):
        yield NewsItem(
            title=response.css('h1::text').get(),
            content=response.css('.article-content::text').get(),
            author=response.css('.author::text').get(),
            publish_date=response.css('.date::text').get()
        )

# 运行爬虫
if __name__ == "__main__":
    process = CrawlProcess()
    process.crawl(NewsSpider)
    process.start()
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定示例
python -m tests.baidu_spider.run
```

## 本地开发

如果你要在本地启动示例爬虫、FastAPI 后端和前端联调界面，建议直接看这份文档：

- `docs/local_dev_guide.md`

## 项目结构

```
bald_spider/
├── __init__.py           # 主要导出
├── crawler.py           # 爬虫和爬取进程
├── core/                # 核心引擎组件
│   ├── engine.py        # 主引擎
│   ├── downloader/      # HTTP 下载器
│   └── processor.py     # 响应处理器
├── http/                # HTTP 处理
│   ├── request.py       # 请求类
│   └── response.py      # 响应类
├── spider/              # 爬虫基类
├── items/               # 数据结构
├── pipeline/            # 项目处理管道
├── middleware/          # 中间件系统
├── duplicate_filter/    # URL 去重
├── extension/           # 扩展系统
├── settings/            # 配置管理
└── utils/               # 工具函数

tests/
└── baidu_spider/        # 示例爬虫
```

## 依赖要求

- Python 3.8+
- aiohttp
- httpx
- lxml
- cssselect
- redis（可选，用于去重过滤）

## 贡献指南

1. Fork 仓库
2. 创建功能分支
3. 进行修改
4. 为新功能添加测试
5. 提交 pull request

## 许可证

本项目采用 MIT 许可证。

## 更新日志

### v0.1.0
- 初始发布
- 基本爬虫功能
- 异步支持
- 中间件系统
- 管道系统
- 去重过滤
- 统计收集

## 支持

如有问题或建议：
- 在 GitHub 上创建 issue
- 查看 `tests/` 目录中的示例
- 查阅源代码注释

## 示例项目

项目包含一个百度爬虫示例，展示了框架的主要功能：

```bash
# 运行百度爬虫示例
python -m tests.baidu_spider.run
```

该示例演示了：
- 多页面爬取
- 回调函数链式调用
- 错误处理
- 事件钩子
- 自定义项目定义
