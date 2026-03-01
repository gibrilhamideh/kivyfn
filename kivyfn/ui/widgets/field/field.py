from __future__ import annotations

from typing import TYPE_CHECKING, Type, Callable

import os
import re

if TYPE_CHECKING:
    from main import MainApp
    from theme.components.timedialog import TimeDialog

from kivy.logger import Logger
from kivy.base import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    OptionProperty,
    ObjectProperty,
    ColorProperty,
    VariableListProperty,
    DictProperty,
    ListProperty,
)

from kivycore.store import Action
from kivycore.store.bus import BusMixin

from resources.icons.md_icons import md_icons
from definitions.icons import icons
from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "field", "field.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

# NOTE ip address filter
# r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'


class FieldIcon(Label):
    icon: str = StringProperty(None, allownone=True)
    """
    Icon to display before the value.
    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    Default is None.
    """

    icon_markup: str = StringProperty("")
    """
    Markup for the icon.
    :attr:`icon_markup` is a :class:`~kivy.properties.StringProperty`
    Default is an empty string.
    """

    def on_icon(self, instance, value):
        if value:
            if value in icons:
                value = md_icons[icons[value]]
            elif value in md_icons:
                value = md_icons[value]
            else:
                value = ""
                Logger.error(f"Icon {value} not found in icons or md_icons.")

            self.icon_markup = f"[font=Icons]{value}[/font]"
        else:
            self.icon_markup = None


