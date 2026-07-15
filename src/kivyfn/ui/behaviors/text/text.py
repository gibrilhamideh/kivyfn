from __future__ import annotations
from typing import Any, cast

from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.uix.widget import Widget
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    DictProperty,
    StringProperty,
    NumericProperty,
    ReferenceListProperty
)

from kivyfn.app import FnApp
from kivyfn.fonts import FontManager
from kivyfn.i18n import I18n

from kivyfn.ui.behaviors.layouts.adaptive_size import FnTextureAdaptiveSizeBehavior


class FnTextSizingBehavior:
    """
    Provides the intrinsic, unconstrained size of the text.

    Unlike texture_size, normal_size is measured without applying text_size,
    shortening, clipping, or external layout constraints.
    """

    normal_width = NumericProperty(0)
    normal_height = NumericProperty(0)
    normal_size = ReferenceListProperty(
        normal_width,
        normal_height,
    )

    def __init__(self, **kwargs: Any) -> None:
        self._normal_size_trigger = Clock.create_trigger(
            self._update_normal_size,
            -1,
        )

        super().__init__(**kwargs)  # pyright: ignore

        self.bind( # pyright: ignore
            text=self._queue_normal_size_update,
            font_name=self._queue_normal_size_update,
            font_size=self._queue_normal_size_update,
            bold=self._queue_normal_size_update,
            italic=self._queue_normal_size_update,
            underline=self._queue_normal_size_update,
            strikethrough=self._queue_normal_size_update,
            line_height=self._queue_normal_size_update,
            markup=self._queue_normal_size_update,
        )

    def on_kv_post(self, base_widget) -> None:
        self._queue_normal_size_update()
        super().on_kv_post(base_widget)  # pyright: ignore

    def _queue_normal_size_update(self, *_: Any) -> None:
        self._normal_size_trigger()

    def _update_normal_size(self, *_: Any) -> None:
        label_type = CoreMarkupLabel if self.markup else CoreLabel # pyright: ignore
        label = label_type(
            text=self.text or "",  # pyright: ignore
            font_name=self.font_name, # pyright: ignore
            font_size=self.font_size, # pyright: ignore
            bold=self.bold, # pyright: ignore
            italic=self.italic, # pyright: ignore
            underline=self.underline, # pyright: ignore
            strikethrough=self.strikethrough, # pyright: ignore
            line_height=self.line_height, # pyright: ignore
            halign="left",
            valign="bottom",
            shorten=False,
        )

        label.refresh()

        texture = label.texture

        if texture is None:
            self.normal_size = (0, 0)
            return

        self.normal_size = texture.size


class FnFontTextBehavior:
    use_system_font = BooleanProperty(None, allownone=True)

    def on_kv_post(self, base_widget: Widget) -> None:
        self.set_font_defaults()
        super().on_kv_post(base_widget)  # pyright: ignore

    def set_font_defaults(self) -> None:
        if self.use_system_font is None:
            self.use_system_font = True

    def on_use_system_font(self, _, value: bool | None) -> None:
        if not self.attached: # pyright: ignore
            return

        if value:
            self._bind_font()
        else:
            self._unbind_font()

    def _bind_font(self) -> None:
        if not self.use_system_font:
            return

        fonts = self._get_font_manager()
        fonts.unbind(current=self._apply_font)
        fonts.bind(current=self._apply_font)
        self._apply_font()

    def _unbind_font(self) -> None:
        fonts = self._get_font_manager()
        fonts.unbind(current=self._apply_font)

    def _apply_font(self, *_: Any) -> None:
        fonts = self._get_font_manager()

        self.font_name = fonts.current

    def _get_font_manager(self) -> FontManager:
        app = cast(FnApp, FnApp.get_running_app())
        return app.fn.fonts

    def on_attach(self) -> None:
        self._bind_font()
        super().on_attach()  # pyright: ignore

    def on_detach(self) -> None:
        self._unbind_font()
        super().on_detach()  # pyright: ignore

