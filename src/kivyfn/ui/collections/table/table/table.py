from __future__ import annotations

from kivy.properties import DictProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.effects.scroll import ScrollEffect

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.style import (
    FnBackgroundBehavior,
    FnBorderBehavior,
    FnElevationBehavior,
)

from kivyfn.ui.collections.table.body import FnTableBody
from kivyfn.ui.collections.table.cell import FnTableCell
from kivyfn.ui.collections.table.column import FnTableColumn
from kivyfn.ui.collections.table.footer import FnTableFooter
from kivyfn.ui.collections.table.header import FnTableHeader

from kivyfn.ui.collections.table.table.data import FnTableDataMixin
from kivyfn.ui.collections.table.table.layout import FnTableLayoutMixin
from kivyfn.ui.collections.table.table.cache import FnTableCellCacheMixin


class FnTable(
    FnTableDataMixin,
    FnTableLayoutMixin,
    FnTableCellCacheMixin,
    FnElevationBehavior,
    FnBackgroundBehavior,
    FnBorderBehavior,
    FnWidget,
    BoxLayout,
):
    columns: list[FnTableColumn] = ListProperty([])
    column_cells: dict[str, list[FnTableCell]] = DictProperty({})
    row_cells: dict[str, dict[str, FnTableCell]] = DictProperty({})

    header_height: float = NumericProperty(48)
    row_height: float = NumericProperty(48)
    footer_height: float = NumericProperty(0)

    header: FnTableHeader = ObjectProperty(None, allownone=True)
    body: FnTableBody = ObjectProperty(None, allownone=True)
    footer: FnTableFooter = ObjectProperty(None, allownone=True)

    row_spacing: int = NumericProperty()

    __events__ = ("on_cell_press",)

    def on_kv_post(self, base_widget):
        self.orientation = "vertical"
        return super().on_kv_post(base_widget)

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, FnTableHeader):
            self.header = widget
            self.header.effect_cls = ScrollEffect

        elif isinstance(widget, FnTableBody):
            self.body = widget
            self.body.effect_cls = ScrollEffect

        elif isinstance(widget, FnTableFooter):
            self.footer = widget
            self.footer.effect_cls = ScrollEffect

        return super().add_widget(widget, *args, **kwargs)

    def set_columns(self, columns: list[FnTableColumn]):
        for column in self.columns:
            column.unbind(visible=self._on_column_visibility)

        self.columns = columns

        for column in self.columns:
            column.bind(visible=self._on_column_visibility)

        self.rebuild()

    def build_header(self):
        self.header.clear_widgets()

        for column in self.get_visible_columns():
            cell = FnTableCell(size_hint_x=None)
            cell.column_key = column.key
            cell.width = self.column_widths[column.key]
            if column.header_cls is not None:
                content = column.header_cls()
                content.set_table_content(column.header_content)
                cell.add_widget(content)

            self.header.add_widget(cell)

    def rebuild(self):
        self.release_all_cells()
        self.body.clear_rows()

        self.row_cells = {}
        self.column_cells = {}

        self.refresh_column_widths()

        for row_id in self.get_page_row_ids():
            row_data = self.get_row_data(row_id)
            row_cells = []

            for column in self.get_visible_columns():
                value = row_data.get(column.key, "")

                cell = self.get_cell(column)
                cell.row_id = row_id
                cell.column_key = column.key
                cell.width = self.column_widths.get(column.key, 0)
                cell.size_hint_x = None
                cell.bind(on_press=self._on_cell_press)  # pyright: ignore

                cell.content.set_table_content(value, row_id=row_id, row_data=row_data)

                row_cells.append(cell)

                self.row_cells.setdefault(row_id, {})[column.key] = cell
                self.column_cells.setdefault(column.key, []).append(cell)

            self.body.add_row(row_cells, self.row_height)

        self.build_header()

    def refresh_layout(self):
        self.refresh_column_widths()

    def sync(self):
        for row_id, cells in self.row_cells.items():
            row_data = self.get_row_data(row_id)

            for cell in cells.values():
                column = self.get_column_by_key(cell.column_key)
                if column is None:
                    continue

                value = row_data.get(column.key, "")
                content = cell.content

                if content is not None:
                    self._set_content_value(content, value, row_id, row_data)

    def _on_column_visibility(self, column, visible):
        self.rebuild()

    def on_width(self, *args):
        self.refresh_column_widths()

    def _set_content_value(self, content, value, row_id, row_data):
        content.set_table_content(
            value,
            row_id=row_id,
            row_data=row_data,
        )

    def get_column_by_key(self, key: str) -> FnTableColumn | None:
        for column in self.columns:
            if column.key == key:
                return column
        return None

    def _on_cell_press(self, cell):
        self.dispatch("on_cell_press", cell)  # pyright: ignore

    def on_cell_press(self, cell: FnTableCell):
        pass
