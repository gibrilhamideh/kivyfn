"""
kivyfn.resources
================

Utilities for resolving file paths for both framework assets and
developer application assets.

The framework operates with two distinct resource origins:

1. Framework resources
   Files that ship with framework packages such as ``kivyfn``,
   ``kivyfn.ui`` or other extension modules.

2. Application resources
   Files that belong to the developer's application such as images,
   configuration files, or custom fonts.

These helpers provide a consistent way to access both locations
whether the application is running normally or bundled with
PyInstaller.

Examples
--------

Accessing a framework asset::

    from kivyfn.resources import framework_resource

    font_path = framework_resource(
        "kivyfn.ui",
        "resources",
        "fonts",
        "NotoSans-Regular.ttf"
    )


Accessing an application asset::

    from kivyfn.resources import app_resource

    logo_path = app_resource("resources", "images", "logo.png")
"""

from __future__ import annotations

import sys
from pathlib import Path
from importlib import resources


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------


def _runtime_root() -> Path | None:
    """
    Return the runtime extraction directory.

    When running inside a PyInstaller bundle, files are extracted to
    ``sys._MEIPASS``. Otherwise this returns ``None``.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # pyright: ignore
    return None


# ---------------------------------------------------------------------
# Framework resources
# ---------------------------------------------------------------------


def framework_resource(package: str, *parts: str) -> Path:
    """
    Resolve a path to a resource bundled with a framework package.

    Parameters
    ----------
    package:
        Python package containing the resource
        (e.g. ``"kivyfn.ui"`` or ``"kivyfn.threed"``).

    *parts:
        Path components relative to the package root.

    Returns
    -------
    Path
        Absolute path to the requested resource.

    Notes
    -----
    This works for:

    - normal development environments
    - installed packages
    - namespace packages
    - PyInstaller bundles
    """

    runtime = _runtime_root()

    if runtime:
        base = runtime / package.replace(".", "/")
        return base.joinpath(*parts)

    base = resources.files(package)
    return Path(base.joinpath(*parts))  # pyright: ignore
