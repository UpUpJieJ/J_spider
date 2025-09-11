# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/28
import asyncio
from collections import defaultdict
from typing import Coroutine, Callable, Set, Dict
from inspect import iscoroutinefunction

from bald_spider.exceptions import ReceiverTypeError


class Subscriber:
    def __init__(self):
        self._subscriber: Dict[str, Set[Callable[..., Coroutine]]] = defaultdict(set)

    def subscribe(
            self,
            receiver: Callable[..., Coroutine],
            *,
            event: str,
    ) -> None:
        if not iscoroutinefunction(receiver):
            raise ReceiverTypeError(f"receiver {receiver.__qualname__} must be a coroutine function")
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
