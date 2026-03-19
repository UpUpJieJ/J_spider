"""
兼容层：实现已迁移到 `backend.services.config_spider` 包下。
"""

from .config_spider import (
    get_latest_results_csv,
    run_config_spider_full,
    test_config_spider,
)

__all__ = [
    "get_latest_results_csv",
    "run_config_spider_full",
    "test_config_spider",
]
