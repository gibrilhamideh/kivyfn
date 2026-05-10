from __future__ import annotations

from typing import Generic, TypeVar

from kivyfn.runtime import FnClientBus


WindowName = TypeVar("WindowName", bound=str)


class FnWindowController(Generic[WindowName]):
    def __init__(self, bus: FnClientBus) -> None:
        self.bus = bus

    async def focus(self, name: WindowName) -> None:
        await self._publish("fn.window.focus.requested", name)

    async def close(self, name: WindowName) -> None:
        await self._publish("fn.window.close.requested", name)

    async def minimize(self, name: WindowName) -> None:
        await self._publish("fn.window.minimize.requested", name)

    async def maximize(self, name: WindowName) -> None:
        await self._publish("fn.window.maximize.requested", name)

    async def fullscreen(
        self,
        name: WindowName,
        value: bool = True,
    ) -> None:
        await self.bus.publish(
            "fn.window.fullscreen.requested",
            {
                "name": name,
                "value": value,
            },
        )

    async def _publish(
        self,
        topic: str,
        name: WindowName,
    ) -> None:
        await self.bus.publish(
            topic,
            {
                "name": name,
            },
        )
