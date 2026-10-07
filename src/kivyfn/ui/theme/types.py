"""Material 3 color roles and KivyFN component style types.

Success and warning are KivyFN semantic extensions to Material 3.
"""
from __future__ import annotations

from typing import Literal, TypeAlias, get_args

# =================================== #
# section: Color roles
# =================================== #
ThemeMode: TypeAlias = Literal["dark", "light"]

ThemePrimeRole: TypeAlias = Literal[
    "primary",
    "primaryContainer",
    "secondary",
    "secondaryContainer",
    "tertiary",
    "tertiaryContainer",
    "error",
    "errorContainer",
    "success",
    "successContainer",
    "warning",
    "warningContainer",
    "primaryFixed",
    "primaryFixedDim",
    "secondaryFixed",
    "secondaryFixedDim",
    "tertiaryFixed",
    "tertiaryFixedDim",
    "surface",
    "surfaceDim",
    "surfaceBright",
    "surfaceContainerLowest",
    "surfaceContainerLow",
    "surfaceContainer",
    "surfaceContainerHigh",
    "surfaceContainerHighest",
    "inverseSurface",
]


ThemeDerivedRole: TypeAlias = Literal[
    "onPrimary",
    "onPrimaryContainer",
    "onSecondary",
    "onSecondaryContainer",
    "onTertiary",
    "onTertiaryContainer",
    "onError",
    "onErrorContainer",
    "onSuccess",
    "onSuccessContainer",
    "onWarning",
    "onWarningContainer",
    "onPrimaryFixed",
    "onSecondaryFixed",
    "onTertiaryFixed",
    "onSurface",
    "onInverseSurface",
    "onSurfaceVariant",
    "onPrimaryFixedVariant",
    "onSecondaryFixedVariant",
    "onTertiaryFixedVariant",
]


ThemeUtilityRole: TypeAlias = Literal[
    "inversePrimary",
    "outline",
    "outlineVariant",
    "shadow",
    "scrim",
    "surfaceTint",
]


ThemeRole: TypeAlias = ThemePrimeRole | ThemeDerivedRole | ThemeUtilityRole
THEME_PRIME_ROLE = get_args(ThemePrimeRole)
THEME_DERIVED_ROLE = get_args(ThemeDerivedRole)
THEME_UTILITY_ROLE = get_args(ThemeUtilityRole)
THEME_ROLE = THEME_PRIME_ROLE + THEME_DERIVED_ROLE + THEME_UTILITY_ROLE
THEME_SURFACE_ROLE = (
    "surface",
    "surfaceDim",
    "surfaceBright",
    "surfaceContainerLowest",
    "surfaceContainerLow",
    "surfaceContainer",
    "surfaceContainerHigh",
    "surfaceContainerHighest",
)


# ======================================== #
# THEME TYPOGRAPHY ROLES
# ======================================== #
ThemeTypographyRole = Literal[
    "display",
    "headline",
    "title",
    "subtitle",
    "body",
    "caption",
    "button",
    "label"
]

THEME_TYPOGRAPHY_ROLE = (
    "display",
    "headline",
    "title",
    "subtitle",
    "body",
    "caption",
    "button",
    "label"
)

# ======================================== #
# THEME BUTTON STYLE ROLES
# ======================================== #
ThemeButtonStyleRole = Literal [
    "text",
    "filled",
    "elevated",
    "outlined"
]

THEME_BUTTON_STYLE_ROLE = (
    "text",
    "filled",
    "elevated",
    "outlined"
)

# ======================================== #
# THEME FIELD STYLE ROLES
# ======================================== #
ThemeFieldStyleRole = Literal [
    "text",
    "filled",
    "elevated",
    "outlined"
]

THEME_FIELD_STYLE_ROLE = (
    "text",
    "filled",
    "elevated",
    "outlined"
)

# ======================================== #
# THEME BUTTON STYLE ROLES
# ======================================== #
ThemeCardStyleRole = Literal [
    "none",
    "filled",
    "elevated",
    "outlined"
]

THEME_CARD_STYLE_ROLE = (
    "none",
    "filled",
    "elevated",
    "outlined"
)

# ======================================== #
# THEME SIZE ROLES
# ======================================== #
ThemeSizeRole = Literal [
    "small",
    "medium",
    "large"
]

THEME_SIZE_ROLE = (
    "small",
    "medium",
    "large"
)
