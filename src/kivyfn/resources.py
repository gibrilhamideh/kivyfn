"""
kivyfn.resources
================

Utilities for resolving file paths for both framework assets and
developer application assets.

The framework operates with two distinct resource origins:

1. Framework resources
   Files that ship with the ``kivyfn`` package itself such as fonts,
   shaders, icons, kv templates, etc.

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

    font_path = framework_resource("resources", "fonts", "NotoSans-Regular.ttf")


Accessing an application asset::

    from kivyfn.resources import app_resource

    logo_path = app_resource("resources", "images", "logo.png")
"""

from __future__ import annotations

import sys
from pathlib import Path


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
# Public API
# ---------------------------------------------------------------------


def framework_resource(*parts: str) -> Path:
    """
    Resolve a path to a resource bundled with the ``kivyfn`` framework.

    Parameters
    ----------
    *parts:
        Path components relative to the framework package root.

    Returns
    -------
    Path
        Absolute path to the requested resource.

    Notes
    -----
    This works both in development environments and when the application
    is bundled with PyInstaller.
    """

    runtime = _runtime_root()

    if runtime:
        base = runtime / "kivyfn"
    else:
        base = Path(__file__).resolve().parent

    return base.joinpath(*parts)


def app_resource(*parts: str) -> Path:
    """
    Resolve a path to a resource belonging to the developer application.

    Parameters
    ----------
    *parts:
        Path components relative to the application's entry directory
        (where ``main.py`` resides).

    Returns
    -------
    Path
        Absolute path to the requested resource.

    Notes
    -----
    The application root is determined from the entry script location.
    This works both in normal execution and PyInstaller bundles.
    """

    runtime = _runtime_root()

    if runtime:
        base = runtime
    else:
        base = Path(sys.argv[0]).resolve().parent

    return base.joinpath(*parts)

