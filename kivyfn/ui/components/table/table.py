from __future__ import annotations
from typing import Any, Type, Literal, Callable, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainApp

from datetime import datetime
import os

from kivy.core.window import Window
from kivy.base import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ObjectProperty,
    ListProperty,
    BooleanProperty,
    VariableListProperty,
    ColorProperty,
    OptionProperty,
    DictProperty,
)

from theme.components.card import Card
from theme.components.livedata import LiveData
from theme.components.button import ElevatedButton

from resources.icons.md_icons import md_icons
from definitions.icons import icons
from paths import components_path

with open(
    os.path.join(components_path, "table", "table.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class Table(Card):
    name: str = StringProperty("")
    """
    name

    :attr:`name` is a :class:`~kivy.properties.StringProperty`
    """

    # ================================ #
    #           Pagination
    # ================================ #

    dictionary: dict = DictProperty()
    """
    dictionary
    :attr:`dictionary` is a :class:`~kivy.properties.DictProperty`
    """

    items: list = ListProperty()
    """
    items
    :attr:`items` is a :class:`~kivy.properties.ListProperty`
    """

    items_length: int = NumericProperty(0)
    """
    items_length

    :attr:`items_length` is a :class:`~kivy.properties.NumericProperty`
    """

    items_per_page: int = NumericProperty(20)
    """
    items_per_page
    :attr:`items_per_page` is a :class:`~kivy.properties.NumericProperty
    """

    items_per_page_options: list[int] = ListProperty([5, 10, 15, 20])
    """
    items_per_page_options

    :attr:`items_per_page_options` is a :class:`~kivy.properties.List
    """

    items_page_range = ListProperty([0, 0])
    """
    items_page_range

    :attr:`items_page_range` is a :class:`~kivy.properties.ListProperty`
    """

    current_page: int = NumericProperty(0)
    """
    current_page
    :attr:`current_page` is a :class:`~kivy.properties.NumericProperty`
    This is used to track the current page in pagination.
    """

    # ================================ #
    #              sizes
    # ================================ #
    minimum_column_width = NumericProperty(dp(75))
    """
    minimum_column_width

    :attr:`minimum_column_width` is a :class:`~kivy.properties.NumericProperty`
    """

    maximum_column_width = NumericProperty(dp(300))
    """
    maximum_column_width

    :attr:`maximum_column_width` is a :class:`~kivy.properties.NumericProperty`
    """

    adaptive_width: bool = BooleanProperty(True)
    """
    adaptive_width

    :attr:`adaptive_width` is a :class:`~kivy.properties.BooleanProperty`
    """

    adaptive_width_hint: float = ListProperty([0.2, 0.9], allownone=True)
    """
    adaptive_width_hint

    :attr:`adaptive_width_hint` is a :class:`~kivy.properties.ListProperty`
    """

    stretch_children: bool = BooleanProperty(True)
    """
    stretch_children

    :attr:`stretch_children` is a :class:`~kivy.properties.BooleanProperty`
    """

    section_padding = VariableListProperty([dp(6), 0])
    """
    section_padding
    :attr:`section_padding` is a :class:`~kivy.properties.VariableListProperty`
    """

    section_spacing = NumericProperty(dp(12))
    """
    section_spacing
    :attr:`section_spacing` is a :class:`~kivy.properties.NumericProperty`
    """

    column_size: Literal["auto", "fixed"] = OptionProperty(
        "auto", options=["auto", "fixed"]
    )
    """
    column_size

    :attr:`column_size` is a :class:`~kivy.properties.OptionProperty`
    """

    # ================================ #
    #            colors
    # ================================ #
    column_selection_background_color = ColorProperty([0, 0, 0, 0.1])
    """
    column_selection_background_color

    :attr:`column_selection_background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    column_selection_text_color = ColorProperty([0, 0, 0, 0.1])
    """
    column_selection_text_color

    :attr:`column_selection_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    row_selection_background_color = ColorProperty([0, 0, 0, 0.1])
    """
    row_selection_background_color

    :attr:`row_selection_background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    row_selection_text_color = ColorProperty([0, 0, 0, 0.1])
    """
    row_selection_text_color

    :attr:`row_selection_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    # ================================ #
    #               Cls
    # ================================ #
    row_factory = StringProperty()
    """
    row_factory

    :attr:`row_factory` is a :class:`~kivy.properties.StringProperty`
    """

    row_cache: dict[str, list[TableRow]] = DictProperty()
    """
    row_cache

    :attr:`row_cache` is a :class:`~kivy.properties.DictProperty`
    """

    header_factory: str = StringProperty()
    """
    header_factory

    :attr:`header_factory` is a :class:`~kivy.properties.StringProperty`
    """

    header_cache: dict[str, TableHeader] = DictProperty()
    """
    `header_cache`

    :attr:`header_cache` is a :class:`~kivy.properties.DictProperty`
    """

    section_header_factory: str = StringProperty(None, allownone=True)
    """
    section_header_factory

    :attr:`section_header_factory` is a :class:`~kivy.properties.StringProperty`
    """

    section_header_cache: dict[str, TableSectionHeader] = DictProperty()
    """
    section_header_cache

    :attr:`section_header_cache` is a :class:`~kivy.properties.DictProperty`
    """

    # ================================ #
    #             Sections
    # ================================ #
    section_header = ObjectProperty(None, allownone=True)
    """
    section_header

    :attr:`section_header` is a :class:`~widgets.uix.table.TableSectionHeader`
    """

    header: Type[TableHeader] = ObjectProperty()
    """
    The header of the table, typically contains column names or titles.

    :attr:`header` is a :class:`~widgets.uix.table.TableHeader`
    """

    body: Type[TableBody] = ObjectProperty()
    """
    The body of the table, contains the main content and data rows.

    :attr:`body` is a :class:`~widgets.uix.table.TableBody`
    """

    footer: Type[TableFooter] = ObjectProperty()
    """
    The footer of the table, typically contains summary or additional information.

    :attr:`footer` is a :class:`~widgets.uix.table.TableFooter`
    """

    app: Type[MainApp] = ObjectProperty()
    """
    app

    :attr:`app` is a :class:`~widgets.uix.app.App`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_trigger = Clock.create_trigger(self.compute_column_width, -1)

    # ================================ #
    #             Widgets
    # ================================ #
    def add_widget(
        self,
        widget: TableSectionHeader | TableHeader | TableBody | TableFooter | TableRow,
        *args,
        **kwargs,
    ) -> None:
        if isinstance(widget, TableSectionHeader):
            self.section_header = widget
            if self.body:
                self.body.bind(scroll_x=self.section_header.setter("scroll_x"))
            super().add_widget(widget, index=len(self.children))

        elif isinstance(widget, TableHeader):
            self.header = widget

            if self.body:
                self.body.bind(scroll_x=self.header.setter("scroll_x"))

            if self.section_header is None:
                super().add_widget(widget, index=len(self.children))
            else:
                super().add_widget(widget, index=len(self.children) - 1)

        elif isinstance(widget, TableBody):
            self.body = widget
            if self.header:
                self.body.bind(scroll_x=self.header.setter("scroll_x"))

            if self.section_header:
                self.body.bind(scroll_x=self.section_header.setter("scroll_x"))
            super().add_widget(widget, *args, **kwargs)

        elif isinstance(widget, TableFooter):
            self.footer = widget
            super().add_widget(widget, *args, **kwargs)

        elif isinstance(widget, TableRow):
            self.body.add_widget(widget, *args, **kwargs)

        else:
            raise TypeError(
                "Widget must be an instance of TableHeader, TableBody, TableFooter, or TableRow."
            )

    def remove_widget(self, widget, *args, **kwargs) -> None:
        if isinstance(widget, TableRow):
            self.body.remove_widget(widget, *args, **kwargs)

        elif isinstance(widget, TableHeader):
            self.body.unbind(scroll_x=widget.setter("scroll_x"))
            super().remove_widget(widget, *args, **kwargs)

        elif isinstance(widget, TableSectionHeader):
            self.section_header = None
            self.body.unbind(scroll_x=widget.setter("scroll_x"))
            super().remove_widget(widget, *args, **kwargs)

    def clear_widgets(self, *args, **kwargs) -> None:
        self.body.clear_widgets(*args, **kwargs)

    def update_row_cache(self):
        """
        Set the row_cache for the table.
        This is used to store the items for performance optimization.
        """

        row_cls = getattr(Factory, self.row_factory, None)
        if not row_cls:
            raise ValueError(f"Row factory '{self.row_factory}' not found in Factory.")

        row_factory = self.row_factory
        self.row_cache.setdefault(row_factory, [])

        # Only create as many rows as you actually have items
        needed = min(self.items_per_page, len(self.items))
        length = len(self.row_cache[row_factory])

        if length < needed:
            self.row_cache[row_factory].extend(
                row_cls() for _ in range(needed - length)
            )

    # ================================ #
    #             update
    # ================================ #
    def update(self, data: dict):
        """
        Update an existing item in the recycler by its index.
        The data should contain the properties to update.
        """

        index = data["index"]

        for row in self.body.container.children:
            if row.index == index:
                for key, value in data.items():
                    setattr(row, key, value)

        for item in self.items:
            if item["index"] == index:
                for key, value in data.items():
                    item[key] = value

    def lookup(self, index: Any) -> Tuple[TableRow | None, Dict | None]:
        """
        Lookup an item in the table by its index.
        Returns the TableRow and the corresponding data dictionary.
        """
        widget = None
        for row in self.body.container.children:
            if row.index == index:
                widget = row
                break

        row = None
        for item in self.items:
            if item["index"] == index:
                row = item
                break

        return widget, row

    def sort(
        self,
        sort: Literal["ascending", "descending"],
        sort_key: str,
        cast: Callable,
    ):
        reverse = sort == "descending"

        good, bad = [], []
        for item in self.items:
            try:
                cast(item[sort_key])
                good.append(item)
            except Exception:
                bad.append(item)

        good.sort(key=lambda item: cast(item[sort_key]), reverse=reverse)
        self.items = good + bad

    # ================================ #
    #             Events
    # ================================ #
    def on_items(self, *args):
        def on_items(*args):
            self.items_length = len(self.items)
            self.refresh()

        Clock.schedule_once(on_items, -1)

    def on_dictionary(self, instance, value):
        self.items = list(value.values())

    def on_items_per_page(self, *args):
        self.refresh()

    def on_current_page(self, *args):
        self.refresh()

    def on_parent(self, instance, parent):
        self.parent.bind(size=self.on_parent_size)

    def on_parent_size(self, instance, size):
        """
        Callback when the parent size changes. This is used to adjust the table width.
        """

        self.size_trigger.cancel()
        self.size_trigger()

    # ================================ #
    #            Factories
    # ================================ #
    def on_row_factory(self, instance, value: str):
        row_cls = getattr(Factory, value, None)
        if row_cls is None:
            raise ValueError(f"Row factory '{value}' not found in Factory.")

        self.clear_widgets()

    def on_header_factory(self, instance, value: str):
        header_cls = getattr(Factory, value, None)
        if header_cls is None:
            raise ValueError(f"Header factory '{value}' not found in Factory.")

        if self.header:
            self.remove_widget(self.header)

        self.add_widget(header_cls())

    def on_section_header_factory(self, instance, value: str):
        if value is None:
            if self.section_header:
                self.remove_widget(self.section_header)
        else:
            section_header_cls = getattr(Factory, value, None)
            if section_header_cls is None:
                raise ValueError(
                    f"Section header factory '{value}' not found in Factory."
                )

            if self.section_header:
                self.remove_widget(self.section_header)

            self.add_widget(section_header_cls())

    # ================================ #
    #          Table Pagination
    # ================================ #
    def compute_column_width(self, *args):
        columns = self.get_transpose_widths()
        max_widths = [max(max(col), self.minimum_column_width) for col in columns]
        if self.adaptive_width:
            self.size_hint_x = None
            cell_sum_width = sum(max_widths)
            spacing = self.section_spacing * len(max_widths)
            padding = self.section_padding[0] + self.section_padding[3]
            width = cell_sum_width + spacing + padding

            if self.adaptive_width_hint is not None:
                parent_width = self.parent.width
                min_hint, max_hint = self.adaptive_width_hint
                self.width = max(
                    min(width, max_hint * parent_width), min_hint * parent_width
                )

            else:
                self.width = width

        columns = self.get_transpose_cells()
        for index, column in enumerate(columns):
            for cell in column:
                cell.width = max_widths[index]

        if self.stretch_children:
            columns = self.get_transpose_children()
            for index, column in enumerate(columns):
                for child in column:
                    if hasattr(child, "allow_stretch") and child.allow_stretch:
                        child.custom_width = max_widths[index]

        # Set the widths of the section header children
        index = 0  # pointer into max_widths
        children = self.get_section_header_children()
        for child in children:
            col_span = getattr(child, "col_span")
            child.parent.width = (
                sum(max_widths[index : index + col_span])
                + (col_span - 1) * self.section_spacing
            )
            index += col_span

    def refresh(self):
        """
        Refresh the table by clearing the current items and re-adding them.
        This is useful when the data changes and needs to be updated.
        """

        if not self.row_factory:
            return

        self.update_row_cache()
        row_factory = self.row_factory
        row_cache = self.row_cache.get(row_factory, [])

        page_delta = len(self.get_page_rows()) - len(self.get_page_items())

        if page_delta > 0:
            for _ in range(page_delta):
                self.body.container.remove_widget(self.body.container.children[-1])

        elif page_delta < 0:
            widgets = [widget for widget in row_cache if not widget.parent]
            for _ in range(abs(page_delta)):
                widget = widgets.pop()
                self.body.container.add_widget(widget)

        for row, item in zip(reversed(self.get_page_rows()), self.get_page_items()):
            setattr(row, "item", item)

        self.size_trigger.cancel()
        self.size_trigger()

    def next_page(self, footer, page):
        self.current_page = page

    def previous_page(self, footer, page):
        self.current_page = page

    # ================================ #
    #          Transpose
    # ================================ #
    def get_transpose_cells(self) -> list[list[TableCell]]:
        """
        Returns a transposed list of all cell widgets including the header.
        This is useful for displaying the table in a different format, such as columns.
        """

        if not self.do_transpose_headers:
            return []

        cells = [[cell for cell in self.header.children[0].children]]
        if not self.do_transpose_rows:
            return list(zip(*cells))

        for row in self.get_page_rows():
            row_cells = [cell for cell in row.children]
            cells.append(row_cells)

        transposed = list(zip(*cells))
        return transposed

    def get_transpose_children(self) -> list[list[dict]]:
        """
        Returns a transposed list of all cell widgets including the header.
        """

        if not self.do_transpose_headers:
            return []

        items = [[child.children[0] for child in self.header.children[0].children]]
        if not self.do_transpose_rows:
            return list(zip(*items))

        for row in self.get_page_rows():
            row_items = [cell.children[0] for cell in row.children]
            items.append(row_items)

        transposed = list(zip(*items))
        return transposed

    def get_transpose_widths(self) -> list[list[float]]:
        """
        Returns a transposed list of all cell widths including the header.
        This is useful for calculating the widths of each column in the table.
        """

        if not self.do_transpose_headers:
            return []

        widths = [
            [child.children[0].width for child in self.header.children[0].children]
        ]
        if not self.do_transpose_rows:
            return list(zip(*widths))

        for row in self.get_page_rows():
            row_widths = [cell.children[0].width for cell in row.children]
            widths.append(row_widths)

        transposed = list(zip(*widths))
        return transposed

    @property
    def do_transpose_headers(self) -> bool:
        if not self.header or not self.header.children[0]:
            return False

        return True

    @property
    def do_transpose_rows(self) -> bool:
        """
        Determines if the table allows computation of transposed widths.
        This is useful for checking if the table is in a state where it can compute widths.
        """

        if not self.get_page_rows():
            return False

        return True

    # ================================ #
    #          Properties
    # ================================ #
    def get_page_rows(self) -> int:
        """
        Returns the number of rows in the table.
        This is used for pagination and other calculations.
        """
        return self.body.container.children

    def get_page_items(self, page_number=None) -> list[TableRow]:
        """
        Returns the items for the current page based on the page_slice.
        This is used to display only the items for the current page.
        """

        if page_number is None:
            page = self.current_page

        else:
            page = page_number

        start = page * self.items_per_page
        end = start + self.items_per_page

        if page_number is None:
            self.items_page_range = [start, end]

        return self.items[slice(start, end)]

    # ================================ #
    #           children
    # ================================ #
    def get_section_header_children(self) -> list[TableSectionHeaderCell]:
        """
        Returns the children of the section header.
        This is useful for accessing the section header cells directly.
        """

        if not self.section_header or not self.section_header.container:
            return []

        return [child.children[0] for child in self.section_header.container.children]

    def get_header_children(self) -> list[TableHeaderCell]:
        """
        Returns the children of the header.
        This is useful for accessing the header cells directly.
        """

        if not self.header or not self.header.container:
            return []

        return [child for child in self.header.container.children]

    def get_body_children(self) -> list[TableRow]:
        """
        Returns the children of the body.
        This is useful for accessing the body rows directly.
        """

        if not self.body or not self.body.container:
            return []

        return [child for child in self.body.container.children]


# ================================ #
#             Sections
# ================================ #
class TableContainer(BoxLayout):
    pass


class TableSectionHeader(ScrollView):
    container: Type[BoxLayout] = ObjectProperty()
    """
    container

    :attr:`container` is a :class:`~kivy.uix.boxlayout.BoxLayout`
    """

    table: Type[Table] = ObjectProperty(None, allownone=True)
    """
    table

    :attr:`table` is a :class:`~widgets.uix.table.Table`
    """

    def on_parent(self, instance, parent):
        self.table = parent

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, TableContainer):
            self.container = widget
            return super().add_widget(widget, *args, **kwargs)

        cell = TableSectionHeaderCell()
        cell.add_widget(widget, *args, **kwargs)
        return self.container.add_widget(cell, *args, **kwargs)


class TableHeader(ScrollView):
    container: Type[BoxLayout] = ObjectProperty()
    """
    container

    :attr:`container` is a :class:`~kivy.uix.boxlayout.BoxLayout`
    """

    table: Type[Table] = ObjectProperty(None, allownone=True)
    """
    table

    :attr:`table` is a :class:`~widgets.uix.table.Table`
    """

    def on_parent(self, instance, parent):
        self.table = parent
        if self.container:
            for child in self.container.children:
                if isinstance(child, TableHeaderCell):
                    child.table = self.table

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, TableContainer):
            self.container = widget
            return super().add_widget(widget, *args, **kwargs)

        cell = TableHeaderCell()
        cell.add_widget(widget, *args, **kwargs)
        return self.container.add_widget(cell, *args, **kwargs)