class FnI18nTextBehavior:
    i18n_key = StringProperty(None, allownone=True)
    i18n_params = DictProperty(None, allownone=True)

    def __init__(self, **kwargs: Any) -> None:
        self._i18n_trigger = Clock.create_trigger(
            self._apply_i18n_text,
            -1,
        )
        super().__init__(**kwargs)  # pyright: ignore

    def on_i18n_key(
        self,
        *_: Any,
    ) -> None:
        self._i18n_trigger()

    def on_i18n_params(
        self,
        *_: Any,
    ) -> None:
        self._i18n_trigger()

    def _bind_i18n(self) -> None:
        i18n = self._get_i18n()

        i18n.unbind(
            lang=self._on_i18n_lang,
        )
        i18n.bind(
            lang=self._on_i18n_lang,
        )

        self._i18n_trigger()

    def _unbind_i18n(self) -> None:
        i18n = self._get_i18n()
        i18n.unbind(
            lang=self._on_i18n_lang,
        )

    def _on_i18n_lang(
        self,
        *_: Any,
    ) -> None:
        self._i18n_trigger()

    def _apply_i18n_text(
        self,
        *_: Any,
    ) -> None:
        if self.i18n_key is None:
            return

        i18n = self._get_i18n()
        self.text = i18n(  # pyright: ignore
            self.i18n_key,
            **(self.i18n_params or {}),
        )

    def _get_i18n(self) -> I18n:
        app = cast(
            FnApp,
            FnApp.get_running_app(),
        )
        return app.fn.i18n

    def on_attach(self) -> None:
        self._bind_i18n()
        super().on_attach()  # pyright: ignore

    def on_detach(self) -> None:
        self._unbind_i18n()
        super().on_detach()  # pyright: ignore

class FnTextColorBehavior:
    text_color = ColorProperty(None, allownone=True)

    def __init__(self, **kwargs: Any) -> None:
        self._fg_parent: Widget | None = None
        super().__init__(**kwargs)  # pyright: ignore

    def on_text_color(self, _, value: list | None) -> None:
        if self.attached: # pyright: ignore
            self._bind_text_color()

    def resolve_fg_parent(self) -> Widget | None:
        parent = self.parent # pyright: ignore

        while parent is not None:
            if getattr(parent, "fg_color", None) is not None:
                return parent

            next_parent = parent.parent
            if next_parent is parent:
                return None

            parent = next_parent

        return None

    def _bind_text_color(self) -> None:

        def delay(*_):
            self._unbind_text_color()

            if self.text_color is not None:
                self._apply_text_color(self.text_color)
                return

            parent = self.resolve_fg_parent()
            if parent is None:
                return

            self._fg_parent = parent
            parent.bind(fg_color=self._on_parent_fg_color)
            self._apply_text_color(parent.fg_color)  # pyright: ignore

        Clock.schedule_once(delay, -1)


    def _unbind_text_color(self) -> None:
        def delay(*_):
            if self._fg_parent is not None:
                self._fg_parent.unbind(fg_color=self._on_parent_fg_color)

            self._fg_parent = None

        Clock.schedule_once(delay, -1)

    def _on_parent_fg_color(self, parent: Widget, color: list) -> None:
        if self.text_color is None:
            self._apply_text_color(color)

    def _apply_text_color(self, color: list) -> None:
        self.color = color  # pyright: ignore

    def on_attach(self) -> None:
        self._bind_text_color()
        super().on_attach()  # pyright: ignore

    def on_detach(self) -> None:
        self._unbind_text_color()
        super().on_detach()  # pyright: ignore



class FnTextBehavior(
    FnTextSizingBehavior,
    FnTextureAdaptiveSizeBehavior,
    FnFontTextBehavior,
    FnTextColorBehavior,
    FnI18nTextBehavior,
):

    pass
