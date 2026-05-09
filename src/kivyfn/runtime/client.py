from __future__ import annotations

import asyncio

from multiprocessing.queues import Queue
from typing import Any

from kivyfn.runtime.bus import FnBus, BusCallback
from kivyfn.runtime.connection import FnBusConnection
from kivyfn.runtime.message import FnBusMessage


class FnClientBus(FnBus):
    def __init__(self, connection: FnBusConnection) -> None:
        super().__init__()

        self.name = connection.name
        self.host_inbox: Queue = connection.host_inbox
        self.inbox: Queue = connection.inbox

        self._running = False

    def subscribe(self, topic: str, callback: BusCallback) -> None:
        super().subscribe(topic, callback)

        self.host_inbox.put(
            FnBusMessage(
                "subscribe",
                topic,
                source=self.name,
            )
        )

    def unsubscribe(self, topic: str) -> None:
        self.host_inbox.put(
            FnBusMessage(
                "unsubscribe",
                topic,
                source=self.name,
            )
        )

    async def publish(self, topic: str, payload: Any = None) -> None:
        self.host_inbox.put(
            FnBusMessage(
                "publish",
                topic,
                payload,
                source=self.name,
            )
        )

    async def start(self) -> None:
        self._running = True

        while self._running:
            message: FnBusMessage = await asyncio.to_thread(
                self.inbox.get
            )

            if message.type == "publish":
                await self._dispatch(
                    message.topic,
                    message.payload,
                )

    def stop(self) -> None:
        self._running = False

        self.inbox.put(
            FnBusMessage(
                "publish",
                "__bus.stop__",
            )
        )
