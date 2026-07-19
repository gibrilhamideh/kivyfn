# kivyfn/bootstrap.py
from __future__ import annotations


_bootstrapped = False


def bootstrap() -> None:
    global _bootstrapped

    if not _bootstrapped:
        from kivyfn.factory import register

        register()
        _bootstrapped = True

    from kivyfn.ui.bootstrap import bootstrap as bootstrap_ui

    bootstrap_ui()
