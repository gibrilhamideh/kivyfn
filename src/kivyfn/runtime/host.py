# runtime/host.py
from __future__ import annotations

import asyncio

from multiprocessing.queues import Queue
from multiprocessing.context import SpawnContext
from typing import Any

from kivyfn.runtime.bus import BaseBus
from kivyfn.runtime.message import RuntimeMessage

class RuntimeClientInfo:
    def __init__(self, name: str, host_inbox: Queue, inbox: Queue) -> None:
        self.name = name
        self.host_inbox = host_inbox
        self.inbox = inbox

class RuntimeHost:
    def __init__(self, context: SpawnContext) -> None:
        self._ctx = context
        self.inbox: Queue = context.Queue()
        self.bus = HostBus(self.inbox)

    def create_client(self, name: str) -> "RuntimeClientInfo":
        queue = self._ctx.Queue()
        self.bus.register_client(name, queue)
        return RuntimeClientInfo(name=name, host_inbox=self.inbox, inbox=queue)

    async def run(self) -> None:
        await self.bus.run()

class HostBus(BaseBus):
    def __init__(self, inbox: Queue) -> None:
        super().__init__()
        self.inbox = inbox
        self._clients: dict[str, Queue] = {}
        self._subscriptions: dict[str, set[str]] = {}
        self._running = False

    def register_client(self, name: str, inbox: Queue) -> None:
        self._clients[name] = inbox

    async def publish(self, topic: str, payload: Any = None) -> None:
        await self._dispatch(topic, payload)

        for client_name in self._subscriptions.get(topic, set()):
            client_queue = self._clients.get(client_name)
            if client_queue is not None:
                client_queue.put(RuntimeMessage("publish", topic, payload, source="host"))

    async def run(self) -> None:
        self._running = True

        while self._running:
            message: RuntimeMessage = await asyncio.to_thread(self.inbox.get)

            if message.type == "subscribe" and message.source:
                self._subscriptions.setdefault(message.topic, set()).add(message.source)

            elif message.type == "unsubscribe" and message.source:
                self._subscriptions.get(message.topic, set()).discard(message.source)

            elif message.type == "publish":
                await self.publish(message.topic, message.payload)

    def stop(self) -> None:
        self._running = False
        self.inbox.put(RuntimeMessage("publish", "__runtime.stop__"))
