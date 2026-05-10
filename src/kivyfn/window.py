from __future__ import annotations

from kivyfn.base import FnBaseApp
from kivyfn.config import FnConfig
from kivyfn.runtime import (
    FnBusConnection,
    FnClientRuntime,
)


class FnWindow(FnBaseApp):

    fn: FnClientRuntime

    def __init__(
        self,
        config: FnConfig,
        connection: FnBusConnection,
    ) -> None:
        self.fn = FnClientRuntime(config=config, connection=connection)
        super().__init__(self.fn)

        self.fn.start()
