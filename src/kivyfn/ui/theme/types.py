# kiyvfn.ui.theme.types.py
from __future__ import annotations
from typing import Literal, TypeAlias

# ======================================== #
# THEME ROLES
# ======================================== #
ThemePrimeRole: TypeAlias = Literal[
    "primary",
    "secondary",
    "surface",
    "background",
    "error",
    "warning",
    "success",
]


ThemeDerivedRole: TypeAlias = Literal[
    "onPrimary",
    "onSecondary",
    "onSurface",
    "onBackground",
    "onError",
    "onWarning",
    "onSuccess",
]


ThemeUtilityRole: TypeAlias = Literal[
    "surfaceRaised",
    "surfaceHover",
    "surfaceActive",
    "textSecondary",
    "textMuted",
    "textDisabled",
    "outline",
    "outlineStrong",
    "divider",
    "disabled",
    "shadow",
    "focus",
    "selection",
]


ThemeRole: TypeAlias = (
    ThemePrimeRole
    | ThemeDerivedRole
    | ThemeUtilityRole
)

THEME_PRIME_ROLE = (
    "primary",
    "secondary",
    "surface",
    "background",
    "error",
    "warning",
    "success",
)

THEME_DERIVED_ROLE = (
    "onPrimary",
    "onSecondary",
    "onSurface",
    "onBackground",
    "onError",
    "onWarning",
    "onSuccess",
)

THEME_UTILITY_ROLE = (
    "surfaceRaised",
    "surfaceHover",
    "surfaceActive",
    "textSecondary",
    "textMuted",
    "textDisabled",
    "outline",
    "outlineStrong",
    "divider",
    "disabled",
    "shadow",
    "focus",
    "selection",
)

THEME_ROLE = THEME_PRIME_ROLE + THEME_DERIVED_ROLE + THEME_UTILITY_ROLE



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
