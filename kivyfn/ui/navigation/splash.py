from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty

from ..primitives.widget import FnWidget


class FnSplashScreen(FnWidget, Screen):
    len_screens: int = NumericProperty()

    __events__ = ("on_ready",)

    def __init__(self, **kwarg):
        super().__init__(**kwarg)

        self.name = "splash"

    def start(self, len_screens):
        self.len_screens = len_screens

    def update(self, name, index):
        pass

    def ready(self):
        self.dispatch("on_ready")

    def on_ready(self):
        pass