class TableBody(ScrollView):
    container: Type[BoxLayout] = ObjectProperty()

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, TableContainer):
            self.container = widget
            return super().add_widget(widget, *args, **kwargs)

        return self.container.add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        self.container.remove_widget(widget, *args, **kwargs)

    def clear_widgets(self, children=None):
        self.container.clear_widgets(children)


class TableFooter(Card):
    app: Type[App] = ObjectProperty()
    """
    app

    :attr:`app` is a :class:`~widgets.uix.app.App`
    """

    table: Type[Table] = ObjectProperty()
    """
    table

    :attr:`table` is a :class:`~widgets.uix.table.Table`
    """

    def __init__(self, **kwarg):
        super().__init__(**kwarg)

    def on_parent(self, instance, parent):
        self.table = parent

    def next_page(self):
        """
        Go to the next page in pagination.
        """
        if self.table.get_page_items(self.table.current_page + 1):
            self.table.current_page = self.table.current_page + 1

    def previous_page(self):
        """
        Go to the previous page in pagination.
        """
        if self.table.current_page > 0:
            self.table.current_page = self.table.current_page - 1

    # ================================ #
    #             Menu
    # ================================ #
    def open_menu(self, caller):
        items = [
            {"text": str(page), "on_release": lambda x=page: self.on_menu_callback(x)}
            for page in self.table.items_per_page_options
        ]

        self.app.ui.dropdown.orientation = "vertical"
        self.app.ui.dropdown.caller = caller
        self.app.ui.dropdown.items = items
        self.app.ui.dropdown.open()

    def on_menu_callback(self, value):
        """
        Callback for when the menu is closed.
        This is used to update the items_per_page based on the selected value.
        """

        self.table.items_per_page = value
        self.app.ui.dropdown.dismiss()


