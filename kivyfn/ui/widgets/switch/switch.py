import os
from kivy.base import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.properties import (
    ColorProperty,
    NumericProperty,
    ListProperty,
    BooleanProperty,
)

from kivycore.store import Action
from kivycore.store.bus import BusMixin

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "switch", "switch.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class KcSwitch(Widget, BusMixin):
    background_color = ColorProperty()
    """
    `background_color`
    
    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    active_background_color = ColorProperty([1, 0, 0, 0.25])
    """
    `active_background_color`

    :attr:`active_background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    inactive_background_color = ColorProperty([0, 0, 0, 0.25])
    """
    `inactive_background_color`

    :attr:`inactive_background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    border_color = ColorProperty()
    """
    `border_color`

    :attr:`border_color` is a :class:`~kivy.properties.ColorProperty`
    """

    active_border_color = ColorProperty([0, 0, 0, 0])
    """
    `active_border_color`

    :attr:`active_border_color` is a :class:`~kivy.properties.ColorProperty`
    """

    inactive_border_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    `inactive_border_color`

    :attr:`inactive_border_color` is a :class:`~kivy.properties.ColorProperty`
    """

    switch_color = ColorProperty()
    """
    `switch_color`

    :attr:`switch_color` is a :class:`~kivy.properties.ColorProperty`
    """

    active_switch_color = ColorProperty([1, 0, 0, 1])
    """
    `active_switch_color`

    :attr:`active_switch_color` is a :class:`~kivy.properties.ColorProperty`
    """

    inactive_switch_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    `inactive_switch_color`

    :attr:`inactive_switch_color` is a :class:`~kivy.properties.ColorProperty`
    """

    border_width = NumericProperty(1)
    """
    `border_width`

    :attr:`border_width` is a :class:`~kivy.properties.NumericProperty`
    """

    active = BooleanProperty(False)
    """
    `active`

    :attr:`active` is a :class:`~kivy.properties.BooleanProperty`
    """

    switch_active_size_ratio = NumericProperty(
        0.75
    )  # Offset for the switch size when active
    """
    `switch_active_size_ratio`

    :attr:`switch_active_size_ratio` is a :class:`~kivy.properties.NumericProperty`
    """

    switch_inactive_size_ratio = NumericProperty(
        0.5
    )  # Offset for the switch size when inactive
    """
    `switch_inactive_size_ratio`

    :attr:`switch_inactive_size_ratio` is a :class:`~kivy.properties.NumericProperty`
    """

    switch_size = NumericProperty()
    """
    `switch_size`

    :attr:`switch_size` is a :class:`~kivy.properties.ListProperty`
    """

    switch_pos = ListProperty([0, 0])
    """
    `switch_pos`

    :attr:`switch_pos` is a :class:`~kivy.properties.ListProperty`
    """

    __events__ = ("on_selected",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update, pos=self.update)
        Clock.schedule_once(self.initialize, 5)

    def initialize(self, dt):
        self.switch_size = self.compute_switch_size()
        self.switch_pos = self.compute_switch_pos()

        if self.active:
            self.switch_color = self.active_switch_color
            self.background_color = self.active_background_color
            self.border_color = self.active_border_color
        else:
            self.switch_color = self.inactive_switch_color
            self.background_color = self.inactive_background_color
            self.border_color = self.inactive_border_color

    def update(self, *args):
        self.switch_size = self.compute_switch_size()
        self.switch_pos = self.compute_switch_pos()

    def compute_switch_size(self, *args, active=None):
        if active is None:
            if self.active:
                ratio = self.switch_active_size_ratio
            else:
                ratio = self.switch_inactive_size_ratio

        else:
            if active:
                ratio = self.switch_active_size_ratio
            else:
                ratio = self.switch_inactive_size_ratio

        return self.height * ratio

    def compute_switch_pos(self, *args, active=None):
        if active is None:
            size = self.switch_size
        else:
            size = self.compute_switch_size(active=active)

        if self.active:
            x = self.x + self.width - size - dp(3)
        else:
            x = self.x + dp(6)
        y = self.center_y - size / 2

        return [x, y]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = not self.active
            self.dispatch("on_selected", self.active, self.field, self.fieldkey)
            return True
        return super().on_touch_down(touch)

    def on_selected(self, *args):
        pass

    def on_active(self, instance, value):
        anim = Animation(
            background_color=self.active_background_color
            if value
            else self.inactive_background_color,
            border_color=self.active_border_color
            if value
            else self.inactive_border_color,
            switch_color=self.active_switch_color
            if value
            else self.inactive_switch_color,
            switch_size=self.compute_switch_size(),
            switch_pos=self.compute_switch_pos(active=value),
            duration=0.2,
            t="out_quad",
        )
        anim.start(self)

    def on_active_background_color(self, instance, value):
        if self.active:
            self.background_color = value

    def on_inactive_background_color(self, instance, value):
        if not self.active:
            self.background_color = value

    def on_active_border_color(self, instance, value):
        if self.active:
            self.border_color = value

    def on_inactive_border_color(self, instance, value):
        if not self.active:
            self.border_color = value

    def on_active_switch_color(self, instance, value):
        if self.active:
            self.switch_color = value

    def on_inactive_switch_color(self, instance, value):
        if not self.active:
            self.switch_color = value

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        default = metadata.get("default", None)
        if default is not None:
            self.active = default

    def on_patch(self, action: Action):
        if action.intent == Action.UPDATE:
            self.active = action.value

    def on_init(self, value: bool):
        self.active = value

