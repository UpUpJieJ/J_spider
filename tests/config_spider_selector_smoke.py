import asyncio

from bald_spider.http.request import Request
from bald_spider.http.response import Response
from config_spider_runtime.factory import ConfigSpiderFactory
from config_spider_runtime.models import FieldConfig, SelectorType, SpiderConfig


HTML = """
<html>
  <body>
    <ul>
      <li><a href="/a1">T1</a></li>
      <li><a href="/a2">T2</a></li>
    </ul>
  </body>
</html>
""".strip()


async def main():
    config = SpiderConfig(
        target_name="config_spider_smoke",
        start_urls=[],
        selector_type=SelectorType.XPATH,
        list_selector="//li",
        detail_url_selector=None,
        fields=[
            FieldConfig(name="title", selector="//a/text()", attr="text", from_page="list"),
            FieldConfig(name="link", selector="//a", attr="href", from_page="list"),
        ],
    )
    spider_cls = ConfigSpiderFactory.create_spider_class(config)
    spider = spider_cls()

    req = Request(url="https://example.com/list", meta={})
    resp = Response(
        url=req.url,
        headers={},
        request=req,
        cookies={},
        body=HTML.encode("utf-8"),
    )

    items = []
    async for obj in spider.parse(resp):
        items.append(obj)

    assert len(items) == 2
    assert items[0]["title"] == "T1"
    assert items[0]["link"] == "https://example.com/a1"
    assert items[1]["title"] == "T2"
    assert items[1]["link"] == "https://example.com/a2"


if __name__ == "__main__":
    asyncio.run(main())
