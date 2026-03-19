from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Literal, Optional


class SelectorType(str, Enum):
    CSS = "css"
    XPATH = "xpath"


@dataclass
class FieldConfig:
    """
    字段配置
    """

    name: str
    selector: str
    attr: str = "text"  # text / attr 名称，如 href / src
    from_page: Literal["list", "detail"] = "list"
    scope: Literal["page", "node"] = "node"


@dataclass
class SpiderConfig:
    """
    GUI / 前端 与 爬虫核心 之间的配置模型
    """

    target_name: str
    start_urls: List[str]
    selector_type: SelectorType = SelectorType.CSS
    list_selector: str = ""
    detail_url_selector: Optional[str] = None
    next_page_selector: Optional[str] = None
    fields: List[FieldConfig] = field(default_factory=list)
    enable_dedup: bool = True

    # 运行参数（只暴露简单几个常用项）
    concurrency: int = 8
    download_delay: float = 0.0

    # 最多抓取条数，0 或 None 表示不限制
    max_items: Optional[int] = None
