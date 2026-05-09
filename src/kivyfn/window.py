from __future__ import annotations

from typing import Any

from kivyfn.base import FnBaseApp
from kivyfn.runtime import FnClientBus, FnBusConnection
from kivyfn.windows import WindowController


class FnWindow(FnBaseApp):
    fnbus: FnClientBus
    fnwindows: WindowController

    def __init__(
        self,
        *args: Any,
        fnconnection: FnBusConnection,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fnbus = FnClientBus(fnconnection)
        self.fnwindows = WindowController(bus=self.fnbus)

        self.create_task(self.fnbus.start())
