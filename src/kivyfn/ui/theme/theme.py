# kivyfn.ui.theme.theme.py
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

from kivyfn.ui.theme.color import ThemeColor
from kivyfn.ui.theme.spacing import ThemeSpacing
from kivyfn.ui.theme.state import ThemeState


class Theme(EventDispatcher):
    color: ThemeColor = ObjectProperty(None, rebind=True)
    state: ThemeState = ObjectProperty(None, rebind=True)
    spacing: ThemeSpacing = ObjectProperty(None, rebind=True)

    def __init__(self, **kwargs):
        self._bound_color: ThemeColor | None = None
        super().__init__(**kwargs)

        if self.color is None:
            self.color = ThemeColor()
        if self.state is None:
            self.state = ThemeState()
        if self.spacing is None:
            self.spacing = ThemeSpacing()

    def on_color(self, _theme, color: ThemeColor | None) -> None:
        if color is self._bound_color:
            return
        if self._bound_color is not None:
            self._bound_color.unbind(on_changed=self._on_colors_changed)
        self._bound_color = color
        if color is not None:
            color.bind(on_changed=self._on_colors_changed)

    def _on_colors_changed(self, *_args) -> None:
        # KV expressions using get_role()/alpha() observe the color object,
        # not the properties read inside those methods. Notify them as well.
        self.property("color").dispatch(self)
