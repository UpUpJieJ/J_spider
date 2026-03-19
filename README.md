# bald_spider

An asynchronous, extensible web scraping framework built with asyncio. Inspired by Scrapy but designed with a modern Python architecture.

## Features

- **Asynchronous Performance**: Built entirely on asyncio for high-concurrency scraping
- **Event-Driven Architecture**: Clean separation of concerns with publisher-subscriber pattern
- **Extensible Design**: Easy to add custom components, middleware, and pipelines
- **Duplicate Filtering**: Built-in support with optional Redis backend
- **Automatic Retries**: Configurable retry mechanism for failed requests
- **Middleware System**: Request/response processing hooks
- **Pipeline System**: Flexible item processing and storage
- **Statistics Collection**: Built-in stats tracking and reporting
- **Configuration Management**: Flexible settings system with project and spider-specific configs

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd bald_spider

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Create Your First Spider

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

### 2. Run Your Spider

```python
from bald_spider.crawler import CrawlProcess

# Create and run the spider
process = CrawlProcess()
process.crawl(MySpider)
process.start()
```

### 3. Using Pipelines

```python
# Define a pipeline to process items
class MyPipeline:
    async def process_item(self, item, spider):
        # Save to database
        await save_to_database(item)
        return item

    async def open_spider(self, spider):
        # Initialize database connection
        await db.connect()

    async def close_spider(self, spider):
        # Cleanup
        await db.close()
```

## Architecture

### Core Components

- **Engine**: The heart of the spider system, coordinating all components
- **Scheduler**: Manages request queues and priority
- **Downloader**: Handles HTTP requests (supports aiohttp and httpx)
- **Processor**: Processes responses and generates new requests/items
- **Spider**: Base class for defining scraping logic
- **Pipeline**: Processes and stores scraped data
- **Middleware**: Request/response processing hooks

### Data Structures

- **Request**: Represents HTTP requests with metadata
- **Response**: Handles HTTP responses with parsing capabilities
- **Item**: Dictionary-like container for scraped data with field validation

### Event System

The framework uses a publisher-subscriber pattern for communication between components:

```python
# Subscribe to events
spider.subscribe('item_scraped', item_handler)
spider.subscribe('request_failed', error_handler)
```

## Configuration

Settings are managed through a hierarchical system:

```python
# Default settings
CONCURRENT_REQUESTS = 16
DOWNLOAD_TIMEOUT = 60
RETRY_HTTP_CODES = [500, 502, 503, 504]
RANDOMIZE_DOWNLOAD_DELAY = True
DUPEFILTER_CLASS = 'bald_spider.duplicate_filter.RFPDupeFilter'
```

## Advanced Features

### Middleware

```python
class CustomDownloaderMiddleware:
    async def process_request(self, request, spider):
        # Modify requests before downloading
        request.headers['User-Agent'] = 'My Custom Spider'
        return request

    async def process_response(self, response, request, spider):
        # Process responses after downloading
        return response
```

### Custom Duplicate Filter

```python
from bald_spider.duplicate_filter import BaseDupeFilter

class MyDupeFilter(BaseDupeFilter):
    async def request_seen(self, request):
        # Implement your duplicate detection logic
        return False
```

### Statistics Collection

```python
# Access statistics
stats = spider.stats
print(stats.get_value('item_scraped_count'))
print(stats.get_value('requests_count'))
```

## Example: Complete Spider Implementation

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
        # Extract article links
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

# Run the spider
if __name__ == "__main__":
    process = CrawlProcess()
    process.crawl(NewsSpider)
    process.start()
```

## Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m tests.baidu_spider.run
```

## Config Spider GUI (FastAPI + Frontend)

This repository also contains a small **configuration-based spider GUI** built on top of `bald_spider`, implemented as a **FastAPI backend + Vite (React + TypeScript) frontend**.

### 1. Backend (FastAPI) - Config Spider API

- Entry point: `backend/main.py`
- Start the API server:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The main HTTP endpoints:

- `GET /api/health` - basic health check
- `POST /api/config-spider/test` - test a config and fetch a small sample of data
- `POST /api/config-spider/run` - run the config spider and return all collected items
- `GET /api/config-spider/export/csv` - export the latest run results as CSV

The API reuses:

- `config_spider_runtime.models.SpiderConfig` / `FieldConfig`
- `config_spider_runtime.runner.run_config_spider_once`
- `config_spider_runtime.storage.InMemoryResultStore`

Architecture and sustainable development guide:

- `docs/config_spider_sustainable_dev.md`

### 2. Frontend (Vite + React + TS)

The frontend lives under the `frontend/` directory and was bootstrapped with Vite.

Install dependencies if needed:

```bash
cd frontend
npm install
```

Run the dev server:

```bash
npm run dev
```

By default Vite runs at `http://localhost:5173`, and the backend is expected at `http://localhost:8000`.

You can override the backend base URL by creating a `.env` file under `frontend/`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

### 3. Using the Config GUI

1. Start FastAPI:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

2. Start the frontend:

```bash
cd frontend
npm run dev
```

3. Open `http://localhost:5173` in the browser and configure:

- Spider name (`target_name`)
- Start URLs
- Selector type (`css` or `xpath`)
- List selector
- Detail URL selector, if needed
- Next page selector, if needed
- Fields and attributes
- Concurrency, download delay, and optional max items

4. Run:

- Click `Test` first to validate selectors and preview sample rows.
- Click `Run` to execute the full config spider and inspect results in the right-hand panel.
- Click `Export CSV` to download the latest run results from the FastAPI backend.

## Local Development

For a direct, ready-to-run local workflow covering the example spider, FastAPI backend, and Vite frontend, see:

- `docs/local_dev_guide.md`

## Project Structure

```
bald_spider/
├── __init__.py           # Main exports
├── crawler.py           # Crawler and CrawlProcess
├── core/                # Core engine components
│   ├── engine.py        # Main engine
│   ├── downloader/      # HTTP downloaders
│   └── processor.py     # Response processor
├── http/                # HTTP handling
│   ├── request.py       # Request class
│   └── response.py      # Response class
├── spider/              # Spider base class
├── items/               # Data structures
├── pipeline/            # Item processing
├── middleware/          # Middleware system
├── duplicate_filter/    # URL deduplication
├── extension/           # Extension system
├── settings/            # Configuration
└── utils/               # Utilities

tests/
└── baidu_spider/        # Example spider
```

## Requirements

- Python 3.8+
- aiohttp
- httpx
- lxml
- cssselect
- redis (optional, for duplicate filtering)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Changelog

### v0.1.0
- Initial release
- Basic spider functionality
- Async support
- Middleware system
- Pipeline system
- Duplicate filtering
- Statistics collection

## Support

For issues and questions:
- Create an issue on GitHub
- Check the examples in the `tests/` directory
- Review the source code documentation

