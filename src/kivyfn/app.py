from __future__ import annotations

from kivyfn.base import FnBaseApp
from kivyfn.config import FnConfig
from kivyfn.runtime import FnServerRuntime


class FnApp(FnBaseApp):

    fn: FnServerRuntime

    def __init__(self, config: FnConfig):
        self.fn = FnServerRuntime(config)
        super().__init__(self.fn)

        self.fn.start()
