from __future__ import annotations
import os

from kivy.logger import Logger
from kivy.base import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    NumericProperty,
    VariableListProperty,
    ColorProperty,
    ObjectProperty,
    ReferenceListProperty,
    ListProperty,
    DictProperty,
    BoundedNumericProperty,
    OptionProperty
)

from kivycore.components.effects import RectangularButtonEffect

from resources.icons.md_icons import md_icons
from definitions.icons import icons
from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "button", "button.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class KcButtonIcon(Label):
    icon: str = StringProperty(None, allownone=True)
    '''
    Icon to display before the value.
    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    Default is None.
    '''

    icon_markup: str = StringProperty('')
    '''
    Markup for the icon.
    :attr:`icon_markup` is a :class:`~kivy.properties.StringProperty`
    Default is an empty string.
    ''' 

    def on_icon(self, instance, value):
        if value:
            if value in icons:
                value = md_icons[icons[value]]
            elif value in md_icons:
                value = md_icons[value]
            else:
               value = ''
               Logger.error(f'Icon {value} not found in icons or md_icons.')

            self.icon_markup = f'[font=Icons]{value}[/font]'
        else:
            self.icon_markup = None

class KcButton(RectangularButtonEffect, Label):
    sound_effect: bool = BooleanProperty(True)
    '''
    if the button should play a sound effect when clicked.

    :attr:`sound_effect` is a :class:`~kivy.properties.BooleanProperty`
    '''

    text_color = ColorProperty([0, 0, 0, 1])
    '''
    text color of the widget.

    :attr:`text_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    custom_text_color = ColorProperty(None, allownone=True)
    '''
    custom text color of the widget.

    :attr:`custom_text_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    background_color = ColorProperty([0, 0, 0, 0])
    '''
    background color of the widget.

    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    custom_background_color = ColorProperty(None, allownone=True)
    '''
    custom background color of the widget.

    :attr:`custom_background_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    border_color = ColorProperty([0, 0, 0, 1], allownone=True)
    '''
    border color of the widget.

    :attr:`border_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    border_width = NumericProperty(dp(1))
    '''
    border width of the widget.
    
    :attr:`border_width` is a :class:`~kivy.properties.NumericProperty`
    '''

    custom_width: int | None = NumericProperty(None, allownone=True)
    '''
    Custom width of the widget.

    :attr:`custom_width` is a :class:`~kivy.properties.NumericProperty`
    '''

    custom_height: int | None = NumericProperty(None, allownone=True)
    '''
    Custom height of the widget.

    :attr:`custom_height` is a :class:`~kivy.properties.NumericProperty`
    '''

    focus_color = ColorProperty([0, 0, 0, 1])
    '''
    color of the widget when it is focused.
    :attr:`focus_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    disabled: bool = BooleanProperty(False)
    '''
    if the widget is disabled or not.

    :attr:`disabled` is a :class:`~kivy.properties.BooleanProperty`
    '''

    disabled_text_color = ColorProperty([0.5, 0.5, 0.5, 1])
    '''
    text color of the widget when it is disabled.
    :attr:`disabled_text_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    disabled_background_color = ColorProperty([0.5, 0.5, 0.5, 1])
    '''
    background color of the widget when it is disabled.
    :attr:`disabled_background_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    disabled_border_color = ColorProperty([0.5, 0.5, 0.5, 1])
    '''
    border color of the widget when it is disabled.

    :attr:`disabled_border_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    font_name: str = StringProperty('arial')
    '''
    font name of the widget.

    :attr:`font_name` is a :class:`~kivy.properties.StringProperty`
    '''

    radius = VariableListProperty(dp(4))
    '''
    radius of the widget's corners.
    :attr:`radius` is a :class:`~kivy.properties.NumericProperty`
    '''

    icon_texture: KcButtonIcon = ObjectProperty(None, allownone=True)
    '''
    icon texture of the widget.
    :attr:`icon_texture` is an :class:`~kivy.properties.ObjectProperty`
    '''

    icon: str = StringProperty(None, allownone=True)
    '''
    Icon to display before the value.
    :attr:`icon` is a :class:`~kivy.properties.StringProperty`
    Default is None.
    '''

    icon_color = ColorProperty([0, 0, 0, 1])
    '''
    color of the icon.

    :attr:`icon_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    custom_icon_color = ColorProperty(None, allownone=True)
    '''
    custom color of the icon.

    :attr:`custom_icon_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    icon_size: float = NumericProperty(dp(21))
    '''
    size of the icon.
    :attr:`icon_size` is a :class:`~kivy.properties.NumericProperty`
    '''

    icon_position = OptionProperty('trailing', allownone=True, options=('leading', 'leading_text', 'trailing', 'trailing_text'))
    '''
    Position of the icon relative to the text.

    :attr:`icon_position` is a :class:`~kivy.properties.OptionProperty`
    '''

    icon_pos = ListProperty([0, 0])
    '''
    Position of the icon relative to the button.

    :attr:`icon_pos` is a :class:`~kivy.properties.ListProperty`
    '''

    elevation = BoundedNumericProperty(0, min=0, errorvalue=0)
    """
    Elevation level.

    :attr:`elevation` is a :class:`~kivy.properties.BoundedNumericProperty`
    and defaults to `0`.
    """

    elevation_levels = DictProperty(
        {
            0: 0,
            1: dp(8),
            2: dp(12),
            3: dp(16),
            4: dp(20),
            5: dp(24),
        }
    )
    """
    Elevation levels.

    :attr:`elevation_levels` is a :class:`~kivy.properties.DictProperty`
    and defaults to `{0: 0, 1: dp(8), 2: dp(12), 3: dp(16), 4: dp(20), 5: dp(24)}`.
    """

    shadow_color = ColorProperty([0, 0, 0, 0])
    '''
    color of the shadow.

    :attr:`shadow_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    shadow_softness: float = VariableListProperty(0, length=2)
    '''
    softness of the shadow.

    :attr:`shadow_softness` is a :class:`~kivy.properties.VariableListProperty`
    '''

    shadow_offset: list | float = VariableListProperty([0, 0], length=2)
    '''
    offset of the shadow.

    :attr:`shadow_offset` is a :class:`~kivy.properties.VariableListProperty`
    '''

    angle = NumericProperty(0)
    """
    Angle of rotation of the widget.

    :attr:`angle` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0`.
    """

    background_origin = ListProperty(None)

    _background_x = NumericProperty(0)
    _background_y = NumericProperty(0)
    _background_origin = ReferenceListProperty(_background_x, _background_y)

    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.bind(pos=self.update_background_origin)

    def update_background_origin(self, instance, pos: list) -> None:
        """Fired when the values of :attr:`pos` change."""

        if self.background_origin:
            self._background_origin = self.background_origin
        else:
            self._background_origin = self.center

    def on_icon(self, instance, value):

        def on_icon_loaded(*args):
            self.icon_texture = icon

        icon = KcButtonIcon(icon=value, color=[1, 1, 1, 1])
        Clock.schedule_once(on_icon_loaded, -1)






    

