import asyncio

from bald_spider.http.request import Request
from bald_spider.http.response import Response
from config_spider_runtime.factory import ConfigSpiderFactory
from config_spider_runtime.models import FieldConfig, SelectorType, SpiderConfig


HTML = """
<html>
  <head><title>List Page</title></head>
  <body>
    <div class="list">
      <div class="row"><a class="item" href="/d1">A1</a></div>
      <div class="row"><a class="item" href="/d2">A2</a></div>
    </div>
    <a rel="next" href="/list?page=2">Next</a>
  </body>
</html>
""".strip()


async def main():
    config = SpiderConfig(
        target_name="config_spider_pagination_smoke",
        start_urls=[],
        selector_type=SelectorType.XPATH,
        list_selector='//div[@class="row"]',
        next_page_selector='//a[@rel="next"]/@href',
        fields=[
            FieldConfig(name="page_title", selector="//title/text()", attr="text", from_page="list", scope="page"),
            FieldConfig(name="text", selector=".//a/text()", attr="text", from_page="list", scope="node"),
            FieldConfig(name="link", selector=".//a", attr="href", from_page="list", scope="node"),
        ],
    )
    spider_cls = ConfigSpiderFactory.create_spider_class(config)
    spider = spider_cls()

    req = Request(url="https://example.com/list?page=1", meta={})
    resp = Response(
        url=req.url,
        headers={},
        request=req,
        cookies={},
        body=HTML.encode("utf-8"),
    )

    objs = []
    async for obj in spider.parse(resp):
        objs.append(obj)

    items = [o for o in objs if not isinstance(o, Request)]
    requests = [o for o in objs if isinstance(o, Request)]

    assert len(items) == 2
    assert items[0]["page_title"] == "List Page"
    assert items[0]["text"] == "A1"
    assert items[0]["link"] == "https://example.com/d1"
    assert items[1]["page_title"] == "List Page"
    assert items[1]["text"] == "A2"
    assert items[1]["link"] == "https://example.com/d2"

    assert len(requests) == 1
    assert requests[0].url == "https://example.com/list?page=2"


if __name__ == "__main__":
    asyncio.run(main())
