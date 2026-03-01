
from __future__ import annotations
from typing import Literal
import os
from kivy.base import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ColorProperty, ObjectProperty, OptionProperty

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "appbar", "appbar.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())



class KcAppBarLeftContent(BoxLayout):
    pass

class KcAppBarRightContent(BoxLayout):
    pass

class KcAppBarDivider(BoxLayout):
    pass

class KcAppBar(BoxLayout):
    
    bg_color = ColorProperty([1, 1, 1, 1])
    '''
    `bg_color` is the background color of the app bar

    :attr:`bg_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    anchor: Literal['top', 'bottom'] = OptionProperty('top', options=['top', 'bottom'])
    '''
    `anchor` is the anchor position of the app bar

    :attr:`anchor` is a :class:`~kivy.properties.ObjectProperty`
    '''

    left_content = ObjectProperty(None)
    '''
    `left_content` is the left content of the app bar
    :attr:`left_content` is a :class:`~kivy.properties.ObjectProperty`
    '''

    right_content = ObjectProperty(None)
    '''

    `right_content` is the right content of the app bar
    :attr:`right_content` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def add_widget(self, widget, *args):
        if isinstance(widget, KcAppBarLeftContent):
            self.left_content = widget
            super().add_widget(widget, *args)

        elif isinstance(widget, KcAppBarRightContent):
            self.right_content = widget
            super().add_widget(widget, *args)

        elif isinstance(widget, KcAppBarDivider):
            super().add_widget(widget, *args)
        else:
            Clock.schedule_once(lambda dt: self.delay(widget), -1)

    def delay(self, widget, *args):
        side = getattr(widget, 'side', None)
        if side not in ['left', 'right']:
            raise ValueError("Widget must have a 'side' attribute set to 'left' or 'right'")

        if side == 'left':
            self.left_content.add_widget(widget)
        else:
            self.right_content.add_widget(widget)



