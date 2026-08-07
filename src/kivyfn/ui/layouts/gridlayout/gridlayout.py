from __future__ import annotations

from typing import Any

from kivy.uix.gridlayout import GridLayout, GridLayoutException

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.layouts.adaptive_size import (
    FnLayoutAdaptiveSizeBehavior,
)


def _nmax(*values: float | None) -> float:
    return max(
        value
        for value in values
        if value is not None
    )


def _nmin(*values: float | None) -> float:
    return min(
        value
        for value in values
        if value is not None
    )


class FnGridLayout(
    FnLayoutAdaptiveSizeBehavior,
    FnWidget,
    GridLayout,
):
    def _get_display_children(self) -> list[FnWidget]:
        return [ # pyright: ignore
            child
            for child in self.children
            if child.display # pyright: ignore
        ]

    def on_children( # pyright: ignore
        self,
        instance: Any,
        children: list[FnWidget],
    ) -> None:
        max_widgets = self.get_max_widgets()

        if (
            max_widgets is not None
            and len(self._get_display_children()) > max_widgets
        ):
            raise GridLayoutException(
                "Too many displayed children in FnGridLayout. "
                "Increase rows or cols."
            )

    def add_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add_widget(
            widget,
            *args,
            **kwargs,
        )

        widget.fbind(
            "display",
            self._on_child_display,
        )

    def remove_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if widget not in self.children:
            return

        widget.funbind(
            "display",
            self._on_child_display,
        )

        super().remove_widget(
            widget,
            *args,
            **kwargs,
        )

    def _on_child_display(
        self,
        widget: FnWidget,
        display: bool,
    ) -> None:
        max_widgets = self.get_max_widgets()

        if (
            display
            and max_widgets is not None
            and len(self._get_display_children()) > max_widgets
        ):
            raise GridLayoutException(
                "Too many displayed children in FnGridLayout. "
                "Increase rows or cols."
            )

        self._trigger_layout() # pyright: ignore

    def _fill_rows_cols_sizes(self) -> None:
        cols = self._cols
        rows = self._rows

        cols_sh = self._cols_sh
        rows_sh = self._rows_sh

        cols_sh_min = self._cols_sh_min
        rows_sh_min = self._rows_sh_min

        cols_sh_max = self._cols_sh_max
        rows_sh_max = self._rows_sh_max

        has_bound_x = False
        has_bound_y = False

        index_iterator = self._create_idx_iter(
            len(cols), # pyright: ignore
            len(rows), # pyright: ignore
        )

        children = self._get_display_children()

        for child, (column, row) in zip(
            reversed(children),
            index_iterator,
        ):
            size_hint_x, size_hint_y = child.size_hint # pyright: ignore
            width, height = child.size # pyright: ignore

            size_hint_min_x, size_hint_min_y = (
                child.size_hint_min # pyright: ignore
            )
            size_hint_max_x, size_hint_max_y = (
                child.size_hint_max # pyright: ignore
            )

            if size_hint_x is None:
                cols[column] = _nmax( # pyright: ignore
                    cols[column], # pyright: ignore
                    width,
                )
            else:
                cols_sh[column] = _nmax( # pyright: ignore
                    cols_sh[column],
                    size_hint_x,
                )

                if size_hint_min_x is not None:
                    has_bound_x = True
                    cols_sh_min[column] = _nmax( # pyright: ignore
                        cols_sh_min[column],
                        size_hint_min_x,
                    )

                if size_hint_max_x is not None:
                    has_bound_x = True
                    cols_sh_max[column] = _nmin( # pyright: ignore
                        cols_sh_max[column],
                        size_hint_max_x,
                    )

            if size_hint_y is None:
                rows[row] = _nmax( # pyright: ignore
                    rows[row], # pyright: ignore
                    height,
                )
            else:
                rows_sh[row] = _nmax( # pyright: ignore
                    rows_sh[row],
                    size_hint_y,
                )

                if size_hint_min_y is not None:
                    has_bound_y = True
                    rows_sh_min[row] = _nmax( # pyright: ignore
                        rows_sh_min[row],
                        size_hint_min_y,
                    )

                if size_hint_max_y is not None:
                    has_bound_y = True
                    rows_sh_max[row] = _nmin( # pyright: ignore
                        rows_sh_max[row],
                        size_hint_max_y,
                    )

        self._has_hint_bound_x = has_bound_x
        self._has_hint_bound_y = has_bound_y

    def do_layout(self, *args: Any) -> None:
        children = self._get_display_children()

        if (
            not children
            or not self._init_rows_cols_sizes(len(children))
        ):
            left, top, right, bottom = self.padding

            self.minimum_size = (
                left + right,
                top + bottom,
            )
            return

        self._fill_rows_cols_sizes()
        self._update_minimum_size()
        self._finalize_rows_cols_sizes()

        for index, x, y, width, height in self._iterate_layout(
            len(children)
        ):
            child = children[index]
            child.pos = x, y # pyright: ignore

            size_hint_x, size_hint_y = child.size_hint # pyright: ignore

            size_hint_min_x, size_hint_min_y = (
                child.size_hint_min # pyright: ignore
            )
            size_hint_max_x, size_hint_max_y = (
                child.size_hint_max # pyright: ignore
            )

            if size_hint_min_x is not None:
                if size_hint_max_x is not None:
                    width = max(
                        min(width, size_hint_max_x),
                        size_hint_min_x,
                    )
                else:
                    width = max(
                        width,
                        size_hint_min_x,
                    )
            elif size_hint_max_x is not None:
                width = min(
                    width,
                    size_hint_max_x,
                )

            if size_hint_min_y is not None:
                if size_hint_max_y is not None:
                    height = max(
                        min(height, size_hint_max_y),
                        size_hint_min_y,
                    )
                else:
                    height = max(
                        height,
                        size_hint_min_y,
                    )
            elif size_hint_max_y is not None:
                height = min(
                    height,
                    size_hint_max_y,
                )

            if size_hint_x is None:
                if size_hint_y is not None:
                    child.height = height # pyright: ignore
            elif size_hint_y is None:
                child.width = width # pyright: ignore
            else:
                child.size = ( # pyright: ignore
                    width,
                    height,
                )
