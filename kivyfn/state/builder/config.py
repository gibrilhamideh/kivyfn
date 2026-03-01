from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from ..storage.file import FileStorage
    from ..builder.policy import BootPolicyMode


@dataclass(frozen=True)
class BootConfig:
    storage: FileStorage | None = None
    boot_policy: BootPolicyMode | None = None
