from __future__ import annotations

from multiprocessing import get_context

from kivyfn.base import FnBaseApp
from kivyfn.process import FnProcessManager
from kivyfn.runtime import FnHostBus
from kivyfn.windows import WindowManager


class FnApp(FnBaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = get_context("spawn")
        self.fnbus = FnHostBus(context)
        self.fnprocesses = FnProcessManager(context)
        self.fnwindows = WindowManager(self.fnprocesses, self.fnbus, self.fnconfig)

        self.create_task(self.fnbus.start())
