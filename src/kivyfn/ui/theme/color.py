# kivyfn.ui.theme.color.py
from kivy.event import EventDispatcher
from kivy.properties import ColorProperty, OptionProperty

from kivyfn.ui.theme.types import (
    ThemeDerivedRole,
    ThemePrimeRole,
    ThemeRole,
)
from kivyfn.ui.theme.utils import alpha as _alpha
from kivyfn.ui.theme.utils import blend, overlay
from kivyfn.ui.theme.utils import tone as _tone

PRIME_TO_DERIVED_ROLE: dict[ThemePrimeRole, ThemeDerivedRole] = {
    "primary": "onPrimary",
    "secondary": "onSecondary",
    "surface": "onSurface",
    "background": "onBackground",
    "error": "onError",
    "warning": "onWarning",
    "success": "onSuccess",
}


DERIVED_TO_PRIME_ROLE: dict[ThemeDerivedRole, ThemePrimeRole] = {
    "onPrimary": "primary",
    "onSecondary": "secondary",
    "onSurface": "surface",
    "onBackground": "background",
    "onError": "error",
    "onWarning": "warning",
    "onSuccess": "success",
}


class ThemeColor(EventDispatcher):
    """Shared dark palette with explicit surface and text levels."""

    mode = OptionProperty("dark", options=["dark", "light"])

    # =================================== #
    # section: Actions
    # =================================== #
    primary = ColorProperty("#2cd4cc")
    onPrimary = ColorProperty("#071113")

    secondary = ColorProperty("#6685ff")
    onSecondary = ColorProperty("#071113")

    # =================================== #
    # section: Surfaces and text
    # =================================== #
    background = ColorProperty("#080b10")
    onBackground = ColorProperty("#f4f7fb")

    surface = ColorProperty("#10151d")
    onSurface = ColorProperty("#f4f7fb")
    surfaceRaised = ColorProperty("#171e29")
    surfaceHover = ColorProperty("#202936")
    surfaceActive = ColorProperty("#273343")

    textSecondary = ColorProperty("#b4bfcc")
    textMuted = ColorProperty("#7f8b99")
    textDisabled = ColorProperty("#596472")

    # =================================== #
    # section: Status
    # =================================== #
    error = ColorProperty("#fb7185")
    onError = ColorProperty("#071113")

    warning = ColorProperty("#fbbf24")
    onWarning = ColorProperty("#071113")

    success = ColorProperty("#4ade80")
    onSuccess = ColorProperty("#071113")

    # =================================== #
    # section: Borders and interaction
    # =================================== #
    outline = ColorProperty("#2a3544")
    outlineStrong = ColorProperty("#3a485b")
    divider = ColorProperty("#2a3544")
    shadow = ColorProperty("#000000")
    focus = ColorProperty("#6685ff")
    selection = ColorProperty([44 / 255, 212 / 255, 204 / 255, 0.24])

    # Keep the source opaque for existing alpha("disabled", ...) callers.
    # Use textDisabled directly when an opaque disabled text color is needed.
    disabled = ColorProperty("#f4f7fb")

    def get_role(self, role: ThemeRole):
        return getattr(self, role)

    def get_prime_role(self, role: ThemeDerivedRole):
        key = DERIVED_TO_PRIME_ROLE[role]
        return getattr(self, key)

    def get_derived_role(self, role: ThemePrimeRole) -> list[float]:
        key = PRIME_TO_DERIVED_ROLE[role]
        return getattr(self, key)

    def tone(self, role: ThemeRole, value: int):
        return _tone(self.get_role(role), value)

    def alpha(self, role: ThemeRole, value: float):
        return _alpha(self.get_role(role), value)

    def blend(self, role_a: ThemeRole, role_b: ThemeRole, amount: float):
        return blend(self.get_role(role_a), self.get_role(role_b), amount)

    def overlay(self, role: ThemeRole, overlay_role: ThemeRole):
        return overlay(self.get_role(role), self.get_role(overlay_role))

    def with_tone(self, color, value: int):
        return _tone(color, value)

    def with_alpha(self, color, value: float):
        return _alpha(color, value)

    def with_blend(self, color_a, color_b, amount: float):
        return blend(color_a, color_b, amount)

    def with_overlay(self, color, overlay_color):
        return overlay(color, overlay_color)
