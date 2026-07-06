from kivy.uix.floatlayout import FloatLayout
from kivy.properties import BooleanProperty

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.layouts.floatlayout import FnFloatLayout
from kivyfn.ui.behaviors.style import FnBackgroundBehavior

class FnRoot(FnBackgroundBehavior, FnWidget, FloatLayout):
    attached = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.content_layer = FnFloatLayout()
        self.overlay_layer = FnFloatLayout()
        self.modal_layer = FnFloatLayout()

        super().add_widget(self.content_layer)
        super().add_widget(self.overlay_layer)
        super().add_widget(self.modal_layer)

    def add_widget(self, widget, *args, **kwargs):
        return self.content_layer.add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        return self.content_layer.remove_widget(widget, *args, **kwargs)

    def add_overlay(self, widget):
        return self.overlay_layer.add_widget(widget)

    def remove_overlay(self, widget):
        return self.overlay_layer.remove_widget(widget)

    def clear_overlays(self):
        return self.overlay_layer.clear_widgets()

    def add_modal(self, widget):
        return self.modal_layer.add_widget(widget)

    def remove_modal(self, widget):
        return self.modal_layer.remove_widget(widget)

    def clear_modals(self):
        return self.modal_layer.clear_widgets()


