from __future__ import annotations

from typing import Any, Dict, Optional, Type

from bald_spider import Request
from bald_spider.items import Field
from bald_spider.items.items import Item
from bald_spider.spider import Spider
from bald_spider.http.response import Response

from .models import SelectorType, SpiderConfig


def _relative_xpath(expr: str) -> str:
    """
    Scrapy/Parsel 推荐在“节点上下文”中使用相对 XPath（以 .// 开头），
    避免误用 // 导致从整棵文档树重新开始匹配。
    """
    expr = (expr or "").lstrip()
    if expr.startswith("//") or expr.startswith("/"):
        return f".{expr}"
    return expr


def _xpath_with_fallback(context, expr: str):
    """
    为兼容旧配置：优先按相对 XPath 执行；若无结果则回退到原表达式。
    """
    rel = _relative_xpath(expr)
    result = context.xpath(rel)
    if result:
        return result
    if rel != (expr or "").lstrip():
        return context.xpath(expr)
    return result


def _select(context, selector: str, selector_type: SelectorType, *, xpath_relative: bool = False):
    if selector_type == SelectorType.CSS:
        result = context.css(selector)
        if result:
            return result
        stripped = (selector or "").lstrip()
        if stripped.startswith("/") or stripped.startswith("//"):
            return context.xpath(selector)
        return result
    if xpath_relative:
        return _xpath_with_fallback(context, selector)
    return context.xpath(selector)


def _get_attr_from_node(node, attr: str, response: Response):
    if attr == "text":
        raw = node.get() if hasattr(node, "get") else None
        if hasattr(node, "xpath"):
            value = node.xpath("string(.)").get()
            if value is None:
                value = raw
        else:
            value = raw
        return value.strip() if isinstance(value, str) else value
    if attr == "href":
        value = node.attrib.get("href") if hasattr(node, "attrib") else node.get()
        if not value:
            return None
        return response.urljoin(value)
    if attr == "src":
        value = node.attrib.get("src") if hasattr(node, "attrib") else node.get()
        if not value:
            return None
        return response.urljoin(value)
    if hasattr(node, "attrib"):
        return node.attrib.get(attr)
    return node.get()


def _build_item_class(config: SpiderConfig) -> Type[Item]:
    attrs: Dict[str, Any] = {fc.name: Field() for fc in config.fields}
    return type(f"{config.target_name}Item", (Item,), attrs)


def _normalize_limit(value: Optional[int]) -> Optional[int]:
    if value is None:
        return None
    return value if value > 0 else None


async def _extract_fields_from_page(
    response: Response,
    config: SpiderConfig,
    item_cls: Type[Item],
    from_page: str,
):
    item = item_cls()
    for fc in config.fields:
        if fc.from_page != from_page:
            continue
        if from_page == "list" and fc.scope != "page":
            continue
        nodes = _select(response, fc.selector, config.selector_type, xpath_relative=False)
        if not nodes:
            continue
        value = _get_attr_from_node(nodes[0], fc.attr, response)
        item[fc.name] = value
    yield item


class ConfigSpiderFactory:
    @staticmethod
    def create_spider_class(config: SpiderConfig) -> Type[Spider]:
        item_cls = _build_item_class(config)
        max_items = _normalize_limit(config.max_items)

        class ConfigSpider(Spider):
            name = config.target_name
            start_urls = config.start_urls
            _max_items = max_items

            def __init__(self):
                super().__init__()
                self._item_count = 0

            def _limit_reached(self) -> bool:
                return self._max_items is not None and self._item_count >= self._max_items

            def _emit_item(self, item: Item) -> Optional[Item]:
                if self._limit_reached():
                    return None
                self._item_count += 1
                if self._limit_reached() and self.crawler and self.crawler.engine:
                    self.crawler.engine.running = False
                return item

            async def parse(self, response: Response):
                def _yield_next_page():
                    if self._limit_reached():
                        return
                    if not config.next_page_selector:
                        return
                    np_nodes = _select(
                        response, config.next_page_selector, config.selector_type, xpath_relative=False
                    )
                    if not np_nodes:
                        return
                    href = _get_attr_from_node(np_nodes[0], "href", response)
                    if href:
                        yield Request(url=href, callback=self.parse)

                if not config.list_selector:
                    async for item in _extract_fields_from_page(response, config, item_cls, from_page="list"):
                        emitted = self._emit_item(item)
                        if emitted is None:
                            return
                        yield emitted
                    async for item in _extract_fields_from_page(response, config, item_cls, from_page="detail"):
                        emitted = self._emit_item(item)
                        if emitted is None:
                            return
                        yield emitted
                    for req in _yield_next_page():
                        yield req
                    return

                nodes = _select(response, config.list_selector, config.selector_type, xpath_relative=False)

                page_values: Dict[str, Any] = {}
                for fc in config.fields:
                    if fc.from_page != "list" or fc.scope != "page":
                        continue
                    page_nodes = _select(response, fc.selector, config.selector_type, xpath_relative=False)
                    if page_nodes:
                        page_values[fc.name] = _get_attr_from_node(page_nodes[0], fc.attr, response)

                for node in nodes:
                    if self._limit_reached():
                        break
                    item = item_cls()
                    for k, v in page_values.items():
                        item[k] = v
                    for fc in config.fields:
                        if fc.from_page != "list":
                            continue
                        if fc.scope != "node":
                            continue
                        field_nodes = _select(node, fc.selector, config.selector_type, xpath_relative=True)
                        if field_nodes:
                            value = _get_attr_from_node(field_nodes[0], fc.attr, response)
                            item[fc.name] = value

                    if config.detail_url_selector:
                        detail_nodes = _select(
                            node, config.detail_url_selector, config.selector_type, xpath_relative=True
                        )
                        for dn in detail_nodes:
                            if self._limit_reached():
                                break
                            href = _get_attr_from_node(dn, "href", response)
                            if not href:
                                continue
                            yield Request(
                                url=href,
                                callback=self.parse_detail,
                                meta={"partial_item": item},
                            )
                    else:
                        emitted = self._emit_item(item)
                        if emitted is None:
                            break
                        yield emitted

                if not nodes and page_values:
                    item = item_cls()
                    for k, v in page_values.items():
                        item[k] = v
                    emitted = self._emit_item(item)
                    if emitted is not None:
                        yield emitted

                for req in _yield_next_page():
                    yield req

            async def parse_detail(self, response: Response):
                base_item = response.meta.get("partial_item", item_cls())
                for fc in config.fields:
                    if fc.from_page != "detail":
                        continue
                    nodes = _select(response, fc.selector, config.selector_type, xpath_relative=False)
                    if nodes:
                        value = _get_attr_from_node(nodes[0], fc.attr, response)
                        base_item[fc.name] = value
                emitted = self._emit_item(base_item)
                if emitted is not None:
                    yield emitted

            async def spider_opened(self):
                self.crawler.stats["config_spider_name"] = config.target_name

        return ConfigSpider
