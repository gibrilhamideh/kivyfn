from __future__ import annotations

from multiprocessing import get_context

from kivyfn.base import FnBaseApp
from kivyfn.process import ProcessManager
from kivyfn.runtime import RuntimeHost
from kivyfn.windows import WindowManager


class FnApp(FnBaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = get_context("spawn")
        self.fnruntime = RuntimeHost(context)
        self.fnprocesses = ProcessManager(context)
        self.fnwindows = WindowManager(
            processes=self.fnprocesses,
            runtime=self.fnruntime,
            fnconfig=self.fnconfig
        )