class CoreField(BusMixin):
    text_color = ColorProperty([0, 0, 0, 1])
    """
    text color of the widget.

    :attr:`text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    custom_text_color = ColorProperty(None, allownone=True)
    """
    custom text color of the widget.

    :attr:`custom_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    background_color = ColorProperty([0, 0, 0, 0])
    """
    background color of the widget.

    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    border_color = ColorProperty([0, 0, 0, 1], allownone=True)
    """
    border color of the widget.

    :attr:`border_color` is a :class:`~kivy.properties.ColorProperty`
    """

    border_width = NumericProperty(dp(1))
    """
    border width of the widget.
    
    :attr:`border_width` is a :class:`~kivy.properties.NumericProperty`
    """

    focus_color = ColorProperty([0, 0, 0, 1])
    """
    color of the widget when it is focused.
    :attr:`focus_color` is a :class:`~kivy.properties.ColorProperty`
    """

    disabled: bool = BooleanProperty(False)
    """
    if the widget is disabled or not.

    :attr:`disabled` is a :class:`~kivy.properties.BooleanProperty`
    """

    disabled_text_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    text color of the widget when it is disabled.
    :attr:`disabled_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    disabled_background_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    background color of the widget when it is disabled.
    :attr:`disabled_background_color` is a :class:`~kivy.properties.ColorProperty`
    """

    disabled_border_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    border color of the widget when it is disabled.

    :attr:`disabled_border_color` is a :class:`~kivy.properties.ColorProperty`
    """

    font_name: str = StringProperty("arial")
    """
    font name of the widget.

    :attr:`font_name` is a :class:`~kivy.properties.StringProperty`
    """

    radius = VariableListProperty(dp(4))
    """
    radius of the widget's corners.
    :attr:`radius` is a :class:`~kivy.properties.NumericProperty`
    """

    custom_width: int = NumericProperty(None, allownone=True)
    """
    custom width of the widget.

    :attr:`custom_width` is a :class:`~kivy.properties.NumericProperty`
    """

    custom_height: int = NumericProperty(None, allownone=True)
    """
    custom height of the widget.

    :attr:`custom_height` is a :class:`~kivy.properties.NumericProperty`
    """

    icon_texture: FieldIcon = ObjectProperty(None, allownone=True)
    """
    icon texture of the widget.
    :attr:`icon_texture` is an :class:`~kivy.properties.ObjectProperty`
    """

    icon: str = StringProperty(None, allownone=True)
    """
    Icon to display before the value.
    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    Default is None.
    """

    icon_color = ColorProperty([0, 0, 0, 1])
    """
    color of the icon.

    :attr:`icon_color` is a :class:`~kivy.properties.ColorProperty`
    """

    custom_icon_color = ColorProperty(None, allownone=True)
    """
    custom color of the icon.

    :attr:`custom_icon_color` is a :class:`~kivy.properties.ColorProperty`
    """

    icon_disabled_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    color of the icon when the widget is disabled.

    :attr:`icon_disabled_color` is a :class:`~kivy.properties.ColorProperty`
    """

    icon_font_size: float = NumericProperty(dp(14))
    """
    font size of the icon.

    :attr:`icon_font_size` is a :class:`~kivy.properties.NumericProperty`
    """

    icon_size: float = VariableListProperty([dp(16), dp(16)], length=2)
    """
    size of the icon.
    :attr:`icon_size` is a :class:`~kivy.properties.VariableListProperty`
    """

    trailing_text_texture: Label = ObjectProperty(None, allownone=True)
    """
    Texture for the trailing text.

    :attr:`trailing_text_texture` is an :class:`~kivy.properties.ObjectProperty`
    """

    trailing_text: str = StringProperty("")
    """
    Text to display after the value.

    :attr:`trailing_text` is a :class:`~kivy.properties.StringProperty`
    """

    trailing_text_color = ColorProperty([0, 0, 0, 1])
    """
    Color of the trailing text.

    :attr:`trailing_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    custom_trailing_text_color = ColorProperty(None, allownone=True)
    """
    Custom color of the trailing text.

    :attr:`custom_trailing_text_color` is a :class:`~kivy.properties.ColorProperty`
    """

    trailing_text_disabled_color = ColorProperty([0.5, 0.5, 0.5, 1])
    """
    Color of the trailing text when the widget is disabled.

    :attr:`trailing_text_disabled_color` is a :class:`~kivy.properties.ColorProperty`
    """

    trailing_text_font_size: float = NumericProperty(dp(14))
    """
    Font size of the trailing text.

    :attr:`trailing_text_font_size` is a :class:`~kivy.properties.NumericProperty`
    """

    trailing_text_size: float = VariableListProperty([dp(16), dp(16)], length=2)
    """
    Size of the trailing text.

    :attr:`trailing_text_size` is a :class:`~kivy.properties.NumericProperty`
    """

    allow_stretch = BooleanProperty(True)
    """
    allow_stretch, used for table

    :attr:`allow_stretch` is a :class:`~kivy.properties.BooleanProperty`
    """

    def on_icon(self, instance, value):
        icon = FieldIcon(icon=value, color=[1, 1, 1, 1], font_size=self.icon_font_size)
        icon.texture_update()
        self.icon_size = icon.texture_size
        self.icon_texture = icon

    def on_trailing_text(self, instance, value):
        text = Label(
            text=value, color=[1, 1, 1, 1], font_size=self.trailing_text_font_size
        )
        text.texture_update()
        self.trailing_text_size = text.texture_size
        self.trailing_text_texture = text


# ================================ #
#          box fields
# ================================ #
class KcTextField(TextInput, CoreField):
    __events__ = ("on_validated", "on_beforeinput", "on_afterinput")

    cache: str = StringProperty()
    """
    cached text before focus is lost.

    :attr:`cache` is a :class:`~kivy.properties.StringProperty`
    """

    validator: Callable = ObjectProperty(None, allownone=True)
    """
    function to validate the input.

    :attr:`validator` is a :class:`~kivy.properties.ObjectProperty`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_type = "text"

    def insert_text(self, substring, from_undo=False):
        result = self.beforeinput(substring, from_undo)
        if result is False:
            return

        self.dispatch("on_beforeinput", substring)
        super().insert_text(substring, from_undo)
        self.dispatch("on_afterinput", substring)

    def beforeinput(self, substring, from_undo=False):
        pass

    # -------------------------
    # Events
    # -------------------------
    def on_focus(self, instance, focus):
        if focus:
            self.cache = self.text

        else:
            if self.text != self.cache:
                if callable(self.validator):
                    if self.validator(self.text) is False:
                        self.text = self.cache
                        return

                name = getattr(self, "field", None)
                key = getattr(self, "fieldkey", None)
                self.dispatch("on_validated", self.text, name, key)

    def on_beforeinput(self, *args):
        pass

    def on_afterinput(self, *args):
        pass

    def on_validated(self, *args):
        pass

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        self.validator = metadata.get("validator", None)

    def on_patch(self, action: Action):
        if action.intent == Action.UPDATE:
            if callable(self.validator):
                if self.validator(action.value) is False:
                    return

            if action.value is None:
                return

            self.text = str(action.value)

    def on_init(self, value: str):
        self.text = str(value)


class KcNumericField(TextInput, CoreField):
    cache: str = StringProperty()
    """
    cached text before focus is lost.

    :attr:`cache` is a :class:`~kivy.properties.StringProperty`
    """

    le: float | None = NumericProperty(100, allownone=True)
    """
    max value of the field

    :attr:`le` is a :class:`~kivy.properties.NumericProperty`
    """

    ge: float | None = NumericProperty(0, allownone=True)
    """
    min value of the field

    :attr:`ge` is a :class:`~kivy.properties.NumericProperty`
    """

    digit: int = NumericProperty(3)
    """
    maximum number of digits allowed in the field.
    :attr:`digit` is a :class:`~kivy.properties.NumericProperty`
    """

    decimal: int = NumericProperty(1)
    """
    maximum number of decimal places allowed in the field.

    :attr:`decimal` is a :class:`~kivy.properties.NumericProperty`
    """

    allow_negative: bool = BooleanProperty(False)
    """
    if negative numbers are allowed in the field.

    :attr:`allow_negative` is a :class:`~kivy.properties.BooleanProperty`
    """

    app: Type[MainApp] = ObjectProperty()
    """
    app instance.

    :attr:`app` is an :class:`~kivy.properties.ObjectProperty`
    """

    filter_cls: Type[float] | Type[int] = ObjectProperty(float)
    """
    class of the field.

    :attr:`cls` is a :class:`~kivy.properties.ObjectProperty`
    """

    _INT_POS_PAT = re.compile(r"^[0-9]*$")
    _INT_NEG_PAT = re.compile(r"^-?[0-9]*$")
    _FLT_POS_PAT = re.compile(r"^[0-9]*\.?[0-9]*$")
    _FLT_NEG_PAT = re.compile(r"^-?[0-9]*\.?[0-9]*$")

    __events__ = ("on_validated",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = str(self.ge)
        self.input_type = "number"
        self.input_filter = self.pre_filter

    def _pick_pat(self):
        if self.filter_cls is int:
            return self._INT_NEG_PAT if self.allow_negative else self._INT_POS_PAT
        if self.filter_cls is float:
            return self._FLT_NEG_PAT if self.allow_negative else self._FLT_POS_PAT

        raise ValueError("Invalid filter class")

    def _is_in_bound(self, number) -> bool:
        if self.ge is not None and number < self.ge:
            return False
        if self.le is not None and number > self.le:
            return False

        return True

    def pre_filter(self, substring: str, from_undo=False):
        # Build candidate text as Kivy will insert it
        col, row = self.cursor
        text = self._lines[row]
        new_text: str = text[:col] + substring + text[col:]

        # 1) Let regex decide validity (covers all char/dot/minus rules)
        pat = self._pick_pat()
        if not pat.match(new_text):
            return False

        # 2) Only enforce length limits
        _striped = new_text.lstrip("-")
        if self.filter_cls is int:
            # only whole digits
            if len(_striped) > self.digit:
                return False
        else:  # float
            whole, sep, frac = _striped.partition(".")
            if sep:  # dot was found
                if len(whole) > self.digit or len(frac) > self.decimal:
                    return False
            else:
                if len(whole) > self.digit:
                    return False
        # Accept
        return substring

    def on_focus(self, instance, focus):
        if focus:
            self.cache = self.text
            self.text = ""

        else:
            if not self.text == self.cache:
                name = getattr(self, "field", None)
                key = getattr(self, "fieldkey", None)

                try:
                    text = self.filter_cls(self.text)
                    if not self._is_in_bound(text):
                        raise ValueError("Out of bound")

                    if self.filter_cls is float:
                        self.text = f"{text:.{self.decimal}f}"
                    else:
                        self.text = str(text)

                    self.dispatch("on_validated", text, name, key)

                except ValueError:
                    self.text = self.cache

    def on_le(self, instance, value):
        if self.le is None:
            return

        whole, sep, frac = str(value).lstrip("-").partition(".")
        if sep:  # has a decimal point
            self.digit = max(self.digit, len(whole))
            self.decimal = max(self.decimal, len(frac))
        else:
            self.digit = max(self.digit, len(whole))

    def on_ge(self, instance, value):
        if self.ge is None:
            self.allow_negative = True
            return

        whole, sep, frac = str(value).lstrip("-").partition(".")
        if sep:
            self.digit = max(self.digit, len(whole))
            self.decimal = max(self.decimal, len(frac))
        else:
            self.digit = max(self.digit, len(whole))

        self.allow_negative = self.ge < 0

    def on_validated(self, *args):
        pass

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        self.ge = metadata.get("ge")
        self.le = metadata.get("le")
        self.filter_cls = metadata.get("cls", float)

        default = metadata.get("default", self.ge)
        if isinstance(default, (int, float)):
            self.text = str(default)

    def on_patch(self, action: Action):
        if action.intent == Action.UPDATE:
            if action.value is None:
                return

            try:
                self.text = str(self.filter_cls(action.value))
            except ValueError:
                pass

    def on_init(self, value: dict):
        self.text = str(value)


class KcTimeField(Label, CoreField):
    focus: bool = BooleanProperty(False)
    """
    if widget is focused or not. 

    :attr:`focus` is an :class:`~kivy.properties.BooleanProperty`
    """

    time_format: str = OptionProperty("minute", options=["second", "minute", "hour"])
    """
    time format of the widget.
    
    :attr:`time_format` is an :class:`~kivy.properties.OptionProperty`
    """

    min_value: str = StringProperty(None, allowNone=True)
    """
    minimum time that can be selected.

    :attr:`min_value` is an :class:`~kivy.properties.StringProperty`
    """

    max_value: str = StringProperty(None, allowNone=True)
    """
    maximum time that can be selected.

    :attr:`max_value` is an :class:`~kivy.properties.StringProperty`
    """

    le: str = StringProperty(None, allowNone=True)
    """
    less than or equal to value of the field.

    :attr:`le` is an :class:`~kivy.properties.StringProperty`
    """

    ge: str = StringProperty(None, allowNone=True)
    """
    greater than or equal to value of the field.

    :attr:`ge` is an :class:`~kivy.properties.StringProperty`
    """

    time_cls: Type[TimeDialog] = ObjectProperty()
    """
    time dialog class.P

    :attr:`time_cls` is an :class:`~kivy.properties.ObjectProperty`
    """

    app: Type[MainApp] = ObjectProperty()
    """
    app instance.

    :attr:`app` is an :class:`~kivy.properties.ObjectProperty`
    """

    __events__ = ("on_validated",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "00:00:00"

    def on_app(self, *args):
        self.time_cls = self.app.ui.time_dialog

    def on_focus(self, instance, focus):
        if focus:
            self.time_cls.show(self)

    def on_validated(self, *args):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            self.focus = True
            return True

        return False

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        self.text = str(metadata.get("default", "00:00:00"))
        self.ge = metadata.get("ge")
        self.le = metadata.get("le")

    def on_patch(self, action: Action):
        if action.intent == Action.UPDATE:
            if action.value is None:
                return

            self.text = str(action.value)

    def on_init(self, value: dict):
        self.text = str(value)


class KcSelectionField(Label, CoreField):
    app: Type[MainApp] = ObjectProperty()
    """
    app instance.

    :attr:`app` is an :class:`~kivy.properties.ObjectProperty`
    """

    focus: bool = BooleanProperty(False)
    """
    if widget is focused or not.
    
    :attr:`focus` is an :class:`~kivy.properties.BooleanProperty`
    """

    text_key: str = StringProperty()
    """
    text key to be translated.

    :attr:`text_key` is an :class:`~kivy.properties.StringProperty`
    """

    use_meta = BooleanProperty(False)
    """
    if the field should use internal options.

    :attr:`use_meta` is a :class:`~kivy.properties.BooleanProperty`
    """

    mapping = DictProperty()
    """
    mapping of options to their display values.

    :attr:`mapping` is a :class:`~kivy.properties.DictProperty`
    """

    options: list = ListProperty()
    """
    options for the selection field.

    :attr:`options` is a :class:`~kivy.properties.ListProperty`
    """

    __events__ = ("on_open_menu", "on_focus")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Window.bind(on_touch_down=self.window_touch_event)

    def window_touch_event(self, instance, touch):
        if not self.collide_point(*touch.pos):
            self.focus = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            self.focus = True
            return True
        return False

    def on_open_menu(self, *args):
        pass

    def on_focus(self, *args):
        if self.focus:
            if self.use_meta:
                pass
            else:
                self.dispatch("on_open_menu", self.field, self.fieldkey)

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        options = metadata.get("options", None)
        if options:
            self.options = options

    def on_patch(self, action: Action):
        if action.intent == Action.UPDATE:
            if action.value is None:
                return

            if self.mapping:
                if action.value in self.mapping:
                    self.text_key = str(self.mapping[action.value])
                else:
                    self.text_key = str(action.value)
            else:
                self.text_key = str(action.value)

    def on_init(self, value: dict):
        if self.mapping:
            if value in self.mapping:
                self.text_key = str(self.mapping[value])
            else:
                self.text_key = str(value)
        else:
            self.text_key = str(value)


class KcChannelField(Label, CoreField):
    app: Type[MainApp] = ObjectProperty()
    """
    app instance.

    :attr:`app` is an :class:`~kivy.properties.ObjectProperty`
    """

    focus: bool = BooleanProperty(False)
    """
    if widget is focused or not.
    
    :attr:`focus` is an :class:`~kivy.properties.BooleanProperty`
    """

    selected: dict = DictProperty()
    """
    selected itmes.
    
    :attr:`selected` is a :class:`~kivy.properties.DictProperty`"""

    channel: str = StringProperty(None, allownone=True)
    """
    channel type for the field.

    :attr:`channel` is a :class:`~kivy.properties.StringProperty`
    """

    __events__ = ("on_open_menu", "on_validated", "on_focus")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Window.bind(on_touch_down=self.window_touch_event)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            self.focus = True
            return True
        return False

    def window_touch_event(self, instance, touch):
        if not self.collide_point(*touch.pos):
            self.focus = False

    def on_focus(self, instance, focus):
        if focus:
            if self.channel is None:
                return

            self.app.ui.channel_dialog.open(self)

    def on_open_menu(self, *args):
        pass

    def on_validated(self, *args):
        pass

    def on_dialog_update(self, index, selected: bool, value: int):
        # if selected:
        #     self.selected[index] = value
        # else:
        #     self.selected.pop(index, None)

        self.dispatch(
            "on_validated", (index, selected, value), self.field, self.fieldkey
        )

    # -------------------------
    # Bus Mixin
    # -------------------------
    def on_metadata(self, instance, metadata: dict):
        channel = metadata.get("channel", None)
        if channel:
            self.channel = channel

    def on_patch(self, action: Action):
        if action.intent in [Action.UPDATE, Action.CREATE]:
            if action.value is None:
                return

            key = action.path.leaf
            self.selected[key] = action.value

        else:
            self.selected.pop(action.path.leaf, None)

    def on_init(self, value: dict):
        self.selected = dict(value)
