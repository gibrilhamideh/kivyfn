from __future__ import annotations

from typing import Generic, TypeVar

from kivyfn.runtime import RuntimeClient


WindowName = TypeVar("WindowName", bound=str)


class WindowController(Generic[WindowName]):
    def __init__(self, runtime: RuntimeClient) -> None:
        self._runtime = runtime

    async def focus(self, name: WindowName) -> None:
        await self._publish("window.focus.requested", name)

    async def close(self, name: WindowName) -> None:
        await self._publish("window.close.requested", name)

    async def minimize(self, name: WindowName) -> None:
        await self._publish("window.minimize.requested", name)

    async def maximize(self, name: WindowName) -> None:
        await self._publish("window.maximize.requested", name)

    async def fullscreen(self, name: WindowName, value: bool = True) -> None:
        await self._runtime.bus.publish(
            "window.fullscreen.requested",
            {"name": name, "value": value},
        )

    async def _publish(self, topic: str, name: WindowName) -> None:
        await self._runtime.bus.publish(
            topic,
            {"name": name},
        )
