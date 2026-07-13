# kivyfn/ui/behaviors/field/box/box.py
from __future__ import annotations

from typing import Any

from kivy.uix.label import Label as LabelBase
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    ColorProperty,
    ListProperty,
    AliasProperty,
)


class FnFieldLayoutBehavior:
    hint_widget: LabelBase | None = ObjectProperty(None, allownone=True, rebind=True)
    leading_widget: LabelBase | None = ObjectProperty(None, allownone=True, rebind=True)
    trailing_widget: LabelBase | None = ObjectProperty(None, allownone=True, rebind=True)
    message_widget: LabelBase | None = ObjectProperty(None, allownone=True, rebind=True)

    # --- Raw texture sizes
    hint_size = ListProperty([0, 0])
    leading_size = ListProperty([0, 0])
    trailing_size = ListProperty([0, 0])
    message_size = ListProperty([0, 0])

    # --- Render scales
    hint_scale = NumericProperty(1.0)
    leading_scale = NumericProperty(1.0)
    trailing_scale = NumericProperty(1.0)
    message_scale = NumericProperty(1.0)

    # --- Scaled/rendered sizes
    def _get_hint_scaled_size(self) -> tuple[float, float]:
        return (
            self.hint_size[0] * self.hint_scale,
            self.hint_size[1] * self.hint_scale,
        )

    hint_scaled_size = AliasProperty(
        _get_hint_scaled_size,
        None,
        bind=("hint_size", "hint_scale"),
    )

    def _get_leading_scaled_size(self) -> tuple[float, float]:
        return (
            self.leading_size[0] * self.leading_scale,
            self.leading_size[1] * self.leading_scale,
        )

    leading_scaled_size = AliasProperty(
        _get_leading_scaled_size,
        None,
        bind=("leading_size", "leading_scale"),
    )

    def _get_trailing_scaled_size(self) -> tuple[float, float]:
        return (
            self.trailing_size[0] * self.trailing_scale,
            self.trailing_size[1] * self.trailing_scale,
        )

    trailing_scaled_size = AliasProperty(
        _get_trailing_scaled_size,
        None,
        bind=("trailing_size", "trailing_scale"),
    )

    def _get_message_scaled_size(self) -> tuple[float, float]:
        return (
            self.message_size[0] * self.message_scale,
            self.message_size[1] * self.message_scale,
        )

    message_scaled_size = AliasProperty(
        _get_message_scaled_size,
        None,
        bind=("message_size", "message_scale"),
    )

    hint_x = NumericProperty(0)
    hint_y = NumericProperty(0)
    hint_color = ColorProperty([0.5, 0.5, 0.5, 1])

    leading_x = NumericProperty(0)
    leading_y = NumericProperty(0)
    leading_color = ColorProperty([1, 1, 1, 1])

    trailing_x = NumericProperty(0)
    trailing_y = NumericProperty(0)
    trailing_color = ColorProperty([1, 1, 1, 1])

    message_x = NumericProperty(0)
    message_y = NumericProperty(0)
    message_color = ColorProperty([0.5, 0.5, 0.5, 1])

    content_padding = NumericProperty(0)
    leading_padding = NumericProperty(0)
    trailing_padding = NumericProperty(0)

    def __init__(self, **kwargs: Any) -> None:
        self._hint_widget: LabelBase | None = None
        self._leading_widget: LabelBase | None = None
        self._trailing_widget: LabelBase | None = None
        self._message_widget: LabelBase | None = None

        super().__init__(**kwargs)

    def on_hint_widget(self, *_args: Any) -> None:
        self._replace_texture_provider(
            "_hint_widget",
            self.hint_widget,
            self._sync_hint_size,
        )

    def on_leading_widget(self, *_args: Any) -> None:
        self._replace_texture_provider(
            "_leading_widget",
            self.leading_widget,
            self._sync_leading_size,
        )

    def on_trailing_widget(self, *_args: Any) -> None:
        self._replace_texture_provider(
            "_trailing_widget",
            self.trailing_widget,
            self._sync_trailing_size,
        )

    def on_message_widget(self, *_args: Any) -> None:
        self._replace_texture_provider(
            "_message_widget",
            self.message_widget,
            self._sync_message_size,
        )

    def _replace_texture_provider(
        self,
        private_name: str,
        widget: LabelBase | None,
        callback: Any,
    ) -> None:
        old_widget = getattr(self, private_name)

        if old_widget is not None:
            old_widget.unbind(texture_size=callback)

        setattr(self, private_name, widget)

        if widget is None:
            callback()
            return

        widget.bind(texture_size=callback)
        widget.texture_update()
        callback()

    def _sync_hint_size(self, *_args: Any) -> None:
        self.hint_size = (
            [0, 0]
            if self.hint_widget is None
            else list(self.hint_widget.texture_size)
        )

    def _sync_leading_size(self, *_args: Any) -> None:
        self.leading_size = (
            [0, 0]
            if self.leading_widget is None
            else list(self.leading_widget.texture_size)
        )

    def _sync_trailing_size(self, *_args: Any) -> None:
        self.trailing_size = (
            [0, 0]
            if self.trailing_widget is None
            else list(self.trailing_widget.texture_size)
        )

    def _sync_message_size(self, *_args: Any) -> None:
        self.message_size = (
            [0, 0]
            if self.message_widget is None
            else list(self.message_widget.texture_size)
        )