# ================================ #
#             Rows
# ================================ #
class TableRow(Card):
    index: int = NumericProperty()
    """
    index

    :attr:`index` is a :class:`~kivy.properties.NumericProperty`
    """

    table: Type[Table] = ObjectProperty()
    """
    table

    :attr:`table` is a :class:`~theme.components.table.Table`
    """

    item: dict = ObjectProperty()
    """
    `item` hold reference item in the table so updates can reflect on the table directly.

    :attr:`item` is a :class:`~kivy.properties.ObjectProperty`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_touch_down=self.window_touch_down)

        self.initialized = False

    def on_item(self, instance, value):
        if value:
            for key, val in value.items():
                setattr(self, key, val)

    def on_parent(self, instance, parent):
        if not self.initialized:
            self.initialized = True
            self.table = parent.parent.parent

    def on_touch_down(self, touch):
        has_touch = super().on_touch_down(touch)
        if self.collide_point(*touch.pos) and not has_touch:
            self.background_color = self.table.row_selection_background_color
        return has_touch

    def add_widget(self, widget, *args, **kwargs):
        cell = TableRowCell()
        cell.add_widget(widget, *args, **kwargs)
        return super().add_widget(cell, *args, **kwargs)

    def window_touch_down(self, window, touch):
        local_x, local_y = self.to_widget(*touch.pos)
        if not self.collide_point(local_x, local_y):
            self.background_color = [0, 0, 0, 0]


# =============================== #
#             Cells
# ================================ #
class TableCell(Card):
    pass


class TableRowCell(TableCell):
    pass


class TableHeaderCell(TableCell):
    table: Type[Table] = ObjectProperty(None, allownone=True)
    """
    table
    
    :attr:`table` is a :class:`~widgets.uix.table.Table`
    """

    selected: bool = BooleanProperty(False)
    """
    selected

    :attr:`selected` is a :class:`~kivy.properties.BooleanProperty`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_touch_down=self.window_touch_down)

    def on_touch_down(self, touch):
        has_touch = super().on_touch_down(touch)
        if self.collide_point(*touch.pos) and not has_touch:
            self.selected = True
            if self.table:
                cells = self.table.get_transpose_cells()
                for cell in cells[self.index]:
                    cell.background_color = self.table.column_selection_background_color

        return has_touch

    def window_touch_down(self, window, touch):
        local_x, local_y = self.to_widget(*touch.pos)
        if not self.collide_point(local_x, local_y) and self.selected:
            self.selected = False
            if self.table:
                cells = self.table.get_transpose_cells()
                for cell in cells[self.index]:
                    cell.background_color = [0, 0, 0, 0.0]

    @property
    def index(self) -> int:
        """
        Returns the index of the current column based on the header.
        This is useful for sorting or other operations that require column identification.
        """
        return self.parent.children.index(self)


