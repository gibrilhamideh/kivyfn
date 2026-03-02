from kivyfn.fonts import fonts

from .base import FnWidget


class FnTextWidget(FnWidget):
    def on_kv_post(self, base_widget):
        self.font_name = fonts.current
        fonts.bind(current=self._apply_font)

    def _apply_font(self, instance, value):
        self.font_name = value
