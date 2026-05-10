from __future__ import annotations

from kivy.properties import ObjectProperty

from kivyfn.base import FnBaseApp
from kivyfn.config import FnConfig
from kivyfn.runtime.runtime import FnServerRuntime
from kivyfn.runtime.context import set_runtime


class FnApp(FnBaseApp):

    fn: FnServerRuntime = ObjectProperty()

    def __init__(self, config: FnConfig):
        self.fn = FnServerRuntime(config)
        set_runtime(self.fn)
        super().__init__(self.fn)

        self.fn.start()
