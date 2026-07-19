# kivyfn/ui/feedback/snackbar/manager.py
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from kivyfn.ui.feedback.snackbar.snackbar import FnSnackbar
    from kivyfn.ui.root import FnRoot


class FnSnackbarManager:
    def __init__(self) -> None:
        self._root: FnRoot | None = None
        self._queue: deque[FnSnackbar] = deque()
        self._current: FnSnackbar | None = None

    # =================================== #
    # Root
    # =================================== #

    def attach(
        self,
        root: FnRoot,
    ) -> None:
        if self._root is root:
            return

        if self._root is not None and self._current is not None:
            raise RuntimeError(
                "Cannot attach FnSnackbarManager to a different root "
                "while a snackbar is open"
            )

        self._root = root
        self._open_next()

    def detach(self) -> None:
        if self._current is not None:
            raise RuntimeError(
                "Cannot detach FnSnackbarManager while a snackbar is open"
            )

        self._root = None

    # =================================== #
    # Queue
    # =================================== #

    def queue(
        self,
        snackbar: FnSnackbar,
    ) -> None:
        if snackbar is self._current:
            return

        if snackbar in self._queue:
            return

        self._queue.append(snackbar)
        self._open_next()

    def remove(
        self,
        snackbar: FnSnackbar,
    ) -> None:
        if snackbar is self._current:
            snackbar.dismiss()
            return

        try:
            self._queue.remove(snackbar)
        except ValueError:
            pass

    def clear(self) -> None:
        self._queue.clear()

        if self._current is not None:
            self._current.dismiss()

    # =================================== #
    # Lifecycle
    # =================================== #

    def _open_next(self) -> None:
        if self._current is not None:
            return

        if not self._queue:
            return

        root = self._root
        if root is None:
            return

        snackbar = self._queue[0]
        self._current = snackbar

        snackbar.bind(
            on_dismiss=self._on_dismiss,
        )

        root.add_overlay(snackbar)
        snackbar.open()

    def _on_dismiss(
        self,
        snackbar: FnSnackbar,
    ) -> None:
        root = self._root

        if root is None:
            raise RuntimeError(
                "Cannot dismiss snackbar because "
                "FnSnackbarManager is not attached to an FnRoot"
            )

        snackbar.unbind(
            on_dismiss=self._on_dismiss,
        )

        root.remove_overlay(snackbar)

        if self._queue and self._queue[0] is snackbar:
            self._queue.popleft()
        else:
            try:
                self._queue.remove(snackbar)
            except ValueError:
                pass

        if self._current is snackbar:
            self._current = None

        self._open_next()

    # =================================== #
    # Queries
    # =================================== #

    @property
    def current(self) -> FnSnackbar | None:
        return self._current

    @property
    def pending(self) -> tuple[FnSnackbar, ...]:
        return tuple(self._queue)

