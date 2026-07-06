from __future__ import annotations

from kivy.properties import DictProperty

from kivyfn.ui.collections.table.cell import FnTableCell
from kivyfn.ui.collections.table.column import FnTableColumn


class FnTableCellCacheMixin:
    cell_cache: dict[str, list[FnTableCell]] = DictProperty({})

    def get_cell(self, column: FnTableColumn):
        cache = self.cell_cache.setdefault(column.key, [])

        if cache:
            return cache.pop()

        # create full cell with content
        cell = FnTableCell(size_hint_x=None)
        cell.column_key = column.key

        content = column.cell_cls()
        cell.add_widget(content)

        return cell

    def release_cell(self, cell: FnTableCell):
        if cell.parent is not None:
            cell.parent.remove_widget(cell)

        self.cell_cache.setdefault(cell.column_key, []).append(cell)

    def release_all_cells(self):
        for cells in self.row_cells.values():  # pyright: ignore
            for cell in cells.values():
                self.release_cell(cell)

        self.row_cells = {}  # pyright: ignore
        self.column_cells = {}  # pyright: ignore
