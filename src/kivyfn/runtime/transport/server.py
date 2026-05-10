from __future__ import annotations

import asyncio
from multiprocessing.context import SpawnContext
from multiprocessing.queues import Queue
from typing import Any, Literal

from kivyfn.runtime.transport.bus import FnBus
from kivyfn.runtime.transport.connection import FnBusConnection
from kivyfn.runtime.transport.message import FnBusMessage


class FnServerBus(FnBus):
    role: Literal["server"] = "server"

    def __init__(self, context: SpawnContext) -> None:
        super().__init__()

        self._ctx = context
        self.inbox: Queue = context.Queue()

        self._clients: dict[str, Queue] = {}
        self._subscriptions: dict[str, set[str]] = {}

        self._running = False

    def create_connection(
        self,
        name: str,
    ) -> FnBusConnection:
        inbox = self._ctx.Queue()
        self._clients[name] = inbox

        return FnBusConnection(
            name=name,
            server_inbox=self.inbox,
            client_inbox=inbox,
        )

    def remove_connection(
        self,
        name: str,
    ) -> None:
        self._clients.pop(name, None)

        for subscribers in self._subscriptions.values():
            subscribers.discard(name)

    async def publish(
        self,
        topic: str,
        payload: Any = None,
    ) -> None:
        await self.dispatch(topic, payload)

        for client_name in self._subscriptions.get(topic, set()):
            client_queue = self._clients.get(client_name)

            if client_queue is None:
                continue

            client_queue.put(
                FnBusMessage(
                    type="publish",
                    topic=topic,
                    payload=payload,
                    source="server",
                )
            )

    async def start(self) -> None:
        self._running = True

        while self._running:
            message: FnBusMessage = await asyncio.to_thread(self.inbox.get)

            if message.type == "stop":
                break

            if message.type == "subscribe" and message.source:
                self._subscriptions.setdefault(message.topic, set()).add(
                    message.source
                )

            elif message.type == "unsubscribe" and message.source:
                self._subscriptions.get(message.topic, set()).discard(
                    message.source
                )

            elif message.type == "disconnect" and message.source:
                self.remove_connection(message.source)

            elif message.type == "publish":
                await self.publish(message.topic, message.payload)

            elif message.type == "call":
                await self._reply_to_call(message)

        self._running = False

    async def _reply_to_call(
        self,
        message: FnBusMessage,
    ) -> None:
        if message.source is None or message.call_id is None:
            return

        client_queue = self._clients.get(message.source)

        if client_queue is None:
            return

        try:
            result = await self._handle(message.topic, message.payload)

            client_queue.put(
                FnBusMessage(
                    type="reply",
                    topic=message.topic,
                    payload=result,
                    source="server",
                    call_id=message.call_id,
                )
            )

        except Exception as exc:
            client_queue.put(
                FnBusMessage(
                    type="reply",
                    topic=message.topic,
                    source="server",
                    call_id=message.call_id,
                    error=str(exc),
                )
            )

    def stop(self) -> None:
        self._running = False
        self.inbox.put(
            FnBusMessage(
                type="stop",
                topic="fn.bus.stop",
            )
        )
