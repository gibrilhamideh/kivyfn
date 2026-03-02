from __future__ import annotations
import sys
from pathlib import Path


def framework_path() -> Path:
    """
    Path to kivyfn package (framework assets).
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    return framework_path().joinpath(*parts)


def project_root() -> Path:
    """
    Path to project root (where main.py is).
    """
    return Path(sys.argv[0]).resolve().parent


def app_path(*parts: str) -> Path:
    """
    Path to developer's app directory.
    """
    return project_root().joinpath("app", *parts)

