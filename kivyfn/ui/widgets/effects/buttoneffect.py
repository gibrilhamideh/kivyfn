'''
Button Behavior
===============

The :class:`~kivy.uix.behaviors.button.ButtonEffect`
`mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
:class:`~kivy.uix.button.Button` behavior. You can combine this class with
other widgets, such as an :class:`~kivy.uix.image.Image`, to provide
alternative buttons that preserve Kivy button behavior.

For an overview of behaviors, please refer to the :mod:`~kivy.uix.behaviors`
documentation.

Example
-------

The following example adds button behavior to an image to make a checkbox that
behaves like a button::

    from kivy.app import App
    from kivy.uix.image import Image
    from kivy.uix.behaviors import ButtonEffect


    class MyButton(ButtonEffect, Image):
        def __init__(self, **kwargs):
            super(MyButton, self).__init__(**kwargs)
            self.source = 'atlas://data/images/defaulttheme/checkbox_off'

        def on_press(self):
            self.source = 'atlas://data/images/defaulttheme/checkbox_on'

        def on_release(self):
            self.source = 'atlas://data/images/defaulttheme/checkbox_off'


    class SampleApp(App):
        def build(self):
            return MyButton()


    SampleApp().run()

See :class:`~kivy.uix.behaviors.ButtonEffect` for details.
'''

__all__ = (
    'ButtonEffect',
    "RectangularButtonEffect",
    "CircularButtonEffect"
)

from typing import NoReturn
from kivy.clock import Clock
from kivy.config import Config
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.graphics import (
    Color,
    Ellipse,
    StencilPop,
    StencilPush,
    StencilUnUse,
    StencilUse,
)

from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
    OptionProperty,
    ObjectProperty
)
from time import time
import os

from paths import resources_path

