from __future__ import annotations

import asyncio
import uuid
from multiprocessing.queues import Queue
from typing import Any, Literal

from kivyfn.runtime.transport.bus import FnBus, BusCallback
from kivyfn.runtime.transport.connection import FnBusConnection
from kivyfn.runtime.transport.message import FnBusMessage


class FnClientBus(FnBus):
    role: Literal["client"] = "client"

    def __init__(self, connection: FnBusConnection) -> None:
        super().__init__()

        self.name = connection.name
        self.server_inbox: Queue = connection.server_inbox
        self.inbox: Queue = connection.client_inbox

        self._running = False
        self._pending_calls: dict[str, asyncio.Future[Any]] = {}

    def subscribe(
        self,
        topic: str,
        callback: BusCallback,
    ) -> None:
        super().subscribe(topic, callback)

        self.server_inbox.put(
            FnBusMessage(
                type="subscribe",
                topic=topic,
                source=self.name,
            )
        )

    def unsubscribe(
        self,
        topic: str,
        callback: BusCallback,
    ) -> None:
        super().unsubscribe(topic, callback)

        self.server_inbox.put(
            FnBusMessage(
                type="unsubscribe",
                topic=topic,
                source=self.name,
            )
        )

    async def publish(
        self,
        topic: str,
        payload: Any = None,
    ) -> None:
        self.server_inbox.put(
            FnBusMessage(
                type="publish",
                topic=topic,
                payload=payload,
                source=self.name,
            )
        )

    async def call(
        self,
        topic: str,
        payload: Any = None,
    ) -> Any:
        call_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()

        future: asyncio.Future[Any] = loop.create_future()
        self._pending_calls[call_id] = future

        self.server_inbox.put(
            FnBusMessage(
                type="call",
                topic=topic,
                payload=payload,
                source=self.name,
                call_id=call_id,
            )
        )

        return await future

    def disconnect(self) -> None:
        self.server_inbox.put(
            FnBusMessage(
                type="disconnect",
                topic="fn.bus.disconnect",
                source=self.name,
            )
        )

    async def start(self) -> None:
        self._running = True

        while self._running:
            message: FnBusMessage = await asyncio.to_thread(self.inbox.get)

            if message.type == "stop":
                break

            if message.type == "publish":
                await self.dispatch(message.topic, message.payload)

            elif message.type == "reply" and message.call_id:
                self._resolve_reply(message)

        self._running = False
        self._cancel_pending_calls()

    def stop(self) -> None:
        self._running = False
        self.inbox.put(
            FnBusMessage(
                type="stop",
                topic="fn.bus.stop",
            )
        )

    def _resolve_reply(
        self,
        message: FnBusMessage,
    ) -> None:
        if message.call_id is None:
            return

        future = self._pending_calls.pop(message.call_id, None)

        if future is None or future.done():
            return

        if message.error is not None:
            future.set_exception(RuntimeError(message.error))
            return

        future.set_result(message.payload)

    def _cancel_pending_calls(self) -> None:
        for future in self._pending_calls.values():
            if not future.done():
                future.set_exception(
                    RuntimeError("Client bus stopped before reply was received")
                )

        self._pending_calls.clear()
