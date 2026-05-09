from __future__ import annotations

from typing import Any

from kivyfn.base import FnBaseApp
from kivyfn.runtime import RuntimeClient, RuntimeConnection
from kivyfn.windows import WindowController


class FnWindow(FnBaseApp):
    fnruntime: RuntimeClient
    fnwindows: WindowController

    def __init__(
        self,
        *args: Any,
        runtime: RuntimeConnection,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fnruntime = RuntimeClient(
            name=runtime.name,
            host_inbox=runtime.host_inbox,
            inbox=runtime.inbox,
        )

        self.fnwindows = WindowController(
            runtime=self.fnruntime,
        )
