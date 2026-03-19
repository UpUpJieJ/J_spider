from __future__ import annotations

from typing import List, Optional

from config_spider_runtime import FieldConfig, SelectorType, SpiderConfig

from ...schemas import SpiderConfigIn


def clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def clean_urls(urls: List[str]) -> List[str]:
    return [u.strip() for u in urls if isinstance(u, str) and u.strip()]


def to_spider_config(dto: SpiderConfigIn) -> SpiderConfig:
    start_urls = clean_urls(dto.start_urls)
    fields: List[FieldConfig] = [
        FieldConfig(
            name=f.name.strip(),
            selector=f.selector.strip(),
            attr=f.attr,
            from_page=f.from_page,
            scope=f.scope,
        )
        for f in dto.fields
        if f.name.strip() and f.selector.strip()
    ]
    concurrency = dto.concurrency if dto.concurrency and dto.concurrency > 0 else 8
    download_delay = (
        dto.download_delay
        if dto.download_delay is not None and dto.download_delay >= 0
        else 0.0
    )

    return SpiderConfig(
        target_name=dto.target_name.strip() or "config_spider",
        start_urls=start_urls,
        selector_type=SelectorType(dto.selector_type),
        list_selector=(dto.list_selector or "").strip(),
        detail_url_selector=clean_optional_text(dto.detail_url_selector),
        next_page_selector=clean_optional_text(dto.next_page_selector),
        fields=fields,
        enable_dedup=dto.enable_dedup,
        concurrency=concurrency,
        download_delay=download_delay,
        max_items=dto.max_items,
    )