class ButtonEffect(object):
    '''
    This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides
    :class:`~kivy.uix.button.Button` behavior. Please see the
    :mod:`button behaviors module <kivy.uix.behaviors.button>` documentation
    for more information.

    :Events:
        `on_press`
            Fired when the button is pressed.
        `on_release`
            Fired when the button is released (i.e. the touch/click that
            pressed the button goes away).

    '''

    state = OptionProperty('normal', options=('normal', 'down'))
    '''The state of the button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise its 'normal'.

    :attr:`state` is an :class:`~kivy.properties.OptionProperty` and defaults
    to 'normal'.
    '''

    last_touch = ObjectProperty(None)
    '''Contains the last relevant touch received by the Button. This can
    be used in `on_press` or `on_release` in order to know which touch
    dispatched the event.

    .. versionadded:: 1.8.0

    :attr:`last_touch` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to `None`.
    '''

    min_state_time = NumericProperty(0)
    '''The minimum period of time which the widget must remain in the
    `'down'` state.

    .. versionadded:: 1.9.1

    :attr:`min_state_time` is a float and defaults to 0.035. This value is
    taken from :class:`~kivy.config.Config`.
    '''

    always_release = BooleanProperty(False)
    '''This determines whether or not the widget fires an `on_release` event if
    the touch_up is outside the widget.

    .. versionadded:: 1.9.0

    .. versionchanged:: 1.10.0
        The default value is now False.

    :attr:`always_release` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to `False`.
    '''

    # =================================== #
    #         LONG PRESS EFFECT
    # =================================== #
    long_press_effect = BooleanProperty(False)
    """
    Should I use the long press effect.

    :attr:`long_press_effect` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.

    """

    long_press_delay = NumericProperty(0.5)
    """
    The delay before the long press effect starts.

    :attr:`long_press_delay` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    # =================================== #
    #           REPEAT EFFECT
    # =================================== #
    repeat_effect = BooleanProperty(False)
    """
    Should I use the repeat effect.

    :attr:`repeat_effect` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    start_repeat_delay = NumericProperty(0.5)
    """
    The delay before the repeat effect starts.

    :attr:`start_repeat_delay` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0.5`.
    """

    repeat_interval = NumericProperty(0.15)
    """
    The interval between repeat effects.

    :attr:`repeat_interval` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0.15`.
    """

    # =================================== #
    #           SOUND EFFECT
    # =================================== #
    sound_effect = BooleanProperty(True)
    """
    Should I use the sound effect.

    :attr:`sound_effect` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    sound_obj = SoundLoader.load(
        os.path.join(resources_path, 'sounds', 'button.wav'))
    """
    Sound object.

    :attr:`sound_obj` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    # =================================== #
    #               RIPPLE                #
    # =================================== #
    ripple_rad_default = NumericProperty(1)
    """
    The starting value of the radius of the ripple effect.

    :attr:`ripple_rad_default` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    ripple_color = ColorProperty(None)
    """
    Ripple color in (r, g, b, a) format.

    :attr:`ripple_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    ripple_alpha = NumericProperty(0.5)
    """
    Alpha channel values for ripple effect.

    :attr:`ripple_alpha` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0.5`.
    """

    ripple_scale = NumericProperty(None)
    """
    Ripple effect scale.

    :attr:`ripple_scale` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `None`.
    """

    ripple_duration_in_fast = NumericProperty(0.3)
    """
    Ripple duration when touching to widget.

    :attr:`ripple_duration_in_fast` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0.3`.
    """

    ripple_duration_in_slow = NumericProperty(2)
    """
    Ripple duration when long touching to widget.

    :attr:`ripple_duration_in_slow` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `2`.
    """

    ripple_duration_out = NumericProperty(0.3)
    """
    The duration of the disappearance of the wave effect.

    :attr:`ripple_duration_out` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0.3`.
    """

    ripple_canvas_after = BooleanProperty(True)
    """
    The ripple effect is drawn above/below the content.

    :attr:`ripple_canvas_after` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    ripple_func_in = StringProperty("out_quad")
    """
    Type of animation for ripple in effect.

    :attr:`ripple_func_in` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'out_quad'`.
    """

    ripple_func_out = StringProperty("out_quad")
    """
    Type of animation for ripple out effect.

    :attr:`ripple_func_out` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'ripple_func_out'`.
    """

    ripple_effect = BooleanProperty(True)
    """
    Should I use the ripple effect.

    :attr:`ripple_effect` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    _ripple_rad = NumericProperty()
    _doing_ripple = BooleanProperty(False)
    _finishing_ripple = BooleanProperty(False)
    _fading_out = BooleanProperty(False)
    _round_rad = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self.register_event_type('on_repeat')
        self.register_event_type('on_long_press')
        if 'min_state_time' not in kwargs:
            self.min_state_time = float(Config.get('graphics',
                                                   'min_state_time'))
    
        super(ButtonEffect, self).__init__(**kwargs)
        self.__state_event = None
        self.__touch_time = None
        self.fbind('state', self.cancel_event)

        self._repeat_trigger = Clock.create_trigger(self._do_repeat, 0.15)
        self._start_repeat_trigger = Clock.create_trigger(self._do_repeat, 0.5)

        self._long_press_trigger = Clock.create_trigger(self._do_long_press, self.long_press_delay)

    # =================================== #
    #           BUTTON BEHAVIOR
    # =================================== #
    def _do_press(self):
        self.state = 'down'

    def _do_release(self, *args):
        self.state = 'normal'

    def cancel_event(self, *args):
        if self.__state_event:
            self.__state_event.cancel()
            self.__state_event = None

    def trigger_action(self, duration=0.1):
        '''Trigger whatever action(s) have been bound to the button by calling
        both the on_press and on_release callbacks.

        This is similar to a quick button press without using any touch events,
        but note that like most kivy code, this is not guaranteed to be safe to
        call from external threads. If needed use
        :class:`Clock <kivy.clock.Clock>` to safely schedule this function and
        the resulting callbacks to be called from the main thread.

        Duration is the length of the press in seconds. Pass 0 if you want
        the action to happen instantly.

        .. versionadded:: 1.8.0
        '''
        self._do_press()
        self.dispatch('on_press')

        def trigger_release(dt):
            self._do_release()
            self.dispatch('on_release')
        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(trigger_release, duration)

    # =================================== #
    #         LONG PRESS EFFECT
    # =================================== #
    def _do_long_press(self, *args):
        self.dispatch('on_long_press')

    def _stop_long_press(self, *args):
        self._long_press_trigger.cancel()

    # =================================== #
    #           REPEAT EFFECT
    # =================================== #
    def _do_repeat(self, *args):
        self.dispatch('on_repeat')
        
        self._repeat_trigger()

        if self.sound_effect:
            self._do_sound()
        
    def _stop_repeat(self, *args):
        self._repeat_trigger.cancel()
        self._start_repeat_trigger.cancel()

    # =================================== #
    #           RIPPLE BEHAVIOR
    # =================================== #
    def lay_canvas_instructions(self) -> NoReturn:
        raise NotImplementedError

    def start_ripple(self) -> None:
        if not self._doing_ripple:
            self._doing_ripple = True
            anim = Animation(
                _ripple_rad=self.finish_rad,
                t="linear",
                duration=self.ripple_duration_in_slow,
            )
            anim.bind(on_complete=self.fade_out)
            anim.start(self)

    def finish_ripple(self) -> None:
        if self._doing_ripple and not self._finishing_ripple:
            self._finishing_ripple = True
            self._doing_ripple = False
            Animation.cancel_all(self, "_ripple_rad")
            anim = Animation(
                _ripple_rad=self.finish_rad,
                t=self.ripple_func_in,
                duration=self.ripple_duration_in_fast,
            )
            anim.bind(on_complete=self.fade_out)
            anim.start(self)

    def fade_out(self, *args) -> None:
        rc = self.ripple_color
        if not self._fading_out:
            self._fading_out = True
            Animation.cancel_all(self, "ripple_color")
            anim = Animation(
                ripple_color=[rc[0], rc[1], rc[2], 0.0],
                t=self.ripple_func_out,
                duration=self.ripple_duration_out,
            )
            anim.bind(on_complete=self.anim_complete)
            anim.start(self)

    def anim_complete(self, *args) -> None:
        """Fired when the "fade_out" animation complete."""

        self._doing_ripple = False
        self._finishing_ripple = False
        self._fading_out = False

        if not self.ripple_canvas_after:
            canvas = self.canvas.before
        else:
            canvas = self.canvas.after

        canvas.remove_group("circular_ripple_behavior")
        canvas.remove_group("rectangular_ripple_behavior")

    def call_ripple_animation_methods(self, touch) -> None:
        if self._doing_ripple:
            Animation.cancel_all(
                self, "_ripple_rad", "ripple_color", "rect_color"
            )
            self.anim_complete()
        self._ripple_rad = self.ripple_rad_default
        self.ripple_pos = (touch.x, touch.y)

        if self.ripple_color:
            pass
        elif hasattr(self, "theme_cls"):
            self.ripple_color = self.theme_cls.rippleColor
        else:
            # If no theme, set Gray 300.
            self.ripple_color = [
                0.8784313725490196,
                0.8784313725490196,
                0.8784313725490196,
                self.ripple_alpha,
            ]
        self.ripple_color[3] = self.ripple_alpha
        self.lay_canvas_instructions()
        self.finish_rad = max(self.width, self.height) * self.ripple_scale
        self.start_ripple()

    def _set_ellipse(self, instance, value):
        self.ellipse.size = (self._ripple_rad, self._ripple_rad)

    def _set_color(self, instance, value):
        self.col_instruction.a = value[3]


    # =================================== #
    #            SOUND EFFECT
    # =================================== #
    def _do_sound(self):
        if not self.sound_effect:
            return

        self.sound_obj.play()

    # =================================== #
    #           TOUCH EVENTS
    # =================================== #
    def on_touch_down(self, touch):
        if super(ButtonEffect, self).on_touch_down(touch):
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self.__touch_time = time()
        self._do_press()
        self.dispatch('on_press')

        # RIPPLE ANIMATION
        self.call_ripple_animation_methods(touch)

        # REPEAT EFFECT
        if self.repeat_effect:
            self._start_repeat_trigger()

        # LONG PRESS EFFECT
        if self.long_press_effect:
            self._long_press_trigger()

        return True

    def on_touch_move(self, touch):

        # ============================ #
        #        RIPPLE EFFECT
        # ============================ #
        if not self.collide_point(touch.x, touch.y):
            if not self._finishing_ripple and self._doing_ripple:
                self.finish_ripple()

            self._stop_repeat()
            self._stop_long_press()

        # ============================ #
        #        BUTTON EFFECT
        # ============================ #
        if touch.grab_current is self:
            return True
        if super(ButtonEffect, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):

        # ============================ #
        #        RIPPLE EFFECT
        # ============================ #
        if self.collide_point(touch.x, touch.y) and self._doing_ripple:
            self.finish_ripple()

        # ============================ #
        #        BUTTON EFFECT
        # ============================ #
        if touch.grab_current is not self:
            return super(ButtonEffect, self).on_touch_up(touch)
        assert self in touch.ud
        touch.ungrab(self)
        self.last_touch = touch

        if (not self.always_release and
                not self.collide_point(*touch.pos)):
            self._do_release()
            return

        touchtime = time() - self.__touch_time
        if touchtime < self.min_state_time:
            self.__state_event = Clock.schedule_once(
                self._do_release, self.min_state_time - touchtime)
        else:
            self._do_release()

        
        self._do_sound()
        self._stop_repeat()
        self._stop_long_press()
        self.dispatch('on_release')
        return True

    # =================================== #
    #              EVENTS
    # =================================== #
    def on_press(self):
        pass

    def on_release(self):
        pass

    def on_repeat(self):
        pass

    def on_long_press(self):
        pass

class RectangularButtonEffect(ButtonEffect):
    """
    Class implements a rectangular ripple effect.

    For more information, see in the :class:`~kivymd.uix.behavior.CommonRipple`
    class documentation.
    """

    ripple_scale = NumericProperty(2.75)
    """
    See :class:`~CommonRipple.ripple_scale`.

    :attr:`ripple_scale` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `2.75`.
    """

    def lay_canvas_instructions(self) -> None:
        """
        Adds graphic instructions to the canvas to implement ripple animation.
        """

        if not self.ripple_effect:
            return

        with self.canvas.after if self.ripple_canvas_after else self.canvas.before:
            if hasattr(self, "radius"):
                if isinstance(self.radius, (float, int)):
                    self.radius = [
                        self.radius,
                    ]
                self._round_rad = self.radius
            StencilPush(group="rectangular_ripple_behavior")
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self._round_rad,
                group="rectangular_ripple_behavior",
            )
            StencilUse(group="rectangular_ripple_behavior")
            self.col_instruction = Color(
                rgba=self.ripple_color, group="rectangular_ripple_behavior"
            )
            self.ellipse = Ellipse(
                size=(self._ripple_rad, self._ripple_rad),
                pos=(
                    self.ripple_pos[0] - self._ripple_rad / 2.0,
                    self.ripple_pos[1] - self._ripple_rad / 2.0,
                ),
                group="rectangular_ripple_behavior",
            )
            StencilUnUse(group="rectangular_ripple_behavior")
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self._round_rad,
                group="rectangular_ripple_behavior",
            )
            StencilPop(group="rectangular_ripple_behavior")
        self.bind(ripple_color=self._set_color, _ripple_rad=self._set_ellipse)

    def _set_ellipse(self, instance, value):
        super()._set_ellipse(instance, value)
        self.ellipse.pos = (
            self.ripple_pos[0] - self._ripple_rad / 2.0,
            self.ripple_pos[1] - self._ripple_rad / 2.0,
        )

class CircularButtonEffect(ButtonEffect):
    """
    Class implements a circular ripple effect.

    For more information, see in the :class:`~kivymd.uix.behavior.CommonRipple`
    class documentation.
    """

    ripple_scale = NumericProperty(1)
    """
    See :class:`~CommonRipple.ripple_scale`.

    :attr:`ripple_scale` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    def lay_canvas_instructions(self) -> None:
        if not self.ripple_effect:
            return

        with self.canvas.after if self.ripple_canvas_after else self.canvas.before:
            StencilPush(group="circular_ripple_behavior")
            self.stencil = Ellipse(
                size=(
                    self.width * self.ripple_scale,
                    self.height * self.ripple_scale,
                ),
                pos=(
                    self.center_x - (self.width * self.ripple_scale) / 2,
                    self.center_y - (self.height * self.ripple_scale) / 2,
                ),
                group="circular_ripple_behavior",
            )
            StencilUse(group="circular_ripple_behavior")
            self.col_instruction = Color(rgba=self.ripple_color)
            self.ellipse = Ellipse(
                size=(self._ripple_rad, self._ripple_rad),
                pos=(
                    self.center_x - self._ripple_rad / 2.0,
                    self.center_y - self._ripple_rad / 2.0,
                ),
                group="circular_ripple_behavior",
            )
            StencilUnUse(group="circular_ripple_behavior")
            Ellipse(
                pos=self.pos, size=self.size, group="circular_ripple_behavior"
            )
            StencilPop(group="circular_ripple_behavior")
            self.bind(
                ripple_color=self._set_color, _ripple_rad=self._set_ellipse
            )

    def _set_ellipse(self, instance, value):
        super()._set_ellipse(instance, value)
        if self.ellipse.size[0] > self.width * 0.6 and not self._fading_out:
            self.fade_out()
        self.ellipse.pos = (
            self.center_x - self._ripple_rad / 2.0,
            self.center_y - self._ripple_rad / 2.0,
        )
