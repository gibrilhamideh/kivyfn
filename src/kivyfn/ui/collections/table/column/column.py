from __future__ import annotations
from typing import Any

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty

from kivyfn.ui.collections.table.protocol import TableContentProtocol


class FnTableColumn(EventDispatcher):
    key = StringProperty("")
    width = ObjectProperty(None, allonone=True)
    cell_cls: type[TableContentProtocol] = ObjectProperty(None)
    header_cls: type[TableContentProtocol] | None = ObjectProperty(None)
    footer_cls: type[TableContentProtocol] | None = ObjectProperty(None)
    header_content: str = StringProperty()
    footer_content: str = StringProperty()
    visible: bool = BooleanProperty(True)
    title: str = StringProperty("")
    sort_func = ObjectProperty()

    def __init__(
        self,
        key: str,
        cell_cls: type[TableContentProtocol],
        header_cls: type[TableContentProtocol] | None = None,
        footer_cls: type[TableContentProtocol] | None = None,
        header_content: str = "",
        footer_content: str = "",
        width: Any = None,
        visible: bool = True,
        sort_func=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.key = key
        self.cell_cls = cell_cls
        self.header_cls = header_cls
        self.footer_cls = footer_cls
        self.header_content = header_content
        self.footer_content = footer_content
        self.width = width
        self.visible = visible
        self.sort_func = sort_func
