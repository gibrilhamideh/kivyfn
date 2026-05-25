"""
kivyfn.paths
=============

Utilities for resolving package-relative paths in a runtime-safe way.

These helpers work consistently across:

- development environments
- installed packages
- editable installs
- namespace packages
- PyInstaller bundles

The system treats both framework packages and application packages
the same way through Python's import system.

Examples
--------

Framework package paths::

    from kivyfn.paths import package_path

    font_path = package_path(
        "kivyfn.ui",
        "resources",
        "fonts",
        "NotoSans-Regular.ttf",
    )


Application package paths::

    from kivyfn.paths import package_path

    logo_path = package_path(
        "app",
        "resources",
        "images",
        "logo.png",
    )
"""

from __future__ import annotations

import sys

from pathlib import Path
from importlib import resources


# =====================================================================
# Runtime
# =====================================================================


def runtime_dir() -> Path | None:
    """
    Return the runtime extraction directory.

    When running inside a PyInstaller bundle, files are extracted to
    ``sys._MEIPASS``.

    Returns
    -------
    Path | None
        Extraction directory if running from a bundle,
        otherwise ``None``.
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # pyright: ignore

    return None


# =====================================================================
# Package paths
# =====================================================================


def package_path(
    package: str,
    *parts: str,
) -> Path:
    """
    Resolve a runtime-safe path inside a Python package.

    Parameters
    ----------
    package:
        Importable Python package name.

        Examples::

            "app"
            "kivyfn.ui"
            "kivyfn.three"

    *parts:
        Additional path components relative to the package root.

    Returns
    -------
    Path
        Absolute path to the requested location.

    Notes
    -----
    This works correctly for:

    - development environments
    - installed packages
    - editable installs
    - namespace packages
    - PyInstaller bundles
    """

    runtime = runtime_dir()

    if runtime:
        return runtime / package.replace(".", "/") / Path(*parts)

    base = resources.files(package)
    resource = base.joinpath(*parts)

    return Path(str(resource))
