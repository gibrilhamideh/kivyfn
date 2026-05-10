from __future__ import annotations
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from kivyfn.runtime.state.shared import FnSharedState


T = TypeVar("T")


class FnSharedField(Generic[T]):
    def __init__(self, default: T) -> None:
        self.default = default
        self.name: str | None = None

    def __set_name__(
        self,
        owner: type[FnSharedState],
        name: str,
    ) -> None:
        self.name = name

        fields = getattr(owner, "__shared_fields__", None)

        if fields is None:
            fields = {}
            setattr(owner, "__shared_fields__", fields)

        fields[name] = self

    def __get__(
        self,
        instance: FnSharedState | None,
        _owner: type[FnSharedState],
    ) -> T | FnSharedField[T]:
        if instance is None:
            return self

        if self.name is None:
            raise RuntimeError("FnSharedField is missing name")

        return instance._values.get(self.name, self.default)

    def __set__(
        self,
        instance: FnSharedState,
        value: T,
    ) -> None:
        if self.name is None:
            raise RuntimeError("FnSharedField is missing name")

        instance._set(self.name, value)


