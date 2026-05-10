from __future__ import annotations

from multiprocessing import get_context

from kivyfn.config import FnConfig
from kivyfn.settings import FnSettings
from kivyfn.process import FnProcessManager
from kivyfn.runtime.client import FnClientBus
from kivyfn.runtime.server import FnServerBus
from kivyfn.runtime.connection import FnBusConnection
from kivyfn.runtime.state import FnSharedStateManager
from kivyfn.windows import FnWindowManager, FnWindowController

import asyncio

class FnServerRuntime:
    def __init__(self, config):
        self.context = get_context("spawn")

        self.config = config
        self.settings = FnSettings()
        self.bus = FnServerBus(self.context)
        self.processes = FnProcessManager(self.context)
        self.shared = FnSharedStateManager(self.bus)

        self.windows = FnWindowManager(
            self.processes,
            self.bus,
            self.config,
        )

    def start(self) -> None:
        asyncio.create_task(self.bus.start())


class FnClientRuntime:
    def __init__(
        self,
        config: FnConfig,
        connection: FnBusConnection,
    ) -> None:

        self.config = config
        self.settings = FnSettings()
        self.bus = FnClientBus(connection)
        self.state = FnSharedStateManager(self.bus)
        self.windows = FnWindowController(bus=self.bus)

    def start(self) -> None:
        asyncio.create_task(self.bus.start())
