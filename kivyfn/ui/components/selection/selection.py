import os
from kivy.logger import Logger
from kivy.base import Builder
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    NumericProperty,
    ColorProperty,
)

from kivycore.store import Action
from kivycore.store.bus import BusMixin
from kivycore.components.effects import RectangularButtonEffect

from resources.icons.md_icons import md_icons

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "selection", "selection.kv"),
    encoding="utf-8",
) as kv_file:
    Builder.load_string(kv_file.read())


class KcSelection(RectangularButtonEffect, Label, BusMixin):
    icon_markup = StringProperty()
    """
    Markup string for the icon.

    :attr:`icon_markup` is a :class:`~kivy.properties.StringProperty`
    """

    active = BooleanProperty(False)
    """
    Indicates whether the selection is currently active.

    :attr:`active` is a :class:`~kivy.properties.BooleanProperty`
    """

    active_color = ColorProperty([1, 0, 0, 1])
    """
    The color to use when the selection is active.

    :attr:`active_color` is a :class:`~kivy.properties.ColorProperty`
    """

    inactive_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    The color to use when the selection is not active.

    :attr:`inactive_color` is a :class:`~kivy.properties.ColorProperty`
    """

    active_icon = StringProperty("checkbox-marked")
    """
    The icon to display when the selection is active.

    :attr:`active_icon` is a :class:`~kivy.properties.StringProperty`
    """

    inactive_icon = StringProperty("checkbox-blank-outline")
    """
    The icon to display when the selection is not active.

    :attr:`inactive_icon` is a :class:`~kivy.properties.StringProperty`
    """

    icon = StringProperty()
    """
    The icon to display in the selection.

    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    """

    icon_size = NumericProperty(dp(24))
    """
    The size of the icon.

    :attr:`icon_size` is a :class:`~kivy.properties.NumericProperty`
    """

    __events__ = ("on_selected",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.icon = self.inactive_icon
        self.color = self.inactive_color
        self.update_size()

    def on_icon(self, instance, value):
        if value:
            if value in md_icons:
                value = md_icons[value]
            else:
                value = ""
                Logger.error(f"Icon '{value}' not found in icons.")

            self.icon_markup = f"[font=Icons]{value}[/font]"
        else:
            self.icon_markup = ""

    def on_icon_size(self, instance, value):
        self.update_size()

    def update_size(self):
        """Update the size of the button based on the icon size."""

        size = self.icon_size * 1.5
        self.size = [size, size]
        self.radius = [size / 2]
        self.font_size = self.icon_size

    def on_release(self):
        """Fired when the button is released."""

        self.active = not self.active
        self.dispatch("on_selected", self.active, self.field, self.fieldkey)

    def on_selected(self, *args):
        pass

    def on_active(self, instance, value):
        anim = Animation(font_size=1, d=0.1, t="out_sine")
        anim.bind(on_complete=self.on_complete)
        anim.start(self)

    def on_complete(self, *args):
        """Fired when the selection is complete."""

        if self.active:
            self.icon = self.active_icon
            color = self.active_color
        else:
            self.icon = self.inactive_icon
            color = self.inactive_color

        Animation(font_size=self.icon_size, color=color, d=0.1, t="in_sine").start(self)

    def on_active_color(self, instance, value):
        """Fired when the active color is changed."""

        if self.active:
            self.color = value

    def on_inactive_color(self, instance, value):
        """Fired when the inactive color is changed."""

        if not self.active:
            self.color = value

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
