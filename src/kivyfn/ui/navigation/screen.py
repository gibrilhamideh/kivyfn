from kivy.uix.screenmanager import Screen

from ..primitives.widget import FnWidget


class FnScreen(Screen):
    __events__ = ("on_ready",)

    # ================================ #
    # Events
    # ================================ #
    def on_build(self):
        self.ready()

    def on_ready(self, *_):
        pass

    # ================================ #
    # API
    # ================================ #
    def ready(self):
        self.dispatch("on_ready")
