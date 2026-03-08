# kivyfn/bootstrap.py

from __future__ import annotations

_bootstrapped = False


def bootstrap() -> None:
    global _bootstrapped

    if _bootstrapped:
        return

    _bootstrapped = True

    # Register core widgets
    from .uibase.factory import register  # pyright: ignore

    register()
