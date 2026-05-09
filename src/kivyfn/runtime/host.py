from __future__ import annotations

import asyncio

from multiprocessing.context import SpawnContext
from multiprocessing.queues import Queue
from typing import Any

from kivyfn.runtime.bus import FnBus
from kivyfn.runtime.connection import FnBusConnection
from kivyfn.runtime.message import FnBusMessage


class FnHostBus(FnBus):
    def __init__(self, context: SpawnContext) -> None:
        super().__init__()

        self._ctx = context

        self.inbox: Queue = context.Queue()

        self._clients: dict[str, Queue] = {}
        self._subscriptions: dict[str, set[str]] = {}

        self._running = False

    def create_connection(self, name: str) -> FnBusConnection:
        inbox = self._ctx.Queue()

        self._clients[name] = inbox

        return FnBusConnection(
            name=name,
            host_inbox=self.inbox,
            inbox=inbox,
        )

    async def publish(self, topic: str, payload: Any = None) -> None:
        await self._dispatch(topic, payload)

        for client_name in self._subscriptions.get(topic, set()):
            client_queue = self._clients.get(client_name)

            if client_queue is not None:
                client_queue.put(
                    FnBusMessage(
                        "publish",
                        topic,
                        payload,
                        source="host",
                    )
                )

    async def start(self) -> None:
        self._running = True

        while self._running:
            message: FnBusMessage = await asyncio.to_thread(
                self.inbox.get
            )

            if message.type == "subscribe" and message.source:
                self._subscriptions.setdefault(
                    message.topic,
                    set(),
                ).add(message.source)

            elif message.type == "unsubscribe" and message.source:
                self._subscriptions.get(
                    message.topic,
                    set(),
                ).discard(message.source)

            elif message.type == "publish":
                await self.publish(
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
