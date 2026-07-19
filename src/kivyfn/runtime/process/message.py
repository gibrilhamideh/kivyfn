# kivyfn/runtime/process/message.py
from __future__ import annotations

from dataclasses import dataclass, field

from kivyfn.runtime.process.types import ProcessPayload


@dataclass(frozen=True, slots=True)
class ProcessError:
    type: str
    message: str
    traceback: str

    def __post_init__(self) -> None:
        if not isinstance(self.type, str) or not self.type:
            raise ValueError(
                "Process error type must be a non-empty string"
            )

        if not isinstance(self.message, str) or not self.message:
            raise ValueError(
                "Process error message must be a non-empty string"
            )

        if not isinstance(self.traceback, str):
            raise TypeError(
                "Process error traceback must be a string"
            )


@dataclass(frozen=True, slots=True)
class ProcessReadyMessage:
    process: str
    payload: ProcessPayload = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_process_name(self.process)

        if not isinstance(self.payload, dict):
            raise TypeError(
                "Process ready payload must be a dictionary"
            )

        object.__setattr__(
            self,
            "payload",
            dict(self.payload),
        )


@dataclass(frozen=True, slots=True)
class ProcessFailedMessage:
    process: str
    error: ProcessError
    payload: ProcessPayload = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_process_name(self.process)

        if not isinstance(self.error, ProcessError):
            raise TypeError(
                "Process failed error must be a ProcessError"
            )

        if not isinstance(self.payload, dict):
            raise TypeError(
                "Process failed payload must be a dictionary"
            )

        object.__setattr__(
            self,
            "payload",
            dict(self.payload),
        )


def _validate_process_name(
    process: str,
) -> None:
    if not isinstance(process, str) or not process:
        raise ValueError(
            "Process message process must be a non-empty string"
        )
