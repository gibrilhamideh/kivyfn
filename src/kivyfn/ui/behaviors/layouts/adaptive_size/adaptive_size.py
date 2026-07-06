from __future__ import annotations
from kivy.properties import BooleanProperty, ReferenceListProperty


class FnLayoutAdaptiveSizeBehavior:
    adaptive_width: bool = BooleanProperty(False)
    adaptive_height: bool = BooleanProperty(False)

    adaptive_size: list[bool] = ReferenceListProperty(adaptive_width, adaptive_height)

    def on_adaptive_width(self, *_):
        if self.adaptive_width:
            self.size_hint_x = None
            self._update_adaptive_width()
            self.bind(minimum_width=self._update_adaptive_width) # pyright: ignore
        else:
            self.unbind(minimum_width=self._update_adaptive_width) # pyright: ignore


    def on_adaptive_height(self, *_):
        if self.adaptive_height:
            self.size_hint_y = None
            self._update_adaptive_height()
            self.bind(minimum_height=self._update_adaptive_height) # pyright: ignore

        else:
            self.unbind(minimum_height=self._update_adaptive_height) # pyright: ignore

    def _update_adaptive_width(self, *_):
        self.width = self.minimum_width # pyright: ignore

    def _update_adaptive_height(self, *_):
        self.height = self.minimum_height # pyright: ignore


class FnTextureAdaptiveSizeBehavior:
    adaptive_width: bool = BooleanProperty(False)
    adaptive_height: bool = BooleanProperty(False)

    adaptive_size: list[bool] = ReferenceListProperty(adaptive_width, adaptive_height)

    def on_adaptive_width(self, *_):
        if self.adaptive_width:
            self.size_hint_x = None
            self._update_adaptive_width()
            self.bind(texture_size=self._update_adaptive_width) # pyright: ignore
        else:
            self.unbind(texture_size=self._update_adaptive_width) # pyright: ignore


    def on_adaptive_height(self, *_):
        if self.adaptive_height:
            self.size_hint_y = None
            self._update_adaptive_height()
            self.bind(texture_size=self._update_adaptive_height) # pyright: ignore

        else:
            self.unbind(texture_size=self._update_adaptive_height) # pyright: ignore

    def _update_adaptive_width(self, *_):
        if self.adaptive_width:
            self.width = self.texture_size[0] # pyright: ignore

    def _update_adaptive_height(self, *_):
        if self.adaptive_height:
            self.height = self.texture_size[1] # pyright: ignore



