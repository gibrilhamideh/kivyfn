from __future__ import annotations

from multiprocessing import get_context

from kivyfn.config import FnConfig
from kivyfn.settings import FnSettings
from kivyfn.fonts import FontManager
from kivyfn.i18n import I18n
from kivyfn.runtime.process import FnProcessManager
from kivyfn.runtime.transport.client import FnClientBus
from kivyfn.runtime.transport.server import FnServerBus
from kivyfn.runtime.transport.connection import FnBusConnection
from kivyfn.runtime.state.manager import FnSharedStateManager
from kivyfn.runtime.window.manager import FnWindowManager
from kivyfn.runtime.window.controller import FnWindowController

import asyncio

class FnServerRuntime:
    def __init__(self, config: FnConfig):
        self.context = get_context("spawn")

        self.config = config
        self.settings = FnSettings()
        self.bus = FnServerBus(self.context)
        self.processes = FnProcessManager(self.context)
        self.state = FnSharedStateManager(self.bus)
        self.i18n = I18n(self.config.locales_dir)
        self.fonts = FontManager(self.config.fonts_dir, self.config.fonts.name)

        self.window_manager = FnWindowManager(
            self.processes,
            self.bus,
            self.config,
        )

    def start(self) -> None:
        asyncio.create_task(self.bus.start())

    def stop(self) -> None:
        self.bus.stop()
        self.processes.kill_all()


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
        self.i18n = I18n(self.config.locales_dir)
        self.fonts = FontManager(self.config.fonts_dir, self.config.fonts.name)
        self.window_controller = FnWindowController(bus=self.bus)

    def start(self) -> None:
        asyncio.create_task(self.bus.start())

    def stop(self) -> None:
        self.bus.disconnect()
        self.bus.stop()
