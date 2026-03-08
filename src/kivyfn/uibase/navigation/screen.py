from kivy.uix.screenmanager import Screen


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
