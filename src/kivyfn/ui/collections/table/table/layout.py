from __future__ import annotations

from kivy.metrics import dp
from kivy.properties import DictProperty

from kivyfn.ui.collections.table.column import FnTableColumn


class FnTableLayoutMixin:
    column_widths: dict[str, float] = DictProperty({})

    def get_visible_columns(self) -> list[FnTableColumn]:
        return [column for column in self.columns if column.visible]  # pyright: ignore

    def get_column_by_key(self, key: str):
        for column in self.columns:  # pyright: ignore
            if column.key == key:
                return column
        return None

    def refresh_column_widths(self):
        self.column_widths = self.compute_column_widths()
        self.apply_column_widths()

    def parse_column_width(self, width) -> tuple[str, float]:
        if width is None:
            return "fr", 1

        if isinstance(width, (int, float)):
            return "px", float(width)

        if not isinstance(width, str):
            raise TypeError(f"Invalid column width: {width!r}")

        value = width.strip().lower()

        if value.endswith("dp"):
            return "px", dp(float(value[:-2]))

        if value.endswith("px"):
            return "px", float(value[:-2])

        if value.endswith("%"):
            return "percent", float(value[:-1]) / 100

        if value.endswith("fr"):
            return "fr", float(value[:-2])

        return "px", float(value)

    def compute_column_widths(self) -> dict[str, float]:
        table_width = self.width  # pyright: ignore

        fixed_total = 0
        percent_total = 0
        fr_total = 0
        parsed = []

        for column in self.get_visible_columns():
            kind, value = self.parse_column_width(column.width)
            parsed.append((column, kind, value))

            if kind == "px":
                fixed_total += value
            elif kind == "percent":
                percent_total += table_width * value
            elif kind == "fr":
                fr_total += value

        remaining = max(0, table_width - fixed_total - percent_total)

        widths = {}

        for column, kind, value in parsed:
            if kind == "px":
                widths[column.key] = value
            elif kind == "percent":
                widths[column.key] = table_width * value
            elif kind == "fr":
                widths[column.key] = remaining * (value / fr_total) if fr_total else 0

        return widths

    def apply_column_widths(self):
        for key, width in self.column_widths.items():
            for cell in self.column_cells.get(key, []):  # pyright: ignore
                cell.size_hint_x = None
                cell.width = width

            cell = self.header.cells.get(key)  # pyright: ignore
            if cell is not None:
                cell.width = width
