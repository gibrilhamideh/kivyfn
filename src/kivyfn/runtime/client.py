# runtime/client.py
from __future__ import annotations

import asyncio
from multiprocessing.queues import Queue
from typing import Any

from kivyfn.runtime.bus import BaseBus, BusCallback
from kivyfn.runtime.message import RuntimeMessage


class RuntimeClient:
    def __init__(self, name: str, host_inbox: Queue, inbox: Queue) -> None:
        self.name = name
        self.host_inbox: Queue = host_inbox
        self.inbox: Queue = inbox
        self.bus = ClientBus(name, host_inbox, inbox)


class ClientBus(BaseBus):
    def __init__(self, name: str, host_inbox: Queue, inbox: Queue) -> None:
        super().__init__()
        self.name = name
        self.host_inbox = host_inbox
        self.inbox = inbox
        self._running = False

    def subscribe(self, topic: str, callback: BusCallback) -> None:
        super().subscribe(topic, callback)
        self.host_inbox.put(RuntimeMessage("subscribe", topic, source=self.name))

    def unsubscribe(self, topic: str) -> None:
        self.host_inbox.put(RuntimeMessage("unsubscribe", topic, source=self.name))

    async def publish(self, topic: str, payload: Any = None) -> None:
        self.host_inbox.put(RuntimeMessage("publish", topic, payload, source=self.name))

    async def listen(self) -> None:
        self._running = True

        while self._running:
            message: RuntimeMessage = await asyncio.to_thread(self.inbox.get)

            if message.type == "publish":
                await self._dispatch(message.topic, message.payload)

    def stop(self) -> None:
        self._running = False
        self.inbox.put(RuntimeMessage("publish", "__runtime.stop__"))