class TableSectionHeaderCell(AnchorLayout):
    pass


# ================================ #
#              Label
# ================================ #
class CoreTableText(Label):
    text_key = StringProperty()
    """
    `text_key`

    :attr:`text_key` is a :class:`~kivy.properties.StringProperty`
    """

    custom_width: int = NumericProperty(None, allownone=True)
    """
    `custom_width`
    
    :attr:`custom_width` is a :class:`~kivy.properties.NumericProperty`
    """

    custom_height: int = NumericProperty(None, allownone=True)
    """
    `custom_height`

    :attr:`custom_height` is a :class:`~kivy.properties.NumericProperty`
    """

    text_color: list = ColorProperty([0, 0, 0, 1])
    """
    `text_color`

    :attr:`text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    disabled_text_color: list = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    `disabled_text_color`

    :attr:`disabled_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    background_color: list = ColorProperty([0, 0, 0, 0])
    """
    `background_color` 

    is a list representing the RGBA color of the background.
    """

    radius: list[float] = VariableListProperty(dp(5))
    """
    `radius`

    :attr:`radius` is a :class:`~kivy.properties.VariableListProperty`
    """

    leading_text: str = StringProperty("")
    """
    `leading_text`

    :attr:`leading_text` is a :class:`~kivy.properties.StringProperty`
    """

    trailing_text: str = StringProperty("")
    """
    `trailing_text`

    :attr:`trailing_text` is a :class:`~kivy.properties.StringProperty
    """

    leading_delimiter: str = StringProperty("  ")
    """
    `leading_delimiter`

    :attr:`leading_delimiter` is a :class:`~kivy.properties.StringProperty
    """

    trailing_delimiter: str = StringProperty(" ")
    """
    `trailing_delimiter`

    :attr:`trailing_delimiter` is a :class:`~kivy.properties.StringProperty`
    """

    icon_delimiter: str = StringProperty(" ")
    """
    `icon_delimiter`

    :attr:`icon_delimiter` is a :class:`~kivy.properties.StringProperty`
    """

    icon: str = StringProperty(None, allownone=True)
    """
    `icon`

    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    """

    icon_markup: str = StringProperty("")
    """
    `icon_markup`

    :attr:`icon_markup` is a :class:`~kivy.properties.StringProperty`
    """

    allow_stretch: bool = BooleanProperty(False)
    """
    `allow_stretch`

    :attr:`allow_stretch` is a :class:`~kivy.properties.BooleanProperty`
    """

    def on_icon(self, instance, value):
        if value:
            if value in icons:
                value = md_icons[icons[value]]
            elif value in md_icons:
                value = md_icons[value]
            else:
                raise ValueError(f"Icon '{value}' not found in md_icons.")

            self.icon_markup = f"[font=Icons]{value}[/font]"
        else:
            self.icon_markup = ""


class TableText(CoreTableText):
    pass


class TableLiveText(CoreTableText, LiveData):
    pass


class TableHeaderText(CoreTableText):
    allow_sort: bool = BooleanProperty(False)
    """
    `allow_sort`

    :attr:`allow_sort` is a :class:`~kivy.properties.BooleanProperty`
    """

    sort: Literal["ascending", "descending"] = OptionProperty(
        "ascending", options=["ascending", "descending"]
    )
    """
    `sort`

    :attr:`sort` is a :class:`~kivy.properties.BooleanProperty`
    """

    sort_key: str = StringProperty(None, allownone=True)
    """
    `sort_key`

    :attr:`sort_key` is a :class:`~kivy.properties.StringProperty`
    """

    cast: Callable = ObjectProperty()
    """
    `cast`

    :attr:`cast` is a :class:`~kivy.properties.ObjectProperty`
    """

    sort_cast: Literal["string", "number", "date", "time"] = ObjectProperty(
        "number", options=["string", "number", "date", "time"]
    )
    """
    `sort_cast`

    :attr:`sort_cast` is a :class:`~kivy.properties.ObjectProperty`
    """

    date_cast_format: str = StringProperty("%Y-%m-%d %H:%M:%S")
    """
    `date_cast_format`

    :attr:`date_cast_format` is a :class:`~kivy.properties.StringProperty`
    """

    time_cast_format: str = StringProperty("%H:%M:%S")
    """
    `time_cast_format`

    :attr:`time_cast_format` is a :class:`~kivy.properties.StringProperty`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.on_sort_cast(self, self.sort_cast)

    def on_sort(self, instance, sort):
        if sort == "ascending":
            self.icon = "menu-down"
        elif sort == "descending":
            self.icon = "menu-up"

        if self.sort_key is None:
            return

        self.table.sort(sort, self.sort_key, self.cast)

    def on_sort_cast(self, instance, value):
        if value == "string":
            self.cast = str
        elif value == "number":
            self.cast = float
        elif value == "date":
            self.cast = lambda x: datetime.strptime(x, self.date_cast_format)
        elif value == "time":
            self.cast = lambda x: datetime.strptime(x, self.time_cast_format).time()
        else:
            raise ValueError(f"Invalid sort cast '{value}'")

    def on_allow_sort(self, instance, value):
        if value:
            self.icon = "menu-down"
        else:
            self.icon = ""

    def on_touch_down(self, touch):
        if not self.allow_sort or not self.table or not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        local_x, local_y = self.to_local(*touch.pos, relative=True)
        for ref, boxes in self.refs.items():
            for x1, y1, x2, y2 in boxes:
                if x1 <= local_x <= x2 and y1 <= local_y <= y2:
                    self.sort = (
                        "ascending" if self.sort == "descending" else "descending"
                    )
                    return True

        return super().on_touch_down(touch)

    @property
    def table(self) -> Table:
        return self.parent.table


class TableSectionHeaderText(Label):
    col_span: int = NumericProperty(1)
    """
    col_span

    :attr:`col_span` is a :class:`~kivy.properties.NumericProperty`
    """

    text_key: str = StringProperty("")
    """
    text_key

    :attr:`text_key` is a :class:`~kivy.properties.StringProperty`
    """

    trailing_text: str = StringProperty("")
    """
    trailing_text

    :attr:`trailing_text` is a :class:`~kivy.properties.StringProperty`
    """

    trailing_delimiter: str = StringProperty("  ")
    """
    trailing_delimiter

    :attr:`trailing_delimiter` is a :class:`~kivy.properties.StringProperty`
    """


# ================================ #
#             Button
# ================================ #
class TableButton(ElevatedButton):
    pass
