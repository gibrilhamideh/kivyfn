# kivyfn/runtime/runtime.py
from __future__ import annotations

from collections.abc import Awaitable, Callable
from multiprocessing import get_context
from typing import Any

import inspect

from kivyfn.config import FnConfig
from kivyfn.fonts import FontManager
from kivyfn.i18n import I18n
from kivyfn.logging import get_logger
from kivyfn.runtime.asyncio import tasks
from kivyfn.runtime.process import FnProcessManager
from kivyfn.runtime.state.manager import FnSharedStateManager
from kivyfn.runtime.transport.client import FnClientBus
from kivyfn.runtime.transport.connection import FnBusConnection
from kivyfn.runtime.transport.server import FnServerBus
from kivyfn.runtime.window.controller import FnWindowController
from kivyfn.runtime.window.manager import FnWindowManager
from kivyfn.settings import FnSettings


logger = get_logger(__name__)


ShutdownHook = Callable[[], Any | Awaitable[Any]]


class FnRuntimeBase:
    def __init__(self) -> None:
        self._shutdown_hooks: list[ShutdownHook] = []
        self._shutdown_started = False

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------
    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    async def shutdown(self) -> None:
        """
        Runs full runtime cleanup.

        Safe to call multiple times.
        Shutdown order:
        1. extension/app shutdown hooks
        2. runtime stop
        3. managed asyncio task cleanup
        """
        if self._shutdown_started:
            return

        self._shutdown_started = True

        try:
            await self._run_shutdown_hooks()

        finally:
            try:
                self.stop()
            except Exception:
                logger.exception("Runtime stop failed")

            try:
                await tasks.stop()
            except Exception:
                logger.exception("Task manager shutdown failed")

    # -------------------------------------------------
    # Shutdown Hooks
    # -------------------------------------------------
    def on_shutdown(self, hook: ShutdownHook) -> None:
        self._shutdown_hooks.append(hook)

    async def _run_shutdown_hooks(self) -> None:
        for hook in reversed(self._shutdown_hooks):
            try:
                result = hook()

                if inspect.isawaitable(result):
                    await result

            except Exception:
                logger.exception(
                    "Shutdown hook failed: %s",
                    self._hook_name(hook),
                )

    def _hook_name(self, hook: ShutdownHook) -> str:
        qualname = getattr(hook, "__qualname__", None)
        if isinstance(qualname, str):
            return qualname

        name = getattr(hook, "__name__", None)
        if isinstance(name, str):
            return name

        return type(hook).__name__


class FnServerRuntime(FnRuntimeBase):
    def __init__(self, config: FnConfig):
        super().__init__()

        self.context = get_context("spawn")

        self.config = config
        self.settings = FnSettings()
        self.bus = FnServerBus(self.context)
        self.processes = FnProcessManager(self.context)
        self.state = FnSharedStateManager(self.bus)
        self.i18n = I18n(self.config.locales_dir)
        self.fonts = FontManager(
            self.config.fonts_dir,
            self.config.fonts.name,
        )

        self.window_manager = FnWindowManager(
            self.processes,
            self.bus,
            self.config,
        )

    def start(self) -> None:
        tasks.create(
            self.bus.start(),
            name="server-bus",
        )

    def stop(self) -> None:
        self.bus.stop()
        self.processes.kill_all()


class FnClientRuntime(FnRuntimeBase):
    def __init__(
        self,
        config: FnConfig,
        connection: FnBusConnection,
    ) -> None:
        super().__init__()

        self.config = config
        self.settings = FnSettings()
        self.bus = FnClientBus(connection)
        self.state = FnSharedStateManager(self.bus)
        self.i18n = I18n(self.config.locales_dir)
        self.fonts = FontManager(
            self.config.fonts_dir,
            self.config.fonts.name,
        )
        self.window_controller = FnWindowController(bus=self.bus)

    def start(self) -> None:
        tasks.create(
            self.bus.start(),
            name="client-bus",
        )

    def stop(self) -> None:
        self.bus.disconnect()
        self.bus.stop()
