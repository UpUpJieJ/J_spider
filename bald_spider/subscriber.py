# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/28
import asyncio
from collections import defaultdict
from typing import Coroutine, Callable, Set, Dict


class Subscriber:
    def __init__(self):
        self._subscriber: Dict[str, Set[Callable[..., Coroutine]]] = defaultdict(set)

    def subscribe(
            self,
            receiver: Callable[..., Coroutine],
            *,
            event: str,
    ) -> None:
        self._subscriber[event].add(receiver)

    def unsubscribe(
            self,
            receiver: Callable[..., Coroutine],
            *,
            event: str,
    ) -> None:
        self._subscriber[event].discard(receiver)

    async def notify(self, event: str, *args, **kwargs):
        for receiver in self._subscriber[event]:
            _ = asyncio.create_task(receiver(*args, **kwargs))
