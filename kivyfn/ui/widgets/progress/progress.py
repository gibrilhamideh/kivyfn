import os
from typing import Literal
from functools import partial
from kivy.base import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.properties import (
    NumericProperty,
    OptionProperty,
    ColorProperty,
    VariableListProperty
)

from paths import kivycore_path
with open(
    os.path.join(kivycore_path, "components", "progress", "progress.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class KcProgressBar(BoxLayout):

    type: Literal['determinate', 'indeterminate'] = OptionProperty('determinate', options=['determinate', 'indeterminate'])
        
    '''
    type of the progress bar.
    
    :attr:`type` is an :class:`~kivy.properties.OptionProperty`
    
    '''
    radius: list = VariableListProperty()
    '''
    Radius of the progress bar.

    :attr:`radius` is an :class:`~kivy.properties.VariableListProperty`
    '''

    value: int = NumericProperty(0)
    '''
    Value of the progress bar.
    
    :attr:`value` is an :class:`~kivy.properties.NumericProperty`
    '''
    limit: int = NumericProperty(100)
    '''
    Maximum value of the progress bar.

    :attr:`limit` is an :class:`~kivy.properties.NumericProperty`
    '''

    color: list = ColorProperty([1, 1, 1, 1])
    '''
    Color of the progress bar.

    :attr:`color` is an :class:`~kivy.properties.ColorProperty`
    '''

    bg_color: list = ColorProperty([0, 0, 0, 0.65])
    '''
    Color of the progress bar background.

    :attr:`bg_color` is an :class:`~kivy.properties.ColorProperty`
    '''

    _width: int = NumericProperty(0)

    def do_linear(self, x, x1, y1, x2, y2):
        """
        Linearly link x to y based on two known points (x1, y1) and (x2, y2).

        :param x: The input value
        :param x1: First input value
        :param y1: First output value
        :param x2: Second input value
        :param y2: Second output value
        :return: The corresponding output value y
        """
        # Calculate the slope (rate of change)
        m = (y2 - y1) / (x2 - x1)

        # Calculate y for the given x
        y = m * (x - x1) + y1
        return int(y)

    def on_value(self, instance, value):
        self._width = self.do_linear(value, 0, 0, self.limit, self.width)

    def do_indeterminate(self):

        def start_animation(*args):

            if self.type != 'indeterminate':
                return

            self._width = 0

            anim = Animation(_width=self.width, duration=1, t='in_out_cubic')
            anim.bind(on_complete=partial(fade_out_animation, self))
            anim.start(self)

            Animation(opacity=1, duration=0.5).start(self)

        def fade_out_animation(*args):
            anim = Animation(opacity=0, duration=0.5)
            anim.bind(on_complete=start_animation)
            anim.start(self)

        start_animation()

    def on_type(self, instance, value):

        def next_frame(*args):
            self.value = 0
            if value == 'indeterminate':
                self.do_indeterminate()

        Clock.schedule_once(next_frame, 0.5)
