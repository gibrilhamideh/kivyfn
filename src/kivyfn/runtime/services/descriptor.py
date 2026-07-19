from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, overload

if TYPE_CHECKING:
    from kivyfn.app import FnApp


T = TypeVar("T")


class Service(Generic[T]):
    def __init__(
        self,
        attribute: str,
    ) -> None:
        self._attribute = attribute

    @overload
    def __get__(
        self,
        instance: None,
        owner: type[FnApp],
    ) -> T:
        ...

    @overload
    def __get__(
        self,
        instance: FnApp,
        owner: type[FnApp],
    ) -> T:
        ...

    def __get__(
        self,
        instance: FnApp | None,
        owner: type[FnApp],
    ) -> T:
        app = (
            owner.require_app()
            if instance is None
            else instance
        )

        value = getattr(
            app,
            self._attribute,
            None,
        )

        if value is None:
            raise RuntimeError(
                f"{owner.__name__} service "
                f"{self._attribute.removeprefix('_')!r} "
                "is not available in this runtime"
            )

        return value
