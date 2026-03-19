from __future__ import annotations

from config_spider_runtime import run_config_spider_once

from ...schemas import RunResult, SpiderConfigIn, TestResult
from .mapper import to_spider_config
from .result_store import result_store


async def test_config_spider(dto: SpiderConfigIn) -> TestResult:
    """
    测试一条/一页抓取：强制限制 max_items 为一个较小值，返回样例数据。
    """
    effective = dto.copy()
    if effective.max_items is None or effective.max_items <= 0:
        effective.max_items = 20

    config = to_spider_config(effective)
    if not config.start_urls:
        raise ValueError("start_urls 不能为空")

    result_store.clear()
    await run_config_spider_once(config, item_collector=result_store)

    items = result_store.items
    total = len(items)

    return TestResult(
        config_summary={
            "target_name": config.target_name,
            "start_urls": config.start_urls,
            "selector_type": config.selector_type.value,
            "list_selector": config.list_selector,
            "detail_url_selector": config.detail_url_selector,
            "next_page_selector": config.next_page_selector,
            "enable_dedup": config.enable_dedup,
        },
        items=items,
        total=total,
    )


async def run_config_spider_full(dto: SpiderConfigIn) -> RunResult:
    """
    正式运行一次配置爬虫，当前版本采用同步方式：请求会等待爬虫结束。
    """
    config = to_spider_config(dto)
    if not config.start_urls:
        raise ValueError("start_urls 不能为空")

    result_store.clear()
    await run_config_spider_once(config, item_collector=result_store)

    items = result_store.items
    total = len(items)
    return RunResult(items=items, total=total)


def get_latest_results_csv() -> str:
    """
    导出最近一次运行结果为 CSV 文本。
    """
    return result_store.to_csv()
