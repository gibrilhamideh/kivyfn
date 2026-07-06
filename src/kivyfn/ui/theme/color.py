# kivyfn.ui.theme.color.py
from kivy.event import EventDispatcher
from kivy.properties import ColorProperty, OptionProperty

from kivyfn.ui.theme.utils import (
    tone as _tone,
    alpha as _alpha,
    blend,
    overlay
)

from kivyfn.ui.theme.types import (
        ThemeRole,
        ThemePrimeRole,
        ThemeDerivedRole,
)

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
    mode = OptionProperty("dark", options=["dark", "light"])

    primary = ColorProperty([0.48, 0.63, 1.00, 1])      # blue
    onPrimary = ColorProperty([0.05, 0.07, 0.12, 1])

    secondary = ColorProperty([0.73, 0.60, 1.00, 1])    # purple
    onSecondary = ColorProperty([0.05, 0.07, 0.12, 1])

    surface = ColorProperty([0.09, 0.11, 0.18, 1])      # #161b2d
    onSurface = ColorProperty([0.75, 0.80, 0.93, 1])    # soft text

    background = ColorProperty([0.04, 0.06, 0.12, 1])   # #0b1020
    onBackground = ColorProperty([0.75, 0.80, 0.93, 1])

    error = ColorProperty([1.00, 0.46, 0.56, 1])        # red
    onError = ColorProperty([0.05, 0.07, 0.12, 1])

    warning = ColorProperty([0.88, 0.73, 0.46, 1])      # yellow/orange
    onWarning = ColorProperty([0.05, 0.07, 0.12, 1])

    success = ColorProperty([0.62, 0.82, 0.42, 1])      # green
    onSuccess = ColorProperty([0.05, 0.07, 0.12, 1])

    outline = ColorProperty([0.30, 0.35, 0.50, 1])
    divider = ColorProperty([0.55, 0.60, 0.65, 0.25])
    shadow = ColorProperty([1, 1, 1, 1])
    disabled = ColorProperty([0.75, 0.80, 0.93, 1])

    def get_role(self, role: ThemeRole):
        return getattr(self, role)

    def get_prime_role(self, role: ThemeDerivedRole):
        key = DERIVED_TO_PRIME_ROLE[role]
        return getattr(self, key)

    def get_derived_role(self, role: ThemePrimeRole) -> ThemeDerivedRole:
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
