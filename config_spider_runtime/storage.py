from __future__ import annotations

import csv
import io
from typing import List


class InMemoryResultStore:
    """
    简单的内存结果存储，用于 GUI/Web 预览和导出。
    真实项目中可以替换为数据库或文件存储。

    注意：此类实现了 __deepcopy__ 以防止被深拷贝，
    因为 settings 会被 crawler 深拷贝，我们需要保持同一个实例。
    """

    def __init__(self):
        self._items: List[dict] = []

    def __deepcopy__(self, memo):
        # 防止被深拷贝，直接返回自身
        return self

    def add_item(self, item: dict):
        self._items.append(dict(item))

    def clear(self):
        self._items.clear()

    @property
    def items(self) -> List[dict]:
        return list(self._items)

    def to_csv(self) -> str:
        if not self._items:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(self._items[0].keys()))
        writer.writeheader()
        writer.writerows(self._items)
        return output.getvalue()
