"""
兼容层：实际实现已迁移到仓库顶层的 `config_spider_runtime` 包。
"""

from config_spider_runtime import (
    ConfigSpiderFactory,
    FieldConfig,
    InMemoryResultStore,
    SelectorType,
    SpiderConfig,
    run_config_spider,
    run_config_spider_once,
)

__all__ = [
    "SpiderConfig",
    "FieldConfig",
    "SelectorType",
    "ConfigSpiderFactory",
    "run_config_spider",
    "run_config_spider_once",
    "InMemoryResultStore",
]
