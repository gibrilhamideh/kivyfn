from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.collections.table.cell import FnTableCell


class FnTableRow(FnWidget, BoxLayout):
    cells: list[FnTableCell] = ListProperty()

    def set_row_content(self, row_id, row_data, columns):
        for column, cell in zip(columns, self.cells):
            value = row_data.get(column.key, "")
            cell.set_table_content(value)
