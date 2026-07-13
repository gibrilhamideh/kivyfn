# kivyfn/ui/feedback/snackbar/manager.py

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from kivyfn.ui.feedback.snackbar.snackbar import FnSnackbar
    from kivyfn.ui.root import FnRoot


class FnSnackbarManager:
    _root: FnRoot | None = None
    _queue: deque[FnSnackbar] = deque()
    _current: FnSnackbar | None = None

    # =================================== #
    # Root
    # =================================== #

    @classmethod
    def attach(
        cls,
        root: FnRoot,
    ) -> None:
        if cls._root is root:
            return

        cls._root = root
        cls._open_next()

    # =================================== #
    # Queue
    # =================================== #

    @classmethod
    def queue(
        cls,
        snackbar: FnSnackbar,
    ) -> None:
        if snackbar is cls._current:
            return

        if snackbar in cls._queue:
            return

        cls._queue.append(snackbar)
        cls._open_next()

    @classmethod
    def remove(
        cls,
        snackbar: FnSnackbar,
    ) -> None:
        if snackbar is cls._current:
            snackbar.dismiss()
            return

        try:
            cls._queue.remove(snackbar)
        except ValueError:
            pass

    @classmethod
    def clear(cls) -> None:
        cls._queue.clear()

        if cls._current is not None:
            cls._current.dismiss()

    # =================================== #
    # Lifecycle
    # =================================== #

    @classmethod
    def _open_next(cls) -> None:
        if cls._current is not None:
            return

        if not cls._queue:
            return

        root = cls._root
        if root is None:
            return

        snackbar = cls._queue[0]
        cls._current = snackbar

        snackbar.bind(
            on_dismiss=cls._on_dismiss,
        )

        root.add_overlay(snackbar)
        snackbar.open()

    @classmethod
    def _on_dismiss(
        cls,
        snackbar: FnSnackbar,
    ) -> None:
        root = cls._root

        if root is None:
            raise RuntimeError(
                "Cannot dismiss snackbar because "
                "FnSnackbarManager is not attached to an FnRoot"
            )

        snackbar.unbind(
            on_dismiss=cls._on_dismiss,
        )

        root.remove_overlay(snackbar)

        if cls._queue and cls._queue[0] is snackbar:
            cls._queue.popleft()
        else:
            try:
                cls._queue.remove(snackbar)
            except ValueError:
                pass

        if cls._current is snackbar:
            cls._current = None

        cls._open_next()

    # =================================== #
    # Queries
    # =================================== #

    @classmethod
    def current(cls) -> FnSnackbar | None:
        return cls._current

    @classmethod
    def pending(cls) -> tuple[FnSnackbar, ...]:
        return tuple(cls._queue)

