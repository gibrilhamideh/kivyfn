from __future__ import annotations
from typing import Any, ClassVar

from .registry import SchemaRegistry
from .trigger import Trigger

from ..schema.fields import BaseField, ForeignKeyField
from ..core.registry import ForeignKeyRegistry
from ..errors import FieldNotFoundError


class Schema:
    many: ClassVar[bool] = False
    persistant: ClassVar[bool] = False

    __fields__: ClassVar[dict[str, BaseField]]
    __triggers__: ClassVar[list[Trigger]]
    __composite_uniques__: ClassVar[list[tuple[str, ...]]] = []

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        fields: dict[str, BaseField] = {}
        triggers: list[Trigger] = []

        for name, attr in cls.__dict__.items():
            if isinstance(attr, BaseField):
                attr.name = name

                # 🔒 Normalize constraints
                if getattr(attr, "unique", False):
                    attr.index = True

                if isinstance(attr, ForeignKeyField):
                    attr.index = True

                    ForeignKeyRegistry.register(
                        schema=cls.__name__,
                        field=name,
                        reference=attr.schema,
                        on_delete=attr.on_delete,
                    )

                fields[name] = attr

            if hasattr(attr, "_trigger_meta"):
                triggers.extend(attr._trigger_meta)

        cls.__fields__ = fields
        cls.__triggers__ = triggers

        SchemaRegistry.register(cls)  # ------------------------

    # Introspection API
    # ------------------------
    @classmethod
    def get_field(cls, name: str) -> BaseField:
        try:
            return cls.__fields__[name]
        except KeyError:
            raise FieldNotFoundError(f"Unknown field '{name}' in {cls.__name__}")

    @classmethod
    def fields(cls) -> dict[str, BaseField]:
        return cls.__fields__.copy()

    @classmethod
    def field_names(cls) -> set[str]:
        return set(cls.__fields__)

    @classmethod
    def indexed_fields(cls) -> tuple[str, ...]:
        return tuple(name for name, field in cls.__fields__.items() if field.index)

    @classmethod
    def unique_fields(cls) -> tuple[str, ...]:
        return tuple(name for name, field in cls.__fields__.items() if field.unique)

    @classmethod
    def foreign_key_fields(cls) -> tuple[str, ...]:
        return tuple(
            name
            for name, field in cls.__fields__.items()
            if isinstance(field, ForeignKeyField)
        )

    # ------------------------
    # Flags
    # ------------------------
    @classmethod
    def is_many(cls) -> bool:
        return cls.many

    @classmethod
    def defaults(cls) -> dict:
        data = {}
        for name, field in cls.fields().items():
            data[name] = getattr(field, "default", None)

        return data

    # ------------------------
    # Challenges
    # ------------------------
    @classmethod
    def challenge_field(cls, name: str, value: Any) -> Any:
        field = cls.get_field(name)
        return field.parse(value)

    @classmethod
    def challenge_fields(cls, data: dict) -> dict:
        casts = {}
        for name, value in data.items():
            casts[name] = cls.challenge_field(name, value)

        return casts
