# kivyfn/i18n/ref.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class I18nRef:
    key: str
    params: dict[str, Any] = field(default_factory=dict)
