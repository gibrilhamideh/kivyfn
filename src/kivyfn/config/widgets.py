from __future__ import annotations

from dataclasses import dataclass



@dataclass(slots=True)
class FnWidgetsConfig:
    scroll_distance: int = 10
    """
    Default scroll gesture distance.
    """

    scroll_timeout: int = 250
    """
    Default scroll timeout in milliseconds.
    """

    scroll_moves: int = 5
    """
    Number of movement events required before scrolling starts.
    """

    def apply(self) -> None:

        from kivy.config import Config
        Config.set("widgets", "scroll_distance", str(self.scroll_distance))
        Config.set("widgets", "scroll_timeout", str(self.scroll_timeout))
        Config.set("widgets", "scroll_moves", str(self.scroll_moves))
