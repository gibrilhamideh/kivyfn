from kivy.properties import VariableListProperty


class FnClipBehavior:
    radius = VariableListProperty([0], length=4)
    """
    Radius of the widget's corners.

    The value should contain four numbers representing the radius
    of each corner in the following order::

        (top_left, top_right, bottom_right, bottom_left)

    These values are used by canvas instructions that support
    rounded rectangles such as ``SmoothRoundedRectangle`` and
    ``SmoothLine``.

    Example::

        FnWidget:
            radius: 12, 12, 12, 12

    :attr:`radius` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``(0, 0, 0, 0)``.
    """


# from kivy.graphics import (
#     StencilPush,
#     StencilUse,
#     StencilUnUse,
#     StencilPop,
# )
# from kivy.graphics.vertex_instructions import RoundedRectangle
# from kivy.properties import VariableListProperty
# from kivy.uix.relativelayout import RelativeLayout
#
#
# class FnClipBehavior:
#     radius = VariableListProperty([0], length=4)
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         # ---- canvas.before ----
#         with self.canvas.before:
#             self._stencil_push = StencilPush()
#
#             self._clip_rect_before = RoundedRectangle()
#
#             self._stencil_use = StencilUse()
#
#         # ---- canvas.after ----
#         with self.canvas.after:
#             self._stencil_unuse = StencilUnUse()
#
#             self._clip_rect_after = RoundedRectangle()
#
#             self._stencil_pop = StencilPop()
#
#         self.bind(
#             pos=self._update_clip,
#             size=self._update_clip,
#             radius=self._update_clip,
#         )
#
#         self._update_clip()
#
#     def _get_clip_pos(self):
#         if isinstance(self, RelativeLayout):
#             return (0, 0)
#         return self.pos
#
#     def _update_clip(self, *args):
#         pos = self._get_clip_pos()
#         size = self.size
#
#         self._clip_rect_before.pos = pos
#         self._clip_rect_before.size = size
#         self._clip_rect_before.radius = self.radius
#
#         self._clip_rect_after.pos = pos
#         self._clip_rect_after.size = size
#         self._clip_rect_after.radius = self.radius
