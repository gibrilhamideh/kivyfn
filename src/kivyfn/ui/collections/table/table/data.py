from __future__ import annotations

import copy
from uuid import uuid4

from kivy.properties import DictProperty, ListProperty, NumericProperty


class FnTableDataMixin:
    data: dict[str, dict] = DictProperty({})
    row_order: list[str] = ListProperty([])

    page_index: int = NumericProperty(0)
    page_size: int = NumericProperty(20)

    # -------------------------
    # Bulk data
    # -------------------------
    def set_rows(self, rows: dict[str, dict] | list[dict]):
        self.data = {}
        self.row_order = []

        if isinstance(rows, dict):
            self.data = copy.deepcopy(rows)
            self.row_order = list(rows.keys())

        elif isinstance(rows, list):
            for row in rows:
                row_id = str(uuid4())
                self.data[row_id] = copy.deepcopy(row)
                self.row_order.append(row_id)

        else:
            raise TypeError("rows must be dict[str, dict] or list[dict]")

        self.page_index = 0
        self.rebuild()  # pyright: ignore

    # -------------------------
    # Row mutation
    # -------------------------
    def insert(self, row: dict, id: str | None = None):
        if id is None:
            id = str(uuid4())

        if id in self.data:
            raise ValueError(f"Row '{id}' already exists")

        self.data[id] = copy.deepcopy(row)
        self.row_order.append(id)

        if self._is_row_on_current_page(id):
            self.rebuild()  # pyright: ignore

        return id

    def remove(self, id: str):
        if id not in self.data:
            return

        was_visible = self._is_row_visible(id)

        del self.data[id]
        self.row_order.remove(id)

        max_page = max(0, self.get_total_pages() - 1)
        if self.page_index > max_page:
            self.page_index = max_page
            self.rebuild()  # pyright: ignore
            return

        if was_visible:
            self.rebuild()  # pyright: ignore

    def setrow(self, id: str, column_key: str, value):
        if id not in self.data:
            raise ValueError(f"Row '{id}' does not exist")

        self.data[id][column_key] = value

        if self._is_row_visible(id):
            self.sync()  # pyright: ignore

    # -------------------------
    # Pagination
    # -------------------------
    def set_page(self, page_index: int):
        max_page = max(0, self.get_total_pages() - 1)
        page_index = max(0, min(page_index, max_page))

        if self.page_index == page_index:
            return

        self.page_index = page_index
        self.rebuild()  # pyright: ignore

    def set_page_size(self, page_size: int):
        page_size = max(1, page_size)

        if self.page_size == page_size:
            return

        self.page_size = page_size
        self.page_index = 0
        self.rebuild()  # pyright: ignore

    # -------------------------
    # Read helpers
    # -------------------------
    def get_page_row_count(self) -> int:
        return len(self.get_page_row_ids())

    def get_total_rows(self) -> int:
        return len(self.row_order)

    def get_total_pages(self) -> int:
        if not self.row_order:
            return 0

        return (len(self.row_order) + self.page_size - 1) // self.page_size

    def get_page_row_ids(self) -> list[str]:
        start = self.page_index * self.page_size
        end = start + self.page_size
        return self.row_order[start:end]

    def get_row_data(self, row_id: str) -> dict:
        return self.data.get(row_id, {})

    def get_cell_value(self, row_id: str, column_key: str):
        return self.get_row_data(row_id).get(column_key, "")

    # -------------------------
    # Sorting
    # -------------------------
    def sort_by_column(self, column_key: str, descending: bool = False):
        column = self.get_column_by_key(column_key)  # pyright: ignore
        if column is None:
            return

        def sort_key(row_id: str):
            row_data = self.get_row_data(row_id)
            value = row_data.get(column.key, "")

            if column.sort_func is not None:
                return column.sort_func(value, row_data, row_id)

            return value

        self.row_order.sort(key=sort_key, reverse=descending)
        self.page_index = 0
        self.rebuild()  # pyright: ignore

    # -------------------------
    # Optimization helpers
    # -------------------------
    def _is_row_visible(self, row_id: str) -> bool:
        return row_id in self.row_cells  # pyright: ignore

    def _is_row_on_current_page(self, row_id: str) -> bool:
        return row_id in self.get_page_row_ids()
