# kivyfn/windonw.py
from __future__ import annotations

from kivy.properties import ObjectProperty

from kivyfn.base import FnBaseApp
from kivyfn.config import FnConfig
from kivyfn.runtime.runtime import FnClientRuntime
from kivyfn.runtime.transport.connection import FnBusConnection
from kivyfn.runtime.context import set_runtime


class FnWindow(FnBaseApp):

    fn: FnClientRuntime = ObjectProperty()

    def __init__(
        self,
        config: FnConfig,
        connection: FnBusConnection,
    ) -> None:
        self.fn = FnClientRuntime(config=config, connection=connection)
        set_runtime(self.fn)
        super().__init__(self.fn)

        self.fn.start()
