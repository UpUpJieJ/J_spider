from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class FieldConfigIn(BaseModel):
    name: str
    selector: str
    attr: str = "text"  # text / href / src / 自定义属性名
    from_page: Literal["list", "detail"] = "list"
    scope: Literal["page", "node"] = "node"


class SpiderConfigIn(BaseModel):
    target_name: str = Field(default="config_spider", description="爬虫名称")
    start_urls: List[str] = Field(default_factory=list, description="起始 URL 列表")
    selector_type: Literal["css", "xpath"] = "css"
    list_selector: str = ""
    detail_url_selector: Optional[str] = None
    next_page_selector: Optional[str] = None
    fields: List[FieldConfigIn] = Field(default_factory=list)
    enable_dedup: bool = Field(default=True, description="是否启用请求去重")
    concurrency: int = 8
    download_delay: float = 0.0
    max_items: Optional[int] = Field(
        default=None,
        description="最多抓取条数，None 表示不限制；测试接口会自动限制为较小数量",
    )


class TestResult(BaseModel):
    config_summary: dict
    items: list[dict]
    total: int


class RunResult(BaseModel):
    items: list[dict]
    total: int
    message: str = "爬虫已完成"

