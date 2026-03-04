from kivy.properties import StringProperty, BooleanProperty
from kivyfn.fonts import fonts


class FnTextBehavior:
    """
    Text capability mixin.

    Handles font resolution based on:
    - Explicit font override
    - Font role
    - Current language
    """

    font_role = StringProperty("system")
    """
    Semantic font role.
    Examples: system, display, monospace.
    """

    use_system_font = BooleanProperty(True)
    """
    Whether to automatically bind to the framework font manager.
    """

    def on_kv_post(self, base_widget):
        self.font_name = fonts.current
        fonts.bind(current=self._apply_font)

    def _apply_font(self, instance, value):
        self.font_name = value
