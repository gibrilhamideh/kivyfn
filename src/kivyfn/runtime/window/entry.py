# kivyfn/runtime/window/entry.py
from __future__ import annotations

import asyncio
from typing import cast

from kivyfn.runtime.process import FnProcessContext
from kivyfn.runtime.window.types import (
    WindowArgs,
    WindowFactory,
    WindowKwargs,
)


def window_entry(context: FnProcessContext) -> None:
    factory, args, kwargs, async_mode = context.args

    factory = cast(WindowFactory, factory)
    args = cast(WindowArgs, args)
    kwargs = cast(WindowKwargs, kwargs)
    async_mode = cast(bool, async_mode)

    factory.__runtime__ = "spawn"

    app = factory(*args, **kwargs)

    # Import Kivy only after the application class has been imported.
    # Its module is responsible for importing config before KivyFn/Kivy.
    from kivy.app import App
    from kivy.clock import Clock

    if not isinstance(app, App):
        raise TypeError(
            f"Window factory for {context.name!r} must return a Kivy App"
        )

    def stop_app() -> None:
        Clock.schedule_once(
            lambda _dt: app.stop(),
            0,
        )

    context.listen(stop_app)
    app.bind(on_start=lambda *_args: context.ready())

    if async_mode:
        asyncio.run(
            app.async_run(async_lib="asyncio")
        )
        return

    app.run()
