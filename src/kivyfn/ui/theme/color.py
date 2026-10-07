"""Reactive Material 3 colors and documented semantic extensions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypeAlias

from kivy.event import EventDispatcher
from kivy.properties import ColorProperty, OptionProperty
from kivy.utils import get_color_from_hex

from kivyfn.ui.theme.palettes import DARK_COLORS, LIGHT_COLORS
from kivyfn.ui.theme.types import (
    THEME_ROLE,
    THEME_SURFACE_ROLE,
    ThemeDerivedRole,
    ThemeMode,
    ThemePrimeRole,
    ThemeRole,
)
from kivyfn.ui.theme.utils import alpha as _alpha
from kivyfn.ui.theme.utils import blend, normalize_color, overlay
from kivyfn.ui.theme.utils import tone as _tone

ColorValue: TypeAlias = str | Sequence[float]

PRIME_TO_DERIVED_ROLE: dict[ThemePrimeRole, ThemeDerivedRole] = {
    "primary": "onPrimary",
    "primaryContainer": "onPrimaryContainer",
    "secondary": "onSecondary",
    "secondaryContainer": "onSecondaryContainer",
    "tertiary": "onTertiary",
    "tertiaryContainer": "onTertiaryContainer",
    "error": "onError",
    "errorContainer": "onErrorContainer",
    "success": "onSuccess",
    "successContainer": "onSuccessContainer",
    "warning": "onWarning",
    "warningContainer": "onWarningContainer",
    "primaryFixed": "onPrimaryFixed",
    "primaryFixedDim": "onPrimaryFixed",
    "secondaryFixed": "onSecondaryFixed",
    "secondaryFixedDim": "onSecondaryFixed",
    "tertiaryFixed": "onTertiaryFixed",
    "tertiaryFixedDim": "onTertiaryFixed",
    "surface": "onSurface",
    "surfaceDim": "onSurface",
    "surfaceBright": "onSurface",
    "surfaceContainerLowest": "onSurface",
    "surfaceContainerLow": "onSurface",
    "surfaceContainer": "onSurface",
    "surfaceContainerHigh": "onSurface",
    "surfaceContainerHighest": "onSurface",
    "inverseSurface": "onInverseSurface",
}


DERIVED_TO_PRIME_ROLE: dict[ThemeDerivedRole, ThemePrimeRole] = {
    "onPrimary": "primary",
    "onPrimaryContainer": "primaryContainer",
    "onSecondary": "secondary",
    "onSecondaryContainer": "secondaryContainer",
    "onTertiary": "tertiary",
    "onTertiaryContainer": "tertiaryContainer",
    "onError": "error",
    "onErrorContainer": "errorContainer",
    "onSuccess": "success",
    "onSuccessContainer": "successContainer",
    "onWarning": "warning",
    "onWarningContainer": "warningContainer",
    "onPrimaryFixed": "primaryFixed",
    "onSecondaryFixed": "secondaryFixed",
    "onTertiaryFixed": "tertiaryFixed",
    "onSurface": "surface",
    "onInverseSurface": "inverseSurface",
    "onSurfaceVariant": "surface",
    "onPrimaryFixedVariant": "primaryFixed",
    "onSecondaryFixedVariant": "secondaryFixed",
    "onTertiaryFixedVariant": "tertiaryFixed",
}


class ThemeColor(EventDispatcher):
    """Color roles shared by light and dark application palettes.

    ``success`` and ``warning`` families are KivyFN extensions. Interaction
    states are defined separately in ``ThemeState``. No legacy aliases exist.
    ``on_changed`` fires once per palette application or individual edit.
    """

    __events__ = ("on_changed",)
    mode: ThemeMode = OptionProperty("dark", options=("dark", "light"))

    primary = ColorProperty(DARK_COLORS["primary"])
    primaryContainer = ColorProperty(DARK_COLORS["primaryContainer"])
    secondary = ColorProperty(DARK_COLORS["secondary"])
    secondaryContainer = ColorProperty(DARK_COLORS["secondaryContainer"])
    tertiary = ColorProperty(DARK_COLORS["tertiary"])
    tertiaryContainer = ColorProperty(DARK_COLORS["tertiaryContainer"])
    error = ColorProperty(DARK_COLORS["error"])
    errorContainer = ColorProperty(DARK_COLORS["errorContainer"])
    success = ColorProperty(DARK_COLORS["success"])
    successContainer = ColorProperty(DARK_COLORS["successContainer"])
    warning = ColorProperty(DARK_COLORS["warning"])
    warningContainer = ColorProperty(DARK_COLORS["warningContainer"])
    primaryFixed = ColorProperty(DARK_COLORS["primaryFixed"])
    primaryFixedDim = ColorProperty(DARK_COLORS["primaryFixedDim"])
    secondaryFixed = ColorProperty(DARK_COLORS["secondaryFixed"])
    secondaryFixedDim = ColorProperty(DARK_COLORS["secondaryFixedDim"])
    tertiaryFixed = ColorProperty(DARK_COLORS["tertiaryFixed"])
    tertiaryFixedDim = ColorProperty(DARK_COLORS["tertiaryFixedDim"])
    surface = ColorProperty(DARK_COLORS["surface"])
    surfaceDim = ColorProperty(DARK_COLORS["surfaceDim"])
    surfaceBright = ColorProperty(DARK_COLORS["surfaceBright"])
    surfaceContainerLowest = ColorProperty(
        DARK_COLORS["surfaceContainerLowest"]
    )
    surfaceContainerLow = ColorProperty(DARK_COLORS["surfaceContainerLow"])
    surfaceContainer = ColorProperty(DARK_COLORS["surfaceContainer"])
    surfaceContainerHigh = ColorProperty(DARK_COLORS["surfaceContainerHigh"])
    surfaceContainerHighest = ColorProperty(
        DARK_COLORS["surfaceContainerHighest"]
    )
    inverseSurface = ColorProperty(DARK_COLORS["inverseSurface"])
    inversePrimary = ColorProperty(DARK_COLORS["inversePrimary"])
    onPrimary = ColorProperty(DARK_COLORS["onPrimary"])
    onPrimaryContainer = ColorProperty(DARK_COLORS["onPrimaryContainer"])
    onSecondary = ColorProperty(DARK_COLORS["onSecondary"])
    onSecondaryContainer = ColorProperty(DARK_COLORS["onSecondaryContainer"])
    onTertiary = ColorProperty(DARK_COLORS["onTertiary"])
    onTertiaryContainer = ColorProperty(DARK_COLORS["onTertiaryContainer"])
    onError = ColorProperty(DARK_COLORS["onError"])
    onErrorContainer = ColorProperty(DARK_COLORS["onErrorContainer"])
    onSuccess = ColorProperty(DARK_COLORS["onSuccess"])
    onSuccessContainer = ColorProperty(DARK_COLORS["onSuccessContainer"])
    onWarning = ColorProperty(DARK_COLORS["onWarning"])
    onWarningContainer = ColorProperty(DARK_COLORS["onWarningContainer"])
    onPrimaryFixed = ColorProperty(DARK_COLORS["onPrimaryFixed"])
    onSecondaryFixed = ColorProperty(DARK_COLORS["onSecondaryFixed"])
    onTertiaryFixed = ColorProperty(DARK_COLORS["onTertiaryFixed"])
    onSurface = ColorProperty(DARK_COLORS["onSurface"])
    onInverseSurface = ColorProperty(DARK_COLORS["onInverseSurface"])
    onSurfaceVariant = ColorProperty(DARK_COLORS["onSurfaceVariant"])
    onPrimaryFixedVariant = ColorProperty(DARK_COLORS["onPrimaryFixedVariant"])
    onSecondaryFixedVariant = ColorProperty(
        DARK_COLORS["onSecondaryFixedVariant"]
    )
    onTertiaryFixedVariant = ColorProperty(
        DARK_COLORS["onTertiaryFixedVariant"]
    )
    outline = ColorProperty(DARK_COLORS["outline"])
    outlineVariant = ColorProperty(DARK_COLORS["outlineVariant"])
    shadow = ColorProperty(DARK_COLORS["shadow"])
    scrim = ColorProperty(DARK_COLORS["scrim"])
    surfaceTint = ColorProperty(DARK_COLORS["surfaceTint"])

    def __init__(
        self,
        *,
        mode: ThemeMode = "dark",
        light: Mapping[ThemeRole, ColorValue] | None = None,
        dark: Mapping[ThemeRole, ColorValue] | None = None,
        **kwargs: Any,
    ) -> None:
        self._applying = False
        self._palettes = {
            "dark": self._normalize(DARK_COLORS),
            "light": self._normalize(LIGHT_COLORS),
        }
        self._palettes["dark"].update(self._normalize(dark or {}))
        self._palettes["light"].update(self._normalize(light or {}))
        if mode not in self._palettes:
            raise ValueError(f"Unknown theme mode: {mode!r}")
        overrides = {
            role: kwargs.pop(role) for role in THEME_ROLE if role in kwargs
        }
        self._palettes[mode].update(self._normalize(overrides))
        super().__init__(mode=mode, **kwargs)
        self._apply_mode()
        self.bind(mode=self._apply_mode)
        for role in THEME_ROLE:
            self.bind(**{role: self._on_role_changed})

    @staticmethod
    def _normalize(
        colors: Mapping[ThemeRole, ColorValue],
    ) -> dict[ThemeRole, list[float]]:
        unknown = set(colors) - set(THEME_ROLE)
        if unknown:
            raise ValueError(f"Unknown theme color roles: {sorted(unknown)}")
        return {
            role: normalize_color(
                get_color_from_hex(value) if isinstance(value, str) else value
            )
            for role, value in colors.items()
        }

    def set_palette(
        self,
        mode: ThemeMode,
        colors: Mapping[ThemeRole, ColorValue],
    ) -> None:
        if mode not in self._palettes:
            raise ValueError(f"Unknown theme mode: {mode!r}")
        self._palettes[mode].update(self._normalize(colors))
        if mode == self.mode:
            self._apply_mode()

    def _apply_mode(self, *_args: Any) -> None:
        self._applying = True
        try:
            for role, value in self._palettes[self.mode].items():
                setattr(self, role, list(value))
        finally:
            self._applying = False
        self.dispatch("on_changed")

    def _on_role_changed(self, *_args: Any) -> None:
        if not self._applying:
            # Preserve manual adjustments when toggling back to this mode.
            self._palettes[self.mode] = {
                role: list(getattr(self, role)) for role in THEME_ROLE
            }
            self.dispatch("on_changed")

    def on_changed(self) -> None:
        pass

    def get_role(self, role: ThemeRole) -> list[float]:
        if role not in THEME_ROLE:
            raise ValueError(f"Unknown theme color role: {role!r}")
        return list(getattr(self, role))

    @staticmethod
    def is_surface(role: ThemeRole | None) -> bool:
        return role in THEME_SURFACE_ROLE or role == "inverseSurface"

    def get_prime_role(self, role: ThemeDerivedRole) -> list[float]:
        return self.get_role(DERIVED_TO_PRIME_ROLE[role])

    def get_derived_role(self, role: ThemePrimeRole) -> list[float]:
        return self.get_role(PRIME_TO_DERIVED_ROLE[role])

    def tone(self, role: ThemeRole, value: int) -> list[float]:
        return _tone(self.get_role(role), value)

    def alpha(self, role: ThemeRole, value: float) -> list[float]:
        return _alpha(self.get_role(role), value)

    def blend(
        self, role_a: ThemeRole, role_b: ThemeRole, amount: float
    ) -> list[float]:
        return blend(self.get_role(role_a), self.get_role(role_b), amount)

    def overlay(self, role: ThemeRole, overlay_role: ThemeRole) -> list[float]:
        return overlay(self.get_role(role), self.get_role(overlay_role))

    def with_tone(self, color, value: int) -> list[float]:
        return _tone(color, value)

    def with_alpha(self, color, value: float) -> list[float]:
        return _alpha(color, value)

    def with_blend(self, color_a, color_b, amount: float) -> list[float]:
        return blend(color_a, color_b, amount)

    def with_overlay(self, color, overlay_color) -> list[float]:
        return overlay(color, overlay_color)
